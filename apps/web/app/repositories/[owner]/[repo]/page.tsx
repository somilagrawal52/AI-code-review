"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { GitPullRequest, Star } from "lucide-react";
import { useEffect, useState } from "react";

import { AppShell, PageHeader } from "@/components/shell";
import { EmptyState, ErrorState, Loading } from "@/components/ui";
import { api } from "@/lib/api";
import type { Pull, Repository } from "@/lib/types";

export default function RepositoryPage() {
  const { owner, repo } = useParams<{ owner: string; repo: string }>();
  const [repository, setRepository] = useState<Repository | null>(null);
  const [pulls, setPulls] = useState<Pull[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.repository(owner, repo), api.pulls(owner, repo)])
      .then(([currentRepository, currentPulls]) => {
        setRepository(currentRepository);
        setPulls(currentPulls.items);
      })
      .catch((requestError: Error) => setError(requestError.message));
  }, [owner, repo]);

  if (error) return <AppShell><ErrorState message={error} /></AppShell>;
  if (!repository) return <AppShell><Loading label="Loading repository" /></AppShell>;

  const stats = [
    ["Language", repository.language],
    ["Branch", repository.default_branch],
    ["Stars", <span key="stars" className="flex items-center gap-1"><Star className="h-3 w-3" />{repository.stars}</span>],
    ["Open PRs", repository.open_pull_count],
  ];

  return <AppShell>
    <PageHeader eyebrow="Repository" title={`${repository.owner}/${repository.name}`}>
      <span className="rounded-full border border-line px-3 py-1.5 text-xs text-muted">{repository.private ? "Private" : "Public"}</span>
    </PageHeader>
    <p className="-mt-5 mb-7 max-w-2xl text-sm text-muted">{repository.description}</p>
    <div className="mb-7 grid grid-cols-2 gap-3 sm:grid-cols-4">
      {stats.map(([label, value]) => <div className="panel p-4" key={String(label)}><p className="text-xs text-muted">{label}</p><p className="mt-2 text-sm font-semibold">{value}</p></div>)}
    </div>
    <div className="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
      <section className="panel overflow-hidden">
        <div className="border-b border-line p-5"><p className="font-semibold">Pull requests</p><p className="mt-1 text-xs text-muted">Run a diff-first AI review on an open PR.</p></div>
        {pulls.length ? pulls.map((pull) => <Link key={pull.id} href={`/repositories/${owner}/${repo}/pull/${pull.number}`} className="flex items-center justify-between border-b border-line p-5 last:border-0 hover:bg-white/[.02]"><div><p className="font-medium">#{pull.number} {pull.title}</p><p className="mt-1 text-xs text-muted">{pull.author} · {pull.head_branch} → {pull.base_branch}</p></div><GitPullRequest className="h-5 w-5 text-sage" /></Link>) : <EmptyState title="No open pull requests" body="Open a pull request on GitHub to start an AI review." />}
      </section>
      <section className="panel p-5"><p className="font-semibold">Repository health</p><p className="mt-2 text-sm leading-6 text-muted">No completed review metrics exist for this repository yet. Run a review to see security, reliability, performance, maintainability, and testing signals.</p><div className="mt-5 rounded-lg border border-dashed border-line p-4 text-sm text-muted">Metrics appear only after a completed analysis.</div></section>
    </div>
  </AppShell>;
}
