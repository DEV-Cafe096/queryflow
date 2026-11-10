"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { Loader2, Send, ThumbsDown, ThumbsUp } from "lucide-react";
import { Button, buttonVariants } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { SqlView } from "@/components/sql-view";
import { ResultsTable } from "@/components/results-table";
import { useConnections, useSchema } from "@/lib/hooks";
import { api, streamQuery } from "@/lib/api-client";
import type { QueryExecuteResponse } from "@/lib/types";
import { toast } from "sonner";

export default function WorkspacePage() {
  const { data: connections, isLoading: loadingConnections } = useConnections();
  const [connectionIdOverride, setConnectionIdOverride] = useState<string | null>(null);
  const connectionId = connectionIdOverride ?? connections?.[0]?.id ?? "";
  const [question, setQuestion] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [sql, setSql] = useState("");
  const [historyId, setHistoryId] = useState<string | null>(null);
  const [results, setResults] = useState<QueryExecuteResponse | null>(null);
  const [running, setRunning] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  const { data: schema } = useSchema(connectionId || undefined);

  const suggestions = useMemo(() => {
    if (!schema) return [];
    return schema.tables.slice(0, 4).map((t) => `Mostre os primeiros registros de ${t.name}`);
  }, [schema]);

  function resetResult() {
    setSql("");
    setHistoryId(null);
    setResults(null);
    setFeedback(null);
    setStatus(null);
  }

  function handleAsk() {
    if (!connectionId) {
      toast.error("Selecione uma conexão primeiro.");
      return;
    }
    if (!question.trim()) {
      toast.error("Digite uma pergunta.");
      return;
    }
    resetResult();
    setRunning(true);

    streamQuery(connectionId, question, (event) => {
      if (event.type === "status") {
        setStatus(event.message);
      } else if (event.type === "sql") {
        setSql(event.sql);
        setHistoryId(event.history_id);
      } else if (event.type === "result") {
        setResults(event.data);
        setStatus(null);
        setRunning(false);
        if (event.data.error) toast.error(event.data.error);
      } else if (event.type === "error") {
        setStatus(null);
        setRunning(false);
        toast.error(event.message);
      }
    });
  }

  async function handleExecuteEdited() {
    if (!connectionId || !sql.trim()) return;
    setRunning(true);
    try {
      const res = await api.executeQuery(connectionId, sql, historyId ?? undefined);
      setResults(res);
      if (res.error) toast.error(res.error);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Falha ao executar SQL.");
    } finally {
      setRunning(false);
    }
  }

  async function sendFeedback(value: "up" | "down") {
    if (!historyId) return;
    setFeedback(value);
    try {
      await api.sendFeedback(historyId, value);
      toast.success("Obrigado pelo feedback!");
    } catch {
      toast.error("Não foi possível salvar o feedback.");
    }
  }

  if (!loadingConnections && (!connections || connections.length === 0)) {
    return (
      <Card className="mx-auto max-w-lg text-center">
        <CardContent className="space-y-3 py-10">
          <p className="text-lg font-medium">Nenhuma conexão configurada ainda</p>
          <p className="text-sm text-muted-foreground">
            Cadastre uma conexão com seu banco de dados (Postgres, MySQL, SQLite, SQL Server ou
            outro) para começar a fazer perguntas.
          </p>
          <Link href="/connections" className={buttonVariants()}>
            Configurar conexão
          </Link>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight">Faça sua pergunta</h1>
        <p className="text-sm text-muted-foreground">
          Pergunte em português — o QueryFlow gera o SQL para o banco conectado e executa para
          você.
        </p>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <Select value={connectionId} onValueChange={(v) => setConnectionIdOverride(v)}>
          <SelectTrigger className="w-full sm:w-64">
            <SelectValue placeholder="Selecione uma conexão">
              {(id: string) => {
                const c = connections?.find((c) => c.id === id);
                return c ? `${c.name} · ${c.dialect}` : "Selecione uma conexão";
              }}
            </SelectValue>
          </SelectTrigger>
          <SelectContent>
            {connections?.map((c) => (
              <SelectItem key={c.id} value={c.id}>
                {c.name} · {c.dialect}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {connections?.find((c) => c.id === connectionId)?.allow_write && (
          <Badge variant="outline" className="w-fit text-amber-500 border-amber-500/40">
            Escrita habilitada
          </Badge>
        )}
      </div>

      {suggestions.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {suggestions.map((s) => (
            <button
              key={s}
              onClick={() => setQuestion(s)}
              className="rounded-full border border-border px-3 py-1 text-xs text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      <div className="flex gap-2">
        <Input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !running && handleAsk()}
          placeholder="Ex: quais os 5 clientes com maior saldo?"
          className="flex-1"
        />
        <Button onClick={handleAsk} disabled={running}>
          {running ? <Loader2 className="size-4 animate-spin" /> : <Send className="size-4" />}
          Perguntar
        </Button>
      </div>

      {status && (
        <p className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="size-3.5 animate-spin" />
          {status}
        </p>
      )}

      {sql && (
        <Card>
          <CardContent className="space-y-4 pt-6">
            <SqlView sql={sql} onChange={setSql} onExecute={handleExecuteEdited} loading={running} />

            {results && !results.error && (
              <div className="space-y-3 border-t border-border pt-4">
                {results.status_message && (
                  <p className="text-sm text-muted-foreground">{results.status_message}</p>
                )}
                <ResultsTable columns={results.columns} rows={results.rows} />

                {historyId && (
                  <div className="flex items-center gap-2 border-t border-border pt-3">
                    <span className="text-sm text-muted-foreground">Essa resposta ajudou?</span>
                    <Button
                      size="icon"
                      variant={feedback === "up" ? "default" : "outline"}
                      className="size-8"
                      onClick={() => sendFeedback("up")}
                    >
                      <ThumbsUp className="size-4" />
                    </Button>
                    <Button
                      size="icon"
                      variant={feedback === "down" ? "default" : "outline"}
                      className="size-8"
                      onClick={() => sendFeedback("down")}
                    >
                      <ThumbsDown className="size-4" />
                    </Button>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
