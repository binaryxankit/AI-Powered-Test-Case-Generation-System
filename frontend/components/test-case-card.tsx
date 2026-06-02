import { AlertTriangle, CheckCircle2, FileText, ListOrdered, ShieldAlert } from "lucide-react";
import * as React from "react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { CopyButton } from "@/components/copy-button";
import { Separator } from "@/components/ui/separator";
import type { Priority, TestCase } from "@/lib/types";
import { cn } from "@/lib/utils";

interface TestCaseCardProps {
  index: number;
  testCase: TestCase;
  className?: string;
}

const PRIORITY_VARIANT: Record<Priority, "low" | "medium" | "high" | "critical"> = {
  Low: "low",
  Medium: "medium",
  High: "high",
  Critical: "critical",
};

const PRIORITY_DOT: Record<Priority, string> = {
  Low: "bg-priority-low",
  Medium: "bg-priority-medium",
  High: "bg-priority-high",
  Critical: "bg-priority-critical",
};

export function TestCaseCard({ index, testCase, className }: TestCaseCardProps) {
  const copyValue = React.useMemo(
    () => formatTestCaseAsText(testCase),
    [testCase],
  );

  return (
    <Card
      className={cn(
        "group relative overflow-hidden border-border/70 bg-card/80 backdrop-blur transition-all",
        "hover:border-primary/40 hover:shadow-xl hover:shadow-primary/5 animate-fade-in",
        className,
      )}
      style={{ animationDelay: `${index * 60}ms` }}
    >
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-primary/50 to-transparent" />

      <CardContent className="space-y-5 p-6">
        <header className="flex flex-wrap items-start justify-between gap-3">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">
              <span
                className={cn(
                  "h-1.5 w-1.5 rounded-full",
                  PRIORITY_DOT[testCase.priority],
                )}
                aria-hidden
              />
              {testCase.test_case_id}
            </div>
            <h3 className="text-lg font-semibold leading-snug tracking-tight">
              {testCase.title}
            </h3>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant={PRIORITY_VARIANT[testCase.priority]}>
              {testCase.priority}
            </Badge>
            <CopyButton
              value={copyValue}
              label="Copy"
              aria-label="Copy test case to clipboard"
            />
          </div>
        </header>

        <Separator />

        <Section
          icon={<ListOrdered className="h-4 w-4" />}
          label="Test Steps"
        >
          <ol className="space-y-2 text-sm">
            {testCase.steps.map((step, i) => (
              <li key={i} className="flex gap-3">
                <span className="mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-full bg-primary/10 text-[11px] font-semibold text-primary">
                  {i + 1}
                </span>
                <span className="leading-relaxed text-foreground/90">{step}</span>
              </li>
            ))}
          </ol>
        </Section>

        <Section
          icon={<CheckCircle2 className="h-4 w-4 text-emerald-500" />}
          label="Expected Result"
        >
          <p className="rounded-lg border border-emerald-500/20 bg-emerald-500/5 px-3 py-2 text-sm leading-relaxed text-foreground/90">
            {testCase.expected_result}
          </p>
        </Section>

        {testCase.edge_cases.length > 0 && (
          <Section
            icon={<ShieldAlert className="h-4 w-4 text-amber-500" />}
            label="Edge Cases"
          >
            <ul className="space-y-1.5 text-sm">
              {testCase.edge_cases.map((edge, i) => (
                <li
                  key={i}
                  className="flex gap-2 rounded-md border border-amber-500/15 bg-amber-500/5 px-3 py-1.5 text-foreground/90"
                >
                  <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-500" />
                  <span>{edge}</span>
                </li>
              ))}
            </ul>
          </Section>
        )}
      </CardContent>
    </Card>
  );
}

interface SectionProps {
  icon: React.ReactNode;
  label: string;
  children: React.ReactNode;
}

function Section({ icon, label, children }: SectionProps) {
  return (
    <section className="space-y-2.5">
      <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        {icon}
        {label}
      </div>
      {children}
    </section>
  );
}

export function TestCaseCardSkeleton() {
  return (
    <Card className="border-border/60 bg-card/60">
      <CardContent className="space-y-4 p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <div className="h-3 w-16 rounded bg-muted" />
            <div className="h-5 w-64 rounded bg-muted" />
          </div>
          <div className="h-5 w-16 rounded-full bg-muted" />
        </div>
        <div className="space-y-2">
          <div className="h-3 w-20 rounded bg-muted" />
          <div className="h-3 w-full rounded bg-muted" />
          <div className="h-3 w-3/4 rounded bg-muted" />
        </div>
      </CardContent>
    </Card>
  );
}

export function TestCaseSummary({ count }: { count: number }) {
  return (
    <div className="flex items-center gap-2 text-sm text-muted-foreground">
      <FileText className="h-4 w-4" />
      <span>
        {count} test {count === 1 ? "case" : "cases"} generated
      </span>
    </div>
  );
}

export function formatTestCaseAsText(testCase: TestCase): string {
  const lines: string[] = [
    `[${testCase.test_case_id}] ${testCase.title}`,
    `Priority: ${testCase.priority}`,
    "",
    "Test Steps:",
    ...testCase.steps.map((step, i) => `  ${i + 1}. ${step}`),
    "",
    `Expected Result: ${testCase.expected_result}`,
  ];
  if (testCase.edge_cases.length > 0) {
    lines.push("", "Edge Cases:");
    testCase.edge_cases.forEach((edge) => lines.push(`  - ${edge}`));
  }
  return lines.join("\n");
}
