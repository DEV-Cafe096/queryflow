"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./api-client";

export function useConnections() {
  return useQuery({
    queryKey: ["connections"],
    queryFn: api.listConnections,
  });
}

export function useSchema(connectionId: string | undefined) {
  return useQuery({
    queryKey: ["schema", connectionId],
    queryFn: () => api.getSchema(connectionId as string),
    enabled: Boolean(connectionId),
    staleTime: 60_000,
  });
}

export function useHistory() {
  return useQuery({
    queryKey: ["history"],
    queryFn: () => api.listHistory(),
  });
}

export function useInvalidateConnections() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: ["connections"] });
}
