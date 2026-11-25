import type { AuditRun, DisputeLetter, Invoice } from "../types";

interface Props {
  invoice: Invoice | null;
  audit: AuditRun | null;
  dispute: DisputeLetter | null;
  loading: boolean;
  onRunAudit: () => void;
  onDraftDispute: () => void;
}

function severityClass(severity: string) {
  switch (severity) {
    case "critical":
      return "border-red-900/50 bg-red-950/25 text-red-200";
    case "medium":
      return "border-amber-900/40 bg-amber-950/20 text-amber-100";
    default:
      return "border-steel-600 bg-steel-800/50 text-steel-200";
  }
}

function SummaryBanner({ audit, overcharge }: { audit: AuditRun; overcharge: boolean }) {
  return (
    <div
      className={`mx-4 mt-4 rounded border px-3 py-2 text-xs ${
        overcharge
          ? "border-red-900/50 bg-red-950/30 text-red-100"
          : "border-steel-600 bg-steel-800/40 text-steel-200"
      }`}
    >
      {overcharge
        ? `Overcharge of $${audit.variance_amount} vs contract (deterministic).`
        : `Verdict: ${audit.verdict}. Variance $${audit.variance_amount}.`}
    </div>
  );
}

function StatCard({
  label,
  value,
  highlight,
}: {
  label: string;
  value: string;
  highlight?: boolean;
}) {
  return (
    <div className="rounded border border-steel-700 bg-steel-950/50 p-2">
      <dt className="text-[10px] uppercase text-steel-500">{label}</dt>
      <dd className={`font-mono text-sm ${highlight ? "text-red-300" : "text-slate-100"}`}>{value}</dd>
    </div>
  );
}

function DisputeBlock({ dispute }: { dispute: DisputeLetter }) {
  return (
    <div className="rounded-lg border border-steel-700 bg-steel-900/80">
      <div className="border-b border-steel-700 px-4 py-3">
        <h3 className="text-sm font-semibold text-slate-100">Dispute letter draft</h3>
        <p className="font-mono text-xs text-steel-400">{dispute.subject}</p>
      </div>
      <pre className="max-h-80 overflow-auto whitespace-pre-wrap px-4 py-4 font-mono text-xs leading-relaxed text-steel-200">
        {dispute.body}
      </pre>
    </div>
  );
}

export function AuditPanel({
  invoice,
  audit,
  dispute,
  loading,
  onRunAudit,
  onDraftDispute,
}: Props) {
  if (!invoice) {
    return (
      <div className="rounded-lg border border-steel-700 bg-steel-900/60 p-8 text-center text-steel-400">
        Select an invoice to review findings.
      </div>
    );
  }

  const overcharge = audit !== null && Number(audit.variance_amount) > 0;

  return (
    <section className="space-y-4">
      <div className="rounded-lg border border-steel-700 bg-steel-900/60">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-steel-700 px-4 py-3">
          <div>
            <h2 className="text-sm font-semibold text-slate-100">Audit review</h2>
            <p className="font-mono text-xs text-steel-400">{invoice.invoice_number}</p>
          </div>
          <div className="flex gap-2">
            <button
              type="button"
              disabled={loading}
              onClick={onRunAudit}
              className="rounded border border-accent bg-accent px-3 py-1.5 text-xs font-medium text-slate-100 transition hover:bg-accent-light disabled:opacity-50"
            >
              {loading ? "Running…" : "Re-run audit"}
            </button>
            {audit && (
              <button
                type="button"
                disabled={loading}
                onClick={onDraftDispute}
                className="rounded border border-steel-500 bg-steel-800 px-3 py-1.5 text-xs font-medium text-steel-100 hover:bg-steel-700 disabled:opacity-50"
              >
                Draft dispute
              </button>
            )}
          </div>
        </div>

        {audit && <SummaryBanner audit={audit} overcharge={overcharge} />}

        {!audit && (
          <p className="px-4 py-6 text-sm text-steel-400">No audit on file. Run audit to compare against contract.</p>
        )}

        {audit && (
          <div className="space-y-3 px-4 py-4">
            <dl className="grid grid-cols-3 gap-3 text-xs">
              <StatCard label="Verdict" value={audit.verdict} highlight={overcharge} />
              <StatCard label="Expected" value={`$${audit.expected_amount}`} />
              <StatCard label="Variance" value={`$${audit.variance_amount}`} highlight={overcharge} />
            </dl>

            <h3 className="pt-2 text-xs font-semibold uppercase tracking-wide text-steel-300">Findings & evidence</h3>
            <ul className="space-y-3">
              {audit.findings.map((f) => (
                <li
                  key={f.id}
                  className={`rounded border px-3 py-3 text-sm ${severityClass(f.severity)}`}
                >
                  <p className="font-medium">{f.title}</p>
                  <p className="mt-1 text-xs opacity-90">{f.description}</p>
                  <p className="mt-2 font-mono text-[11px] leading-relaxed opacity-80">{f.evidence_excerpt}</p>
                  <p className="mt-2 text-[10px] uppercase tracking-wide text-steel-400">
                    Citation: {f.citation} · Source: {f.evidence_source}
                  </p>
                  <p className="mt-1 font-mono text-xs">
                    Expected {f.expected_value} · Actual {f.actual_value}
                  </p>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {dispute && <DisputeBlock dispute={dispute} />}
    </section>
  );
}