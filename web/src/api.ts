import type { AuditRun, ContractRate, DisputeLetter, Invoice } from "./types";

const base =
  import.meta.env.VITE_API_URL?.replace(/\/$/, "") ?? "";

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${base}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json() as Promise<T>;
}

export function getHealth() {
  return req<{ status: string; service: string }>("/health");
}

export function listInvoices() {
  return req<Invoice[]>("/api/v1/invoices");
}

export function getInvoiceAudits(invoiceId: number) {
  return req<AuditRun[]>(`/api/v1/invoices/${invoiceId}/audits`);
}

export function auditInvoice(invoiceId: number) {
  return req<AuditRun>(`/api/v1/invoices/${invoiceId}/audit`, { method: "POST" });
}

export type InvoiceCreatePayload = Omit<Invoice, "id" | "status" | "uploaded_at">;

export function createInvoice(payload: InvoiceCreatePayload) {
  return req<Invoice>("/api/v1/invoices", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function generateDispute(auditRunId: number) {
  return req<DisputeLetter>(`/api/v1/audits/${auditRunId}/dispute-letter`, {
    method: "POST",
  });
}

export function listContractRates() {
  return req<ContractRate[]>("/api/v1/contracts/rates");
}