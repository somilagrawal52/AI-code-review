import type { Config } from "tailwindcss";
export default { content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"], theme: { extend: { colors: { ink: "#09090b", panel: "#111113", line: "#28282d", sage: "#94f7b1", muted: "#9898a4" }, boxShadow: { panel: "0 10px 40px rgba(0,0,0,.22)" } } }, plugins: [] } satisfies Config;
