"use client";

import { useState } from "react";
import { Loader2, PlugZap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { api } from "@/lib/api-client";
import type { ConnectionConfig, Dialect } from "@/lib/types";
import { toast } from "sonner";

const DEFAULT_PORTS: Record<string, number> = {
  postgresql: 5432,
  mysql: 3306,
  mssql: 1433,
};

const DIALECT_LABELS: Record<Dialect, string> = {
  postgresql: "PostgreSQL",
  mysql: "MySQL",
  sqlite: "SQLite",
  mssql: "SQL Server",
  other: "Outro (via URL SQLAlchemy)",
};

const initialForm: ConnectionConfig = {
  name: "",
  dialect: "postgresql",
  host: "",
  port: DEFAULT_PORTS.postgresql,
  user: "",
  password: "",
  database: "",
  raw_url: "",
  allow_write: false,
};

export function ConnectionForm({ onSaved }: { onSaved: () => void }) {
  const [form, setForm] = useState<ConnectionConfig>(initialForm);
  const [testing, setTesting] = useState(false);
  const [saving, setSaving] = useState(false);

  function update<K extends keyof ConnectionConfig>(key: K, value: ConnectionConfig[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  function handleDialectChange(dialect: Dialect) {
    setForm((f) => ({ ...f, dialect, port: DEFAULT_PORTS[dialect] ?? null }));
  }

  function buildPayload(): ConnectionConfig {
    const base = { name: form.name, dialect: form.dialect, allow_write: form.allow_write };
    if (form.dialect === "sqlite") return { ...base, database: form.database };
    if (form.dialect === "other") return { ...base, raw_url: form.raw_url };
    return {
      ...base,
      host: form.host,
      port: form.port,
      user: form.user,
      password: form.password,
      database: form.database,
    };
  }

  async function handleTest() {
    setTesting(true);
    try {
      await api.testConnection(buildPayload());
      toast.success("Conexão bem-sucedida!");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Falha ao conectar.");
    } finally {
      setTesting(false);
    }
  }

  async function handleSave() {
    if (!form.name.trim()) {
      toast.error("Dê um nome para a conexão.");
      return;
    }
    setSaving(true);
    try {
      await api.createConnection(buildPayload());
      toast.success("Conexão salva!");
      setForm(initialForm);
      onSaved();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Falha ao salvar conexão.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-2">
        <div className="space-y-1.5">
          <Label htmlFor="conn-name">Nome</Label>
          <Input
            id="conn-name"
            value={form.name}
            onChange={(e) => update("name", e.target.value)}
            placeholder="Ex: Produção Postgres"
          />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="conn-dialect">Dialeto</Label>
          <Select
            value={form.dialect}
            onValueChange={(v) => v && handleDialectChange(v as Dialect)}
          >
            <SelectTrigger id="conn-dialect" className="w-full">
              <SelectValue>{(d: Dialect) => DIALECT_LABELS[d]}</SelectValue>
            </SelectTrigger>
            <SelectContent>
              {(Object.keys(DIALECT_LABELS) as Dialect[]).map((d) => (
                <SelectItem key={d} value={d}>
                  {DIALECT_LABELS[d]}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {form.dialect === "sqlite" && (
        <div className="space-y-1.5">
          <Label htmlFor="conn-database-path">Caminho do arquivo</Label>
          <Input
            id="conn-database-path"
            value={form.database ?? ""}
            onChange={(e) => update("database", e.target.value)}
            placeholder="./demo.db"
          />
        </div>
      )}

      {form.dialect === "other" && (
        <div className="space-y-1.5">
          <Label htmlFor="conn-raw-url">URL SQLAlchemy</Label>
          <Input
            id="conn-raw-url"
            value={form.raw_url ?? ""}
            onChange={(e) => update("raw_url", e.target.value)}
            placeholder="snowflake://user:pass@account/db"
          />
        </div>
      )}

      {form.dialect !== "sqlite" && form.dialect !== "other" && (
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="space-y-1.5">
            <Label htmlFor="conn-host">Host</Label>
            <Input
              id="conn-host"
              value={form.host ?? ""}
              onChange={(e) => update("host", e.target.value)}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="conn-port">Porta</Label>
            <Input
              id="conn-port"
              type="number"
              value={form.port ?? ""}
              onChange={(e) => update("port", Number(e.target.value))}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="conn-user">Usuário</Label>
            <Input
              id="conn-user"
              value={form.user ?? ""}
              onChange={(e) => update("user", e.target.value)}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="conn-password">Senha</Label>
            <Input
              id="conn-password"
              type="password"
              value={form.password ?? ""}
              onChange={(e) => update("password", e.target.value)}
            />
          </div>
          <div className="space-y-1.5 sm:col-span-2">
            <Label htmlFor="conn-database">Banco de dados</Label>
            <Input
              id="conn-database"
              value={form.database ?? ""}
              onChange={(e) => update("database", e.target.value)}
            />
          </div>
        </div>
      )}

      <div className="flex items-center justify-between rounded-md border border-border p-3">
        <div>
          <Label htmlFor="conn-allow-write" className="text-sm font-medium">
            Permitir escrita
          </Label>
          <p className="text-xs text-muted-foreground">
            Libera INSERT/UPDATE/DELETE (sempre exige WHERE). Desligado = somente leitura.
          </p>
        </div>
        <Switch
          id="conn-allow-write"
          checked={form.allow_write ?? false}
          onCheckedChange={(v) => update("allow_write", v)}
        />
      </div>

      <div className="flex justify-end gap-2">
        <Button variant="outline" onClick={handleTest} disabled={testing}>
          {testing ? <Loader2 className="size-4 animate-spin" /> : <PlugZap className="size-4" />}
          Testar conexão
        </Button>
        <Button onClick={handleSave} disabled={saving}>
          {saving && <Loader2 className="size-4 animate-spin" />}
          Salvar conexão
        </Button>
      </div>
    </div>
  );
}
