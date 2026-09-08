import type { Pull, Repository, Review } from "./types";
const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
async function request<T>(path: string, options?: RequestInit): Promise<T> { const res = await fetch(`${BASE}${path}`, { ...options, credentials: "include", headers: { "Content-Type": "application/json", ...options?.headers }, cache: "no-store" }); if (!res.ok) throw new Error((await res.json().catch(() => null))?.detail || "Request failed"); return res.json(); }
export const api = {
  dashboard: () => request<{ metrics: Record<string, number>; reviews_over_time: { date: string; reviews: number }[]; recent_reviews: Review[]; findings: Record<string, number> }>("/api/dashboard"),
  repositories: (query = "") => request<{ items: Repository[] }>(`/api/repositories${query ? `?query=${encodeURIComponent(query)}` : ""}`),
  repository: (owner: string, repo: string) => request<Repository>(`/api/repositories/${owner}/${repo}`),
  pulls: (owner: string, repo: string) => request<{ items: Pull[] }>(`/api/repositories/${owner}/${repo}/pulls`),
  pull: (owner: string, repo: string, number: string) => request<Pull & { repository: Repository }>(`/api/repositories/${owner}/${repo}/pulls/${number}`),
  review: (owner: string, repo: string, number: string) => request<Review>(`/api/repositories/${owner}/${repo}/pulls/${number}/review`, { method: "POST" }),
  reviews: () => request<{ items: Review[] }>("/api/reviews"),
  reviewDetail: (id: string) => request<Review>(`/api/reviews/${id}`),
  fix: (review: string, issue: string) => request<{ content: string }>(`/api/reviews/${review}/issues/${issue}/fix`, { method: "POST", body: "{}" }),
  test: (review: string, issue: string) => request<{ content: string }>(`/api/reviews/${review}/issues/${issue}/test`, { method: "POST", body: "{}" }),
  chat: (review: string, message: string) => request<{ answer: string }>(`/api/reviews/${review}/chat`, { method: "POST", body: JSON.stringify({ message }) })
};
