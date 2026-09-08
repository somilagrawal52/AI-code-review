import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = { title: "CodeSage AI", description: "AI code reviews for GitHub pull requests" };
export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }
