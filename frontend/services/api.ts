"use client";

import { ApiError, TestGeneration, TestGenerationSummary } from "@/lib/types";

const DEFAULT_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

class ApiClientError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
  }
}

async function request<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const base = DEFAULT_BASE_URL.replace(/\/$/, "");
  const url = `${base}${path}`;

  let response: Response;
  try {
    response = await fetch(url, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init.headers ?? {}),
      },
      cache: "no-store",
    });
  } catch (networkError) {
    throw new ApiClientError(
      "Unable to reach the API. Is the backend running?",
      0,
    );
  }

  if (!response.ok) {
    let message = `Request failed with status ${response.status}.`;
    try {
      const body = (await response.json()) as ApiError;
      if (body?.detail) {
        message = body.detail;
      }
    } catch {
      // ignore JSON parse errors and fall back to default message
    }
    throw new ApiClientError(message, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export const api = {
  generate(requirement: string): Promise<TestGeneration> {
    return request<TestGeneration>("/api/generate", {
      method: "POST",
      body: JSON.stringify({ requirement }),
    });
  },

  listHistory(): Promise<TestGenerationSummary[]> {
    return request<TestGenerationSummary[]>("/api/history", { method: "GET" });
  },

  getHistory(id: number): Promise<TestGeneration> {
    return request<TestGeneration>(`/api/history/${id}`, { method: "GET" });
  },

  pdfUrl(id: number): string {
    const base = DEFAULT_BASE_URL.replace(/\/$/, "");
    return `${base}/api/history/${id}/pdf`;
  },
};

export { ApiClientError };
