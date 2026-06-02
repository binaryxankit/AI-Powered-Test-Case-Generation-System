"use client";

import { useRouter, useSearchParams } from "next/navigation";
import * as React from "react";
import {
  ArrowLeft,
  ClipboardCopy,
  Download,
  FileText,
  History,
  RefreshCw,
  Sparkles,
} from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { CopyButton } from "@/components/copy-button";
import { Spinner } from "@/components/ui/spinner";
import {
  TestCaseCard,
  TestCaseCardSkeleton,
  TestCaseSummary,
} from "@/components/test-case-card";
import { api, ApiClientError } from "@/services/api";
import { formatDate, truncate } from "@/lib/utils";
import { formatAllTestCasesAsMarkdown } from "@/lib/format";
import type { TestGeneration } from "@/lib/types";

export default function ResultsPage() {
  return (
    <React.Suspense fallback={<ResultsSkeleton />}>
      <ResultsView />
    </React.Suspense>
  );
}

function ResultsView() {
  const params = useSearchParams();
  const router = useRouter();
  const idParam = params.get("id");
  const id = idParam ? Number.parseInt(idParam, 10) : NaN;

  const [data, setData] = React.useState<TestGeneration | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    let cancelled = false;

    async function load() {
      if (!Number.isFinite(id) || id <= 0) {
        setError("Missing or invalid generation id.");
        setIsLoading(false);
        return;
      }

      const cached =
        typeof window !== "undefined"
          ? sessionStorage.getItem(`generation:${id}`)
          : null;
      if (cached) {
        try {
          const parsed = JSON.parse(cached) as TestGeneration;
          if (!cancelled) {
            setData(parsed);
            setIsLoading(false);
          }
          return;
        } catch {
          // fall through to network fetch
        }
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
    return <ResultsSkeleton />;
  }

  if (error || !data) {
    return (
      <div className="container max-w-3xl py-20">
        <Alert variant="destructive">
          <AlertTitle>Could not load results</AlertTitle>
          <AlertDescription>
            {error ?? "This generation could not be found."}
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
            View history
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container max-w-5xl py-10 md:py-14">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <Button variant="ghost" onClick={() => router.push("/generate")}>
          <ArrowLeft className="h-4 w-4" />
          New generation
        </Button>
        <div className="flex flex-wrap gap-2">
          <CopyButton
            value={formatAllTestCasesAsMarkdown(data)}
            label="Copy as Markdown"
            variant="outline"
          />
          <Button
            variant="outline"
            onClick={() => router.push(`/history/${data.id}`)}
          >
            <RefreshCw className="h-4 w-4" />
            Reopen via history
          </Button>
          <Button asChild variant="gradient">
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
        </div>
      </div>

      <header className="mb-10 space-y-3">
        <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-muted-foreground">
          <FileText className="h-3.5 w-3.5" />
          Requirement
        </div>
        <h1 className="text-2xl font-bold tracking-tight md:text-3xl">
          {truncate(data.requirement, 240)}
        </h1>
        <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
          <TestCaseSummary count={data.test_cases.length} />
          <span aria-hidden>&middot;</span>
          <span>Generated {formatDate(data.created_at)}</span>
          <span aria-hidden>&middot;</span>
          <span>ID #{data.id}</span>
        </div>
      </header>

      <section className="grid gap-5">
        {data.test_cases.map((tc, index) => (
          <TestCaseCard key={tc.test_case_id} index={index} testCase={tc} />
        ))}
      </section>

      <div className="mt-12 flex flex-wrap items-center justify-center gap-3 rounded-2xl border border-dashed border-border/70 bg-card/40 p-8 text-center">
        <div>
          <h3 className="text-base font-semibold">
            Need more from this requirement?
          </h3>
          <p className="text-sm text-muted-foreground">
            Refine the prompt or try a different angle.
          </p>
        </div>
        <Button asChild>
          <a href="/generate">Generate again</a>
        </Button>
      </div>
    </div>
  );
}

function ResultsSkeleton() {
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
        <Spinner size="md" label="Loading results..." />
      </div>
    </div>
  );
}
