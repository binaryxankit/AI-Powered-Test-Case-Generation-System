import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Generate Test Cases — TestForge AI",
  description:
    "Type a plain-English requirement and let the AI produce 3–5 prioritised test cases in seconds.",
};

export default function GenerateLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
