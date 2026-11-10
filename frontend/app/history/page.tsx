"use client";

import { Fragment, useState } from "react";
import { ThumbsDown, ThumbsUp } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useHistory } from "@/lib/hooks";

function formatDate(iso: string) {
  return new Date(iso).toLocaleString("pt-BR");
}

export default function HistoryPage() {
  const { data: history, isLoading } = useHistory();
  const [expanded, setExpanded] = useState<string | null>(null);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Histórico</h1>
        <p className="text-sm text-muted-foreground">
          Perguntas, SQL gerado e feedback de todas as conexões.
        </p>
      </div>

      {isLoading && <p className="text-sm text-muted-foreground">Carregando...</p>}

      {!isLoading && history?.length === 0 && (
        <Card>
          <CardContent className="py-10 text-center text-sm text-muted-foreground">
            Nenhuma pergunta feita ainda.
          </CardContent>
        </Card>
      )}

      {history && history.length > 0 && (
        <div className="overflow-auto rounded-md border border-border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Quando</TableHead>
                <TableHead>Pergunta</TableHead>
                <TableHead>Linhas</TableHead>
                <TableHead>Feedback</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {history.map((item) => (
                <Fragment key={item.id}>
                  <TableRow
                    className="cursor-pointer"
                    onClick={() => setExpanded(expanded === item.id ? null : item.id)}
                  >
                    <TableCell className="whitespace-nowrap text-xs text-muted-foreground">
                      {formatDate(item.created_at)}
                    </TableCell>
                    <TableCell className="max-w-md truncate">{item.question}</TableCell>
                    <TableCell>
                      {item.error ? (
                        <Badge variant="outline" className="text-destructive border-destructive/40">
                          erro
                        </Badge>
                      ) : (
                        (item.row_count ?? "—")
                      )}
                    </TableCell>
                    <TableCell>
                      {item.feedback === "up" && <ThumbsUp className="size-4 text-emerald-500" />}
                      {item.feedback === "down" && <ThumbsDown className="size-4 text-destructive" />}
                    </TableCell>
                  </TableRow>
                  {expanded === item.id && (
                    <TableRow>
                      <TableCell colSpan={4} className="bg-secondary/40">
                        <pre className="overflow-auto whitespace-pre-wrap font-mono text-xs">
                          {item.sql || item.error}
                        </pre>
                      </TableCell>
                    </TableRow>
                  )}
                </Fragment>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}
