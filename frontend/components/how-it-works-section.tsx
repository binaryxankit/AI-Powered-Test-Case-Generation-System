import { FileText, Sparkles, Workflow } from "lucide-react";

const STEPS = [
  {
    number: 1,
    title: "Describe your requirement",
    description:
      "Type a sentence or two about what you want to verify. Be as specific as you like — the more context, the better the cases.",
    icon: FileText,
  },
  {
    number: 2,
    title: "Let the AI do the work",
    description:
      "Our Gemini-powered engine analyses the requirement and produces 3–5 structured test cases with steps and edge cases.",
    icon: Sparkles,
  },
  {
    number: 3,
    title: "Review, export, and reuse",
    description:
      "Inspect each card, download a polished PDF, or come back later via the history page. It&apos;s that simple.",
    icon: Workflow,
  },
];

export function HowItWorksSection() {
  return (
    <section className="border-y border-border/40 bg-secondary/20">
      <div className="container py-16 md:py-24">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-sm font-medium uppercase tracking-wider text-primary">
            How it works
          </p>
          <h2 className="mt-2 text-3xl font-bold tracking-tight md:text-4xl">
            Three steps from idea to test plan.
          </h2>
          <p className="mt-3 text-muted-foreground">
            No setup, no login, no nonsense. Just type, generate, and ship.
          </p>
        </div>

        <ol className="mt-12 grid gap-6 md:grid-cols-3">
          {STEPS.map((step) => (
            <li
              key={step.number}
              className="relative flex flex-col rounded-2xl border border-border/60 bg-card p-6"
            >
              <div className="mb-4 flex items-center gap-3">
                <span className="grid h-9 w-9 place-items-center rounded-full bg-primary/15 text-sm font-semibold text-primary">
                  {step.number}
                </span>
                <step.icon className="h-5 w-5 text-muted-foreground" />
              </div>
              <h3 className="text-base font-semibold tracking-tight">
                {step.title}
              </h3>
              <p className="mt-2 text-sm text-muted-foreground">
                {step.description}
              </p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
