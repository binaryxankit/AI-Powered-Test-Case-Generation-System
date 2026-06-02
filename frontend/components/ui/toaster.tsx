"use client";

import { useEffect, useState } from "react";

type Toast = {
  id: number;
  title?: string;
  description?: string;
  variant?: "default" | "destructive";
};

let push: ((t: Omit<Toast, "id">) => void) | null = null;
let counter = 0;

export function toast(t: Omit<Toast, "id">) {
  push?.(t);
}

export function Toaster() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  useEffect(() => {
    push = (t) => {
      counter += 1;
      const id = counter;
      setToasts((prev) => [...prev, { ...t, id }]);
      setTimeout(() => {
        setToasts((prev) => prev.filter((x) => x.id !== id));
      }, 4000);
    };
    return () => {
      push = null;
    };
  }, []);

  return (
    <div className="pointer-events-none fixed inset-x-0 bottom-4 z-50 flex flex-col items-center gap-2 px-4">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={
            "pointer-events-auto w-full max-w-sm rounded-lg border px-4 py-3 text-sm shadow-lg backdrop-blur " +
            (t.variant === "destructive"
              ? "border-destructive/40 bg-destructive/10 text-destructive"
              : "border-border bg-card text-card-foreground")
          }
        >
          {t.title ? <div className="font-semibold">{t.title}</div> : null}
          {t.description ? (
            <div className="text-xs text-muted-foreground">{t.description}</div>
          ) : null}
        </div>
      ))}
    </div>
  );
}
