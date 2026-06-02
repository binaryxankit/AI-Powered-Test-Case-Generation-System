"use client";

import { useRouter } from "next/navigation";
import * as React from "react";
import { Sparkles, Wand2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { api, ApiClientError } from "@/services/api";
import { toast } from "@/components/ui/toaster";

const PLACEHOLDER =
  "Verify login functionality and dashboard access for a SaaS web app";

const MIN_LENGTH = 3;
const MAX_LENGTH = 2000;

export default function GeneratePage() {
  const router = useRouter();
  const [requirement, setRequirement] = React.useState("");
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const trimmed = requirement.trim();
  const charCount = requirement.length;
  const isValid =
    trimmed.length >= MIN_LENGTH && trimmed.length <= MAX_LENGTH;
  const canSubmit = isValid && !isLoading;

  const handleKeyDown = React.useCallback(
    (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
        event.preventDefault();
        if (canSubmit) {
          event.currentTarget.form?.requestSubmit();
        }
      }
    },
    [canSubmit],
  );

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!canSubmit) return;

    setIsLoading(true);
    setError(null);
    try {
      const result = await api.generate(trimmed);
      sessionStorage.setItem(`generation:${result.id}`, JSON.stringify(result));
      toast({
        title: "Test cases generated",
        description: `${result.test_cases.length} cases ready to review.`,
      });
      router.push(`/results?id=${result.id}`);
    } catch (err) {
      const message =
        err instanceof ApiClientError
          ? err.message
          : "Something went wrong. Please try again.";
      setError(message);
      toast({
        title: "Generation failed",
        description: message,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSample = (sample: string) => {
    setRequirement(sample);
    setError(null);
  };

  return (
    <div className="container max-w-4xl py-12 md:py-20">
      <div className="mb-10 text-center">
        <span className="inline-flex items-center gap-2 rounded-full border border-border/60 bg-card/60 px-3 py-1 text-xs font-medium text-muted-foreground">
          <Wand2 className="h-3.5 w-3.5 text-primary" />
          Test Case Generator
        </span>
        <h1 className="mt-4 text-3xl font-bold tracking-tight md:text-4xl">
          Describe what to verify
        </h1>
        <p className="mt-3 text-muted-foreground">
          Type a single requirement in plain English. Our AI will produce
          structured test cases in seconds.
        </p>
      </div>

      <form
        onSubmit={handleSubmit}
        className="space-y-4 rounded-2xl border border-border/60 bg-card/70 p-6 shadow-sm backdrop-blur md:p-8"
      >
        <div className="space-y-2">
          <div className="flex items-baseline justify-between">
            <Label htmlFor="requirement">Requirement</Label>
            <span
              className={
                "text-xs " +
                (charCount > MAX_LENGTH
                  ? "text-destructive"
                  : "text-muted-foreground")
              }
            >
              {charCount}/{MAX_LENGTH}
            </span>
          </div>
          <Textarea
            id="requirement"
            name="requirement"
            value={requirement}
            onChange={(e) => setRequirement(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={PLACEHOLDER}
            disabled={isLoading}
            rows={6}
            autoFocus
            maxLength={MAX_LENGTH + 50}
            className="resize-y"
          />
          <p className="text-xs text-muted-foreground">
            Tip: be specific about the user action, system under test, and
            expected outcome. Press{" "}
            <kbd className="rounded border border-border/60 bg-background px-1.5 py-0.5 font-mono text-[10px]">
              Ctrl/⌘ + Enter
            </kbd>{" "}
            to generate.
          </p>
        </div>

        {error && (
          <Alert variant="destructive">
            <AlertTitle>Could not generate test cases</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="flex flex-col-reverse items-stretch gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            <span>Try:</span>
            <SampleChip
              onClick={() => handleSample(PLACEHOLDER)}
              disabled={isLoading}
            >
              Login flow
            </SampleChip>
            <SampleChip
              onClick={() =>
                handleSample(
                  "Verify that users can reset their password via the forgot-password link and receive a confirmation email within 60 seconds.",
                )
              }
              disabled={isLoading}
            >
              Password reset
            </SampleChip>
            <SampleChip
              onClick={() =>
                handleSample(
                  "Verify the shopping cart calculation for discounts, taxes, and shipping across multiple items and quantities.",
                )
              }
              disabled={isLoading}
            >
              Cart math
            </SampleChip>
          </div>
          <Button
            type="submit"
            size="lg"
            variant="gradient"
            disabled={!canSubmit}
            className="w-full sm:w-auto"
          >
            {isLoading ? (
              <>
                <Spinner size="sm" />
                Generating&hellip;
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                Generate Test Cases
              </>
            )}
          </Button>
        </div>
      </form>

      <section className="mt-12 grid gap-4 md:grid-cols-3">
        <Hint
          title="Be specific"
          description="Mention the user role, action, and expected outcome. e.g. 'admin can deactivate a user account'."
        />
        <Hint
          title="Include context"
          description="Mention platforms, devices, or data. e.g. 'mobile browser on iOS 17'."
        />
        <Hint
          title="State edge cases"
          description="If you have known risks, mention them so the AI can target them."
        />
      </section>
    </div>
  );
}

function SampleChip({
  children,
  onClick,
  disabled,
}: {
  children: React.ReactNode;
  onClick: () => void;
  disabled?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className="rounded-full border border-border/60 bg-background/60 px-2.5 py-1 text-xs font-medium transition-colors hover:border-primary/40 hover:bg-primary/5 disabled:opacity-50"
    >
      {children}
    </button>
  );
}

function Hint({ title, description }: { title: string; description: string }) {
  return (
    <div className="rounded-xl border border-border/50 bg-card/40 p-4">
      <h3 className="text-sm font-semibold">{title}</h3>
      <p className="mt-1 text-xs text-muted-foreground">{description}</p>
    </div>
  );
}
