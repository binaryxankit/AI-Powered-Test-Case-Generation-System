import { CheckCircle2, ClipboardList, FlaskConical, Sparkles, Workflow, Zap } from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";

export function HeroSection() {
  return (
    <section className="relative overflow-hidden">
      <div className="absolute inset-0 -z-10 grid-pattern opacity-60" />
      <div className="absolute -top-32 left-1/2 -z-10 h-72 w-[40rem] -translate-x-1/2 rounded-full bg-primary/30 blur-3xl" />
      <div className="absolute -bottom-24 right-0 -z-10 h-72 w-72 rounded-full bg-violet-500/20 blur-3xl" />

      <div className="container flex flex-col items-center py-20 text-center md:py-28">
        <span className="inline-flex items-center gap-2 rounded-full border border-border/60 bg-card/60 px-3 py-1 text-xs font-medium text-muted-foreground backdrop-blur">
          <Sparkles className="h-3.5 w-3.5 text-primary" />
          AI-powered QA for modern teams
        </span>

        <h1 className="mt-6 max-w-3xl text-balance text-4xl font-bold tracking-tight md:text-6xl">
          Turn plain-English requirements into
          <span className="gradient-text"> production-ready test cases.</span>
        </h1>

        <p className="mt-5 max-w-2xl text-balance text-base text-muted-foreground md:text-lg">
          TestForge AI converts your requirements into structured, prioritised
          test cases — with steps, expected results, and edge cases — in
          seconds. Built for QA engineers, developers, and product managers.
        </p>

        <div className="mt-8 flex flex-col items-center gap-3 sm:flex-row">
          <Button asChild size="xl" variant="gradient" className="w-full sm:w-auto">
            <Link href="/generate">
              <Sparkles className="h-4 w-4" />
              Generate Test Cases
            </Link>
          </Button>
          <Button asChild size="xl" variant="outline" className="w-full sm:w-auto">
            <Link href="/history">View history</Link>
          </Button>
        </div>

        <div className="mt-14 grid w-full max-w-4xl gap-4 rounded-2xl border border-border/60 bg-card/50 p-2 text-left md:grid-cols-3">
          <HeroStat
            icon={<Zap className="h-4 w-4 text-primary" />}
            label="Average generation time"
            value="< 6s"
          />
          <HeroStat
            icon={<ClipboardList className="h-4 w-4 text-primary" />}
            label="Test cases per requirement"
            value="3 – 5"
          />
          <HeroStat
            icon={<CheckCircle2 className="h-4 w-4 text-primary" />}
            label="Includes positive & negative"
            value="Always"
          />
        </div>
      </div>
    </section>
  );
}

interface HeroStatProps {
  icon: React.ReactNode;
  label: string;
  value: string;
}

function HeroStat({ icon, label, value }: HeroStatProps) {
  return (
    <div className="rounded-xl bg-background/60 p-4">
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        {icon}
        {label}
      </div>
      <div className="mt-2 text-2xl font-semibold tracking-tight">{value}</div>
    </div>
  );
}
