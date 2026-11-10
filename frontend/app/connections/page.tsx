"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { ConnectionForm } from "@/components/connection-form";
import { SchemaTree } from "@/components/schema-tree";
import { useConnections, useInvalidateConnections } from "@/lib/hooks";
import { api } from "@/lib/api-client";
import { toast } from "sonner";

export default function ConnectionsPage() {
  const { data: connections, isLoading } = useConnections();
  const invalidate = useInvalidateConnections();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);

  async function handleDelete(id: string) {
    try {
      await api.deleteConnection(id);
      toast.success("Conexão removida.");
      invalidate();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Falha ao remover conexão.");
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Conexões</h1>
          <p className="text-sm text-muted-foreground">
            Cadastre bancos Postgres, MySQL, SQLite, SQL Server ou qualquer outro dialeto
            suportado pelo SQLAlchemy.
          </p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <Button onClick={() => setDialogOpen(true)}>
            <Plus className="size-4" />
            Nova conexão
          </Button>
          <DialogContent className="sm:max-w-lg">
            <DialogHeader>
              <DialogTitle>Nova conexão</DialogTitle>
              <DialogDescription>
                Os dados de conexão ficam armazenados localmente, com a senha cifrada.
              </DialogDescription>
            </DialogHeader>
            <ConnectionForm
              onSaved={() => {
                setDialogOpen(false);
                invalidate();
              }}
            />
          </DialogContent>
        </Dialog>
      </div>

      {isLoading && <p className="text-sm text-muted-foreground">Carregando...</p>}

      {!isLoading && connections?.length === 0 && (
        <Card>
          <CardContent className="py-10 text-center text-sm text-muted-foreground">
            Nenhuma conexão cadastrada ainda.
          </CardContent>
        </Card>
      )}

      <div className="space-y-3">
        {connections?.map((conn) => (
          <Card key={conn.id}>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-medium">{conn.name}</span>
                  <Badge variant="secondary">{conn.dialect}</Badge>
                  {conn.allow_write && (
                    <Badge variant="outline" className="text-amber-500 border-amber-500/40">
                      Escrita habilitada
                    </Badge>
                  )}
                </div>
                <div className="flex items-center gap-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setExpanded(expanded === conn.id ? null : conn.id)}
                  >
                    {expanded === conn.id ? (
                      <ChevronUp className="size-4" />
                    ) : (
                      <ChevronDown className="size-4" />
                    )}
                    Esquema
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="size-8 text-destructive hover:text-destructive"
                    onClick={() => handleDelete(conn.id)}
                  >
                    <Trash2 className="size-4" />
                  </Button>
                </div>
              </div>
              {expanded === conn.id && (
                <div className="border-t border-border pt-3">
                  <SchemaTree connectionId={conn.id} />
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
