"use client";

import * as React from "react";
import { Monitor, Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";

import { Button } from "@/components/ui/button";

type ThemeOption = "dark" | "light" | "system";

const THEME_CYCLE: ThemeOption[] = ["dark", "light", "system"];

const THEME_META: Record<ThemeOption, { icon: typeof Sun; label: string; next: ThemeOption }> = {
  dark: { icon: Moon, label: "Dark mode", next: "light" },
  light: { icon: Sun, label: "Light mode", next: "system" },
  system: { icon: Monitor, label: "System mode", next: "dark" },
};

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => setMounted(true), []);

  const current: ThemeOption =
    mounted && THEME_CYCLE.includes(theme as ThemeOption)
      ? (theme as ThemeOption)
      : "dark";

  const { icon: Icon, label } = THEME_META[current];

  const cycle = () => {
    const next = THEME_META[current].next;
    setTheme(next);
  };

  return (
    <Button
      variant="ghost"
      size="icon"
      aria-label={label}
      title={label}
      onClick={cycle}
    >
      {mounted ? (
        <Icon className="h-4 w-4" />
      ) : (
        <Moon className="h-4 w-4" />
      )}
    </Button>
  );
}
