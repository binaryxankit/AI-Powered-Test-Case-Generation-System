import { AlertCircle, FileSearch2, Inbox } from "lucide-react";
import * as React from "react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type EmptyStateVariant = "empty" | "error" | "not-found";

interface EmptyStateProps {
  variant?: EmptyStateVariant;
  title: string;
  description?: string;
  actionLabel?: string;
  actionHref?: string;
  onAction?: () => void;
  className?: string;
}

const ICON_MAP: Record<EmptyStateVariant, React.ComponentType<{ className?: string }>> = {
  empty: Inbox,
  error: AlertCircle,
  "not-found": FileSearch2,
};

const ACCENT_MAP: Record<EmptyStateVariant, string> = {
  empty: "from-primary/20 to-violet-500/20",
  error: "from-destructive/20 to-amber-500/20",
  "not-found": "from-blue-500/20 to-cyan-500/20",
};

export function EmptyState({
  variant = "empty",
  title,
  description,
  actionLabel,
  actionHref,
  onAction,
  className,
}: EmptyStateProps) {
  const Icon = ICON_MAP[variant];

  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center rounded-2xl border border-dashed border-border/70 bg-card/40 px-6 py-14 text-center",
        className,
      )}
    >
      <div
        className={cn(
          "mb-5 grid h-14 w-14 place-items-center rounded-2xl bg-gradient-to-br text-foreground shadow-inner",
          ACCENT_MAP[variant],
        )}
      >
        <Icon className="h-6 w-6" />
      </div>
      <h3 className="text-lg font-semibold tracking-tight">{title}</h3>
      {description ? (
        <p className="mt-1 max-w-sm text-sm text-muted-foreground">
          {description}
        </p>
      ) : null}
      {actionLabel ? (
        <div className="mt-6">
          {actionHref ? (
            <Button asChild>
              <a href={actionHref}>{actionLabel}</a>
            </Button>
          ) : (
            <Button onClick={onAction}>{actionLabel}</Button>
          )}
        </div>
      ) : null}
    </div>
  );
}
