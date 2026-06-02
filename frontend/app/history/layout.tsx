import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "History — TestForge AI",
  description: "Re-open and re-download any previous test case generation.",
};

export default function HistoryLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
