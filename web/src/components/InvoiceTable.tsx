import type { Invoice } from "../types";

interface Props {
  invoices: Invoice[];
  selectedId: number | null;
  onSelect: (id: number) => void;
}

function formatMoney(value: string) {
  const n = Number(value);
  return Number.isFinite(n) ? `$${n.toLocaleString("en-US", { minimumFractionDigits: 2 })}` : value;
}

function verdictBadge(status: string, invoice: Invoice) {
  if (status === "audited") {
    return (
      <span className="rounded bg-amber-950/50 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-amber-200 border border-amber-900/40">
        audited
      </span>
    );
  }
  return (
    <span className="rounded bg-steel-800 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-steel-300 border border-steel-600">
      {invoice.status}
    </span>
  );
}

export function InvoiceTable({ invoices, selectedId, onSelect }: Props) {
  if (!invoices.length) {
    return <p className="px-4 py-8 text-center text-sm text-steel-400">No invoices yet.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-steel-700 text-xs uppercase tracking-wide text-steel-400">
            <th className="px-4 py-2 font-medium">Invoice</th>
            <th className="px-4 py-2 font-medium">Lane</th>
            <th className="px-4 py-2 font-medium text-right">Billed</th>
            <th className="px-4 py-2 font-medium">Status</th>
          </tr>
        </thead>
        <tbody>
          {invoices.map((inv) => {
            const active = inv.id === selectedId;
            return (
              <tr
                key={inv.id}
                className={`cursor-pointer border-b border-steel-800/80 transition-colors ${
                  active ? "bg-accent-muted/40" : "hover:bg-steel-800/50"
                }`}
                onClick={() => onSelect(inv.id)}
              >
                <td className="px-4 py-3 font-mono text-xs text-slate-100">{inv.invoice_number}</td>
                <td className="px-4 py-3 text-steel-300">
                  {inv.origin_city}, {inv.origin_state} → {inv.dest_city}, {inv.dest_state}
                </td>
                <td className="px-4 py-3 text-right font-mono text-slate-100">
                  {formatMoney(inv.billed_amount)}
                </td>
                <td className="px-4 py-3">{verdictBadge(inv.status, inv)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}