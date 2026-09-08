"""Small, swappable specialist definitions for the review orchestrator.

The prompts intentionally constrain agents to the prepared diff, so no specialist is
given a cloned repository or asked to infer code not present in the review context.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Specialist:
    name: str
    instruction: str


SECURITY_AGENT = Specialist(
    "security",
    "Find evidence-grounded security issues: injection, authorization, authentication, secrets, data exposure, SSRF, path traversal, unsafe crypto, or validation. Calibrate confidence and do not overstate risks.",
)
BUG_AGENT = Specialist(
    "bug", "Find concrete correctness, async, error-handling, type, state, and edge-case defects."
)
PERFORMANCE_AGENT = Specialist(
    "performance",
    "Find plausible performance issues grounded in the diff: N+1 work, unbounded operations, blocking I/O, wasteful rerenders, or expensive algorithms.",
)
MAINTAINABILITY_AGENT = Specialist(
    "maintainability",
    "Find material design debt: poor separation, brittle complexity, error handling gaps, hard-coded policy, or typing problems. Avoid style trivia.",
)
TESTING_AGENT = Specialist(
    "testing",
    "Identify missing tests for changed behavior, boundaries, failures, and regressions. Infer the test framework only from evidence in the diff.",
)

SPECIALISTS = (SECURITY_AGENT, BUG_AGENT, PERFORMANCE_AGENT, MAINTAINABILITY_AGENT, TESTING_AGENT)
