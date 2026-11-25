import { useCallback, useEffect, useState } from "react";
import {
  auditInvoice,
  generateDispute,
  getHealth,
  getInvoiceAudits,
  listContractRates,
  listInvoices,
} from "./api";
import type { AuditRun, ContractRate, DisputeLetter, Invoice } from "./types";
import { InvoiceTable } from "./components/InvoiceTable";
import { AuditPanel } from "./components/AuditPanel";
import { UploadPanel } from "./components/UploadPanel";

function LogoMark() {
  return (
    <div
      className="flex h-10 w-10 items-center justify-center rounded border border-steel-600 bg-steel-800 text-xs font-bold tracking-tighter text-slate-100"
      aria-hidden
    >
      FP
    </div>
  );
}

export default function App() {
  const [apiOk, setApiOk] = useState<boolean | null>(null);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [rates, setRates] = useState<ContractRate[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [audit, setAudit] = useState<AuditRun | null>(null);
  const [dispute, setDispute] = useState<DisputeLetter | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setError(null);
    try {
      const [inv, r] = await Promise.all([listInvoices(), listContractRates()]);
      setInvoices(inv);
      setRates(r);
      if (inv.length && selectedId === null) {
        setSelectedId(inv[0].id);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load data");
    }
  }, [selectedId]);

  useEffect(() => {
    getHealth()
      .then(() => setApiOk(true))
      .catch(() => setApiOk(false));
    void refresh();
  }, [refresh]);

  useEffect(() => {
    if (selectedId === null) {
      setAudit(null);
      return;
    }
    void getInvoiceAudits(selectedId)
      .then((runs) => setAudit(runs[0] ?? null))
      .catch(() => setAudit(null));
    setDispute(null);
  }, [selectedId]);

  const selected = invoices.find((i) => i.id === selectedId) ?? null;

  async function handleRunAudit() {
    if (!selectedId) return;
    setLoading(true);
    setError(null);
    try {
      const run = await auditInvoice(selectedId);
      setAudit(run);
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Audit failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleDispute() {
    if (!audit) return;
    setLoading(true);
    try {
      const letter = await generateDispute(audit.id);
      setDispute(letter);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Dispute draft failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen">
      <header className="border-b border-steel-700 bg-steel-900/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4">
          <div className="flex items-center gap-3">
            <LogoMark />
            <p>
              <span className="text-lg font-semibold tracking-tight text-slate-100">FreightProof</span>
              <span className="mt-0.5 block text-xs text-steel-300">
                Every freight charge. Verified with evidence.
              </span>
            </p>
          </div>
          <div className="flex items-center gap-3 text-xs font-mono text-steel-300">
            <span
              className={`inline-flex items-center gap-1.5 rounded border px-2 py-1 ${
                apiOk === true
                  ? "border-emerald-800/50 bg-emerald-950/40 text-emerald-300"
                  : apiOk === false
                    ? "border-red-900/50 bg-red-950/30 text-red-300"
                    : "border-steel-600 bg-steel-800"
              }`}
            >
              <span className="h-1.5 w-1.5 rounded-full bg-current" />
              API {apiOk === true ? "8006" : apiOk === false ? "offline" : "…"}
            </span>
            <span className="hidden sm:inline text-steel-400">Deterministic audit engine</span>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8">
        {error && (
          <div className="mb-4 rounded border border-red-900/40 bg-red-950/20 px-4 py-3 text-sm text-red-200">
            {error}
          </div>
        )}

        <div className="grid gap-6 lg:grid-cols-[1fr_1.1fr]">
          <section className="space-y-6">
            <UploadPanel onCreated={refresh} />
            <div className="rounded-lg border border-steel-700 bg-steel-900/60">
              <div className="border-b border-steel-700 px-4 py-3">
                <h2 className="text-sm font-semibold uppercase tracking-wide text-steel-200">Invoice queue</h2>
              </div>
              <InvoiceTable
                invoices={invoices}
                selectedId={selectedId}
                onSelect={setSelectedId}
              />
            </div>
            <div className="rounded-lg border border-steel-700 bg-steel-900/40 p-4">
              <h3 className="text-xs font-semibold uppercase tracking-wide text-steel-300">Contract rates</h3>
              <ul className="mt-2 space-y-2 text-sm text-steel-200">
                {rates.map((r) => (
                  <li key={r.id} className="font-mono text-xs leading-relaxed text-steel-300">
                    {r.origin_city}, {r.origin_state} → {r.dest_city}, {r.dest_state}: ${r.rate_per_mile}/mi
                    <span className="text-steel-400"> · {r.clause_ref}</span>
                  </li>
                ))}
              </ul>
            </div>
          </section>

          <AuditPanel
            invoice={selected}
            audit={audit}
            dispute={dispute}
            loading={loading}
            onRunAudit={handleRunAudit}
            onDraftDispute={handleDispute}
          />
        </div>
      </main>

      <footer className="mt-12 border-t border-steel-800 py-6 text-center text-xs text-steel-500">
        Demo MVP · Money math is deterministic · LLM not used for calculations
      </footer>
    </div>
  );
}