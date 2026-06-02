import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Test Case Results — TestForge AI",
  description:
    "Review AI-generated test cases for your requirement. Copy to clipboard or download as a PDF.",
};

export default function ResultsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
