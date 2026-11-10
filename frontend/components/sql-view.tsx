"use client";

import { useState } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { format as formatSql } from "sql-formatter";
import { Check, Copy, Pencil, Play, Wand2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";

export function SqlView({
  sql,
  onChange,
  onExecute,
  loading,
}: {
  sql: string;
  onChange: (sql: string) => void;
  onExecute: () => void;
  loading?: boolean;
}) {
  const [editing, setEditing] = useState(false);
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    await navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  function handleFormat() {
    try {
      onChange(formatSql(sql, { language: "sql" }));
    } catch {
      toast.error("Não foi possível formatar este SQL.");
    }
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          SQL gerado
        </span>
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="sm" onClick={handleFormat}>
            <Wand2 className="size-3.5" />
            Formatar
          </Button>
          <Button variant="ghost" size="sm" onClick={handleCopy}>
            {copied ? <Check className="size-3.5" /> : <Copy className="size-3.5" />}
            {copied ? "Copiado" : "Copiar"}
          </Button>
          <Button variant="ghost" size="sm" onClick={() => setEditing((v) => !v)}>
            <Pencil className="size-3.5" />
            {editing ? "Ver" : "Editar"}
          </Button>
        </div>
      </div>

      {editing ? (
        <Textarea
          value={sql}
          onChange={(e) => onChange(e.target.value)}
          rows={8}
          className="font-mono text-sm"
        />
      ) : (
        <div className="overflow-hidden rounded-md border border-border">
          <SyntaxHighlighter
            language="sql"
            style={oneDark}
            customStyle={{ margin: 0, fontSize: "0.85rem", padding: "1rem" }}
          >
            {sql}
          </SyntaxHighlighter>
        </div>
      )}

      <Button onClick={onExecute} disabled={loading || !sql.trim()} className="w-full sm:w-auto">
        <Play className="size-4" />
        {loading ? "Executando..." : "Executar SQL"}
      </Button>
    </div>
  );
}
