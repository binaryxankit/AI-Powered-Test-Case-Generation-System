import Link from "next/link";

import { Sparkles } from "lucide-react";

export function SiteFooter() {
  return (
    <footer className="border-t border-border/40 bg-background/60">
      <div className="container flex flex-col items-center justify-between gap-3 py-6 text-sm text-muted-foreground md:flex-row">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-primary" />
          <span>
            Built with Next.js, FastAPI, PostgreSQL &amp; Google Gemini.
          </span>
        </div>
        <div className="flex items-center gap-4">
          <Link
            href="/generate"
            className="hover:text-foreground transition-colors"
          >
            Generator
          </Link>
          <Link
            href="/history"
            className="hover:text-foreground transition-colors"
          >
            History
          </Link>
        </div>
      </div>
    </footer>
  );
}
