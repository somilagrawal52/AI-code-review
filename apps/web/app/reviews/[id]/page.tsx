"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { ArrowLeft, Github, Send } from "lucide-react";
import { AppShell, PageHeader } from "@/components/shell";
import { Button, ErrorState, Loading } from "@/components/ui";
import { ReviewView } from "@/components/review-view";
import { api } from "@/lib/api";
import type { Review } from "@/lib/types";
export default function ReviewDetail() { const { id }=useParams<{id:string}>(); const [review,setReview]=useState<Review|null>(null); const [error,setError]=useState(""); const [published,setPublished]=useState(""); useEffect(()=>{api.reviewDetail(id).then(setReview).catch(e=>setError(e.message));},[id]); const publish=async()=>{setPublished("Demo Mode: GitHub publishing is intentionally disabled.");}; return <AppShell><Link href="/reviews" className="mb-5 inline-flex items-center gap-1 text-sm text-muted hover:text-white"><ArrowLeft className="h-4 w-4"/>Review history</Link>{error?<ErrorState message={error}/>:!review?<Loading label="Loading review"/>:<><PageHeader eyebrow="acme/storefront · Pull request #142" title="Improve checkout validation"><Button onClick={publish}><Send className="h-4 w-4"/>Publish to GitHub</Button></PageHeader>{published && <p className="mb-5 rounded-lg border border-sage/20 bg-sage/10 p-3 text-sm text-sage">{published}</p>}<ReviewView review={review}/></>}</AppShell> }
