"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Database, History, Waves } from "lucide-react";
import { cn } from "@/lib/utils";

const links = [
  { href: "/", label: "Consultas", icon: Waves },
  { href: "/connections", label: "Conexões", icon: Database },
  { href: "/history", label: "Histórico", icon: History },
];

export function NavBar() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-40 border-b border-border/60 bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
        <Link href="/" className="flex items-center gap-2 font-semibold tracking-tight">
          <span className="flex size-7 items-center justify-center rounded-lg bg-gradient-to-br from-[var(--brand-blue)] to-[var(--brand-purple)] text-white">
            <Waves className="size-4" />
          </span>
          QueryFlow
        </Link>
        <nav className="flex items-center gap-1">
          {links.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
                  active
                    ? "bg-secondary text-secondary-foreground"
                    : "text-muted-foreground hover:bg-secondary/60 hover:text-foreground"
                )}
              >
                <Icon className="size-4" />
                {label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
