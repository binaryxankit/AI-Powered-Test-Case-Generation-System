"use client";

import { useParams, useRouter } from "next/navigation";
import * as React from "react";
import { ArrowLeft, Download, History, Sparkles } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import {
  TestCaseCard,
  TestCaseCardSkeleton,
  TestCaseSummary,
} from "@/components/test-case-card";
import { api, ApiClientError } from "@/services/api";
import { formatDate, truncate } from "@/lib/utils";
import type { TestGeneration } from "@/lib/types";

export default function HistoryDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const id = Number.parseInt(params?.id ?? "", 10);

  const [data, setData] = React.useState<TestGeneration | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    let cancelled = false;

    async function load() {
      if (!Number.isFinite(id) || id <= 0) {
        setError("Invalid generation id.");
        setIsLoading(false);
        return;
      }
      try {
        const fresh = await api.getHistory(id);
        if (!cancelled) {
          setData(fresh);
          setIsLoading(false);
        }
      } catch (err) {
        if (cancelled) return;
        const message =
          err instanceof ApiClientError
            ? err.message
            : "Unable to load this generation.";
        setError(message);
        setIsLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [id]);

  if (isLoading) {
    return (
      <div className="container max-w-5xl py-10 md:py-14">
        <div className="mb-8 space-y-3">
          <div className="h-3 w-24 rounded bg-muted" />
          <div className="h-8 w-3/4 rounded bg-muted" />
          <div className="h-4 w-40 rounded bg-muted" />
        </div>
        <div className="grid gap-5">
          {Array.from({ length: 3 }).map((_, i) => (
            <TestCaseCardSkeleton key={i} />
          ))}
        </div>
        <div className="mt-8 flex items-center justify-center">
          <Spinner size="md" label="Loading generation..." />
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="container max-w-3xl py-20">
        <Alert variant="destructive">
          <AlertTitle>Could not load this generation</AlertTitle>
          <AlertDescription>
            {error ?? "It may have been removed."}
          </AlertDescription>
        </Alert>
        <div className="mt-6 flex flex-wrap gap-3">
          <Button onClick={() => router.push("/generate")}>
            <Sparkles className="h-4 w-4" />
            Generate new
          </Button>
          <Button
            variant="outline"
            onClick={() => router.push("/history")}
          >
            <History className="h-4 w-4" />
            Back to history
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container max-w-5xl py-10 md:py-14">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <Button variant="ghost" onClick={() => router.push("/history")}>
          <ArrowLeft className="h-4 w-4" />
          Back to history
        </Button>
        <div className="flex flex-wrap gap-2">
          <Button asChild variant="outline">
            <a
              href={api.pdfUrl(data.id)}
              target="_blank"
              rel="noopener noreferrer"
              download
            >
              <Download className="h-4 w-4" />
              Download Report
            </a>
          </Button>
          <Button asChild>
            <a href={`/results?id=${data.id}`}>View results</a>
          </Button>
        </div>
      </div>

      <header className="mb-10 space-y-3">
        <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-muted-foreground">
          <History className="h-3.5 w-3.5" />
          Saved generation #{data.id}
        </div>
        <h1 className="text-2xl font-bold tracking-tight md:text-3xl">
          {truncate(data.requirement, 240)}
        </h1>
        <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
          <TestCaseSummary count={data.test_cases.length} />
          <span aria-hidden>&middot;</span>
          <span>Generated {formatDate(data.created_at)}</span>
        </div>
      </header>

      <section className="grid gap-5">
        {data.test_cases.map((tc, index) => (
          <TestCaseCard key={tc.test_case_id} index={index} testCase={tc} />
        ))}
      </section>
    </div>
  );
}
