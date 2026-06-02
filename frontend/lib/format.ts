import type { TestGeneration } from "@/lib/types";

/**
 * Render a full :class:`TestGeneration` as a single Markdown string
 * suitable for pasting into a PR description, a wiki page, or a Jira
 * ticket. Pure function — safe to call on the server.
 */
export function formatAllTestCasesAsMarkdown(generation: TestGeneration): string {
  const lines: string[] = [
    `# Test Cases — ${generation.requirement}`,
    "",
    `_Generated on ${new Date(generation.created_at).toUTCString()} • ${generation.test_cases.length} cases_`,
    "",
  ];

  generation.test_cases.forEach((testCase) => {
    lines.push(`## ${testCase.test_case_id}: ${testCase.title}`);
    lines.push("");
    lines.push(`**Priority:** ${testCase.priority}`);
    lines.push("");
    lines.push("**Test Steps**");
    lines.push("");
    testCase.steps.forEach((step, i) => {
      lines.push(`${i + 1}. ${step}`);
    });
    lines.push("");
    lines.push(`**Expected Result:** ${testCase.expected_result}`);
    lines.push("");

    if (testCase.edge_cases.length > 0) {
      lines.push("**Edge Cases**");
      lines.push("");
      testCase.edge_cases.forEach((edge) => {
        lines.push(`- ${edge}`);
      });
      lines.push("");
    }
  });

  return lines.join("\n").trimEnd() + "\n";
}
