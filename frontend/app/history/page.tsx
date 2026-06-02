"use client";

import Link from "next/link";
import * as React from "react";
import { Download, FileText, History, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { EmptyState } from "@/components/empty-state";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { api, ApiClientError } from "@/services/api";
import { formatDate, truncate } from "@/lib/utils";
import type { TestGenerationSummary } from "@/lib/types";

export default function HistoryPage() {
  const [items, setItems] = React.useState<TestGenerationSummary[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const list = await api.listHistory();
        if (!cancelled) {
          setItems(list);
          setIsLoading(false);
        }
      } catch (err) {
        if (cancelled) return;
        const message =
          err instanceof ApiClientError
            ? err.message
            : "Could not load history.";
        setError(message);
        setIsLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="container max-w-5xl py-10 md:py-14">
      <div className="mb-8 flex flex-wrap items-end justify-between gap-3">
        <div>
          <span className="inline-flex items-center gap-2 rounded-full border border-border/60 bg-card/60 px-3 py-1 text-xs font-medium text-muted-foreground">
            <History className="h-3.5 w-3.5 text-primary" />
            History
          </span>
          <h1 className="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
            Past generations
          </h1>
          <p className="mt-2 text-muted-foreground">
            Re-open any previous run to review or re-download its report.
          </p>
        </div>
        <Button asChild>
          <Link href="/generate">
            <Sparkles className="h-4 w-4" />
            New generation
          </Link>
        </Button>
      </div>

      {isLoading ? (
        <HistorySkeleton />
      ) : error ? (
        <Alert variant="destructive">
          <AlertTitle>Could not load history</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      ) : items.length === 0 ? (
        <EmptyState
          variant="empty"
          title="No generations yet"
          description="Once you generate test cases, they will appear here for easy re-access."
          actionLabel="Generate your first test cases"
          actionHref="/generate"
        />
      ) : (
        <ul className="space-y-3">
          {items.map((item, index) => (
            <li
              key={item.id}
              className="animate-fade-in"
              style={{ animationDelay: `${index * 30}ms` }}
            >
              <HistoryRow item={item} />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function HistoryRow({ item }: { item: TestGenerationSummary }) {
  return (
    <Card className="border-border/60 bg-card/70 transition-colors hover:border-primary/40">
      <CardContent className="flex flex-col gap-4 p-5 md:flex-row md:items-center md:justify-between">
        <div className="min-w-0 flex-1 space-y-1.5">
          <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-muted-foreground">
            <FileText className="h-3.5 w-3.5" />
            Requirement #{item.id}
            <span aria-hidden>&middot;</span>
            <span className="text-priority-medium">
              {item.test_case_count} {item.test_case_count === 1 ? "case" : "cases"}
            </span>
          </div>
          <p className="line-clamp-2 text-sm font-medium leading-snug md:text-base">
            {truncate(item.requirement, 200)}
          </p>
          <p className="text-xs text-muted-foreground">
            {formatDate(item.created_at)}
          </p>
        </div>
        <div className="flex flex-wrap gap-2 md:shrink-0">
          <Button variant="outline" size="sm" asChild>
            <a
              href={api.pdfUrl(item.id)}
              target="_blank"
              rel="noopener noreferrer"
              download
            >
              <Download className="h-3.5 w-3.5" />
              PDF
            </a>
          </Button>
          <Button size="sm" asChild>
            <Link href={`/history/${item.id}`}>View</Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

function HistorySkeleton() {
  return (
    <div className="flex flex-col items-center gap-3 py-20">
      <Spinner size="md" label="Loading history..." />
    </div>
  );
}
