export type Priority = "Low" | "Medium" | "High" | "Critical";

export interface TestCase {
  test_case_id: string;
  title: string;
  priority: Priority;
  steps: string[];
  expected_result: string;
  edge_cases: string[];
}

export interface TestGeneration {
  id: number;
  requirement: string;
  test_cases: TestCase[];
  created_at: string;
}

export interface TestGenerationSummary {
  id: number;
  requirement: string;
  created_at: string;
  test_case_count: number;
}

export interface ApiError {
  detail: string;
}
