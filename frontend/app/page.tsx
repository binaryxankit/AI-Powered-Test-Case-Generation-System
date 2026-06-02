import type { Metadata } from "next";

import { FeaturesSection } from "@/components/features-section";
import { HeroSection } from "@/components/hero-section";
import { HowItWorksSection } from "@/components/how-it-works-section";

export const metadata: Metadata = {
  title: "TestForge AI — Generate Test Cases with AI",
  description:
    "Turn plain-English requirements into structured, prioritised software test cases in seconds. Powered by Google Gemini.",
  openGraph: {
    title: "TestForge AI",
    description:
      "Generate production-ready software test cases from natural-language requirements.",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "TestForge AI",
    description:
      "Generate production-ready software test cases from natural-language requirements.",
  },
};

export default function HomePage() {
  return (
    <>
      <HeroSection />
      <FeaturesSection />
      <HowItWorksSection />
    </>
  );
}
