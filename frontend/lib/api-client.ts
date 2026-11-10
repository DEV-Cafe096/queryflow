import type {
  ConnectionConfig,
  ConnectionSummary,
  HistoryItem,
  QueryExecuteResponse,
  QueryGenerateResponse,
  SchemaResponse,
} from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(message: string, public status: number) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? JSON.stringify(body);
    } catch {
      // ignore parse failure, keep statusText
    }
    throw new ApiError(detail, res.status);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  testConnection: (config: ConnectionConfig) =>
    request<{ ok: boolean }>("/api/connections/test", {
      method: "POST",
      body: JSON.stringify(config),
    }),

  createConnection: (config: ConnectionConfig) =>
    request<ConnectionSummary>("/api/connections", {
      method: "POST",
      body: JSON.stringify(config),
    }),

  listConnections: () => request<ConnectionSummary[]>("/api/connections"),

  deleteConnection: (id: string) =>
    request<{ ok: boolean }>(`/api/connections/${id}`, { method: "DELETE" }),

  getSchema: (connectionId: string) =>
    request<SchemaResponse>(`/api/connections/${connectionId}/schema`),

  generateQuery: (connectionId: string, question: string) =>
    request<QueryGenerateResponse>("/api/query", {
      method: "POST",
      body: JSON.stringify({ connection_id: connectionId, question }),
    }),

  executeQuery: (connectionId: string, sql: string, historyId?: string) =>
    request<QueryExecuteResponse>("/api/query/execute", {
      method: "POST",
      body: JSON.stringify({ connection_id: connectionId, sql, history_id: historyId }),
    }),

  listHistory: () => request<HistoryItem[]>("/api/history"),

  sendFeedback: (historyId: string, feedback: string) =>
    request<{ ok: boolean }>(`/api/history/${historyId}/feedback`, {
      method: "POST",
      body: JSON.stringify({ feedback }),
    }),

  listModels: (apiKey?: string) =>
    request<{ models: string[] }>("/api/models/list", {
      method: "POST",
      body: JSON.stringify({ api_key: apiKey || null }),
    }),
};

export type StreamEvent =
  | { type: "status"; message: string }
  | { type: "sql"; history_id: string; sql: string }
  | { type: "result"; data: QueryExecuteResponse }
  | { type: "error"; message: string };

export function streamQuery(
  connectionId: string,
  question: string,
  onEvent: (event: StreamEvent) => void
): () => void {
  const url = new URL(`${BASE_URL}/api/query/stream`);
  url.searchParams.set("connection_id", connectionId);
  url.searchParams.set("question", question);

  const source = new EventSource(url.toString());

  source.addEventListener("status", (e) => {
    const data = JSON.parse((e as MessageEvent).data);
    onEvent({ type: "status", message: data.message });
  });
  source.addEventListener("sql", (e) => {
    const data = JSON.parse((e as MessageEvent).data);
    onEvent({ type: "sql", history_id: data.history_id, sql: data.sql });
  });
  source.addEventListener("result", (e) => {
    const data = JSON.parse((e as MessageEvent).data);
    onEvent({ type: "result", data });
    source.close();
  });
  source.addEventListener("error", (e) => {
    const raw = (e as MessageEvent).data;
    let message = "Conexão com o servidor perdida.";
    if (raw) {
      try {
        message = JSON.parse(raw).message ?? message;
      } catch {
        // keep default message
      }
    }
    onEvent({ type: "error", message });
    source.close();
  });

  return () => source.close();
}
