export type Dialect = "postgresql" | "mysql" | "sqlite" | "mssql" | "other";

export interface ConnectionConfig {
  name: string;
  dialect: Dialect;
  host?: string | null;
  port?: number | null;
  user?: string | null;
  password?: string | null;
  database?: string | null;
  raw_url?: string | null;
  allow_write?: boolean;
}

export interface ConnectionSummary {
  id: string;
  name: string;
  dialect: Dialect;
  allow_write: boolean;
}

export interface ColumnInfo {
  name: string;
  type: string;
  primary_key: boolean;
}

export interface ForeignKeyInfo {
  constrained_columns: string[];
  referred_table: string;
  referred_columns: string[];
}

export interface TableInfo {
  name: string;
  columns: ColumnInfo[];
  foreign_keys: ForeignKeyInfo[];
}

export interface SchemaResponse {
  connection_id: string;
  dialect: Dialect;
  tables: TableInfo[];
}

export interface QueryGenerateResponse {
  history_id: string;
  question: string;
  sql: string;
  error?: string | null;
}

export interface QueryExecuteResponse {
  columns: string[];
  rows: Record<string, unknown>[];
  row_count: number;
  truncated: boolean;
  status_message?: string | null;
  error?: string | null;
}

export interface HistoryItem {
  id: string;
  connection_id: string;
  question: string;
  sql: string;
  row_count?: number | null;
  feedback?: string | null;
  error?: string | null;
  created_at: string;
}
