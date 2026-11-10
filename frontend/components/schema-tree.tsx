"use client";

import { Loader2, KeyRound, Table2 } from "lucide-react";
import { useSchema } from "@/lib/hooks";

export function SchemaTree({ connectionId }: { connectionId: string }) {
  const { data, isLoading, error } = useSchema(connectionId);

  if (isLoading) {
    return (
      <p className="flex items-center gap-2 text-sm text-muted-foreground">
        <Loader2 className="size-3.5 animate-spin" />
        Lendo esquema...
      </p>
    );
  }

  if (error) {
    return (
      <p className="text-sm text-destructive">
        {error instanceof Error ? error.message : "Falha ao ler esquema."}
      </p>
    );
  }

  if (!data || data.tables.length === 0) {
    return <p className="text-sm text-muted-foreground">Nenhuma tabela encontrada.</p>;
  }

  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {data.tables.map((table) => (
        <div key={table.name} className="rounded-md border border-border p-3">
          <div className="mb-1.5 flex items-center gap-1.5 text-sm font-medium">
            <Table2 className="size-3.5 text-muted-foreground" />
            {table.name}
          </div>
          <ul className="space-y-0.5">
            {table.columns.map((col) => (
              <li
                key={col.name}
                className="flex items-center justify-between text-xs text-muted-foreground"
              >
                <span className="flex items-center gap-1">
                  {col.primary_key && <KeyRound className="size-3 text-amber-500" />}
                  {col.name}
                </span>
                <span className="font-mono">{col.type}</span>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
