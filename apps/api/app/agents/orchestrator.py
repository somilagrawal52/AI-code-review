import asyncio
from collections import defaultdict

from openai import AsyncOpenAI

from app.agents.specialists import SPECIALISTS
from app.core.config import get_settings
from app.schemas.review import ReviewIssueOutput, ReviewResult, SpecialistOutput
from app.services.scoring import calculate_scores

BASE_PROMPT = """You are a CodeSage specialist. Analyze only the supplied PR diff. Do not invent files or code. Findings require filename and best available line. Avoid duplicates, generic advice, and weak claims. Return Pydantic-conforming JSON only."""


class ReviewOrchestrator:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def _specialist(
        self, name: str, instruction: str, context: str
    ) -> list[ReviewIssueOutput]:
        client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        response = await client.beta.chat.completions.parse(
            model=self.settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": f"{BASE_PROMPT}\nYour role: {instruction}\nSet agent to '{name}'.",
                },
                {"role": "user", "content": context},
            ],
            response_format=SpecialistOutput,
            temperature=0.1,
        )
        parsed = response.choices[0].message.parsed
        return parsed.findings if parsed else []

    @staticmethod
    def _dedupe(items: list[ReviewIssueOutput]) -> list[ReviewIssueOutput]:
        seen: set[tuple[str, int | None, str]] = set()
        output: list[ReviewIssueOutput] = []
        for item in sorted(items, key=lambda i: (i.severity.value, -i.confidence)):
            key = (item.file_path, item.start_line, item.title.lower()[:45])
            if key not in seen:
                seen.add(key)
                output.append(item)
        return output

    async def review(self, context: str) -> ReviewResult:
        if not self.settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required outside Demo Mode")
        result_sets = await asyncio.gather(
            *(self._specialist(agent.name, agent.instruction, context) for agent in SPECIALISTS)
        )
        issues = self._dedupe([issue for result in result_sets for issue in result])
        overall, scores = calculate_scores(issues)
        grouped: dict[str, int] = defaultdict(int)
        for issue in issues:
            grouped[issue.severity.value] += 1
        summary = (
            f"Review completed with score {overall}/100: "
            + ", ".join(f"{count} {severity}" for severity, count in grouped.items())
            if issues
            else "No material issues were identified in the reviewed diff."
        )
        return ReviewResult(
            summary=summary, issues=issues, positive_findings=[], recommended_actions=[]
        )
