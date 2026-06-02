import {
  ClipboardList,
  FileCheck2,
  History,
  Sparkles,
  Target,
  Workflow,
} from "lucide-react";

import { cn } from "@/lib/utils";

const FEATURES = [
  {
    icon: Sparkles,
    title: "AI-driven generation",
    description:
      "Powered by Google Gemini with a strict JSON-only system prompt for reliable, structured output.",
  },
  {
    icon: ClipboardList,
    title: "3–5 test cases per run",
    description:
      "Each generation includes positive and negative scenarios with steps, expected results, and edge cases.",
  },
  {
    icon: Target,
    title: "Risk-based prioritisation",
    description:
      "Each test case is tagged Low, Medium, High, or Critical so you know what to tackle first.",
  },
  {
    icon: FileCheck2,
    title: "Polished PDF reports",
    description:
      "One-click download produces a clean, print-ready PDF suitable for sharing with stakeholders.",
  },
  {
    icon: History,
    title: "Persistent history",
    description:
      "Every generation is stored in PostgreSQL. Re-open, re-download, and audit at any time.",
  },
  {
    icon: Workflow,
    title: "API-first design",
    description:
      "Clean FastAPI backend with typed Pydantic schemas, ready to plug into CI/CD or test management tools.",
  },
];

export function FeaturesSection() {
  return (
    <section className="container py-16 md:py-24">
      <div className="mx-auto max-w-2xl text-center">
        <p className="text-sm font-medium uppercase tracking-wider text-primary">
          Features
        </p>
        <h2 className="mt-2 text-3xl font-bold tracking-tight md:text-4xl">
          Everything you need to draft QA in seconds.
        </h2>
        <p className="mt-3 text-muted-foreground">
          A focused toolkit built around one job: turning your ideas into
          well-structured, executable test cases.
        </p>
      </div>

      <div className="mt-12 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {FEATURES.map((feature) => (
          <FeatureCard key={feature.title} {...feature} />
        ))}
      </div>
    </section>
  );
}

interface FeatureCardProps {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
}

function FeatureCard({ icon: Icon, title, description }: FeatureCardProps) {
  return (
    <div
      className={cn(
        "group relative overflow-hidden rounded-xl border border-border/60 bg-card p-6 transition-all",
        "hover:border-primary/40 hover:shadow-lg hover:shadow-primary/5",
      )}
    >
      <div className="absolute inset-x-0 -top-px h-px bg-gradient-to-r from-transparent via-primary/40 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
      <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
        <Icon className="h-5 w-5" />
      </div>
      <h3 className="text-base font-semibold tracking-tight">{title}</h3>
      <p className="mt-2 text-sm text-muted-foreground">{description}</p>
    </div>
  );
}
