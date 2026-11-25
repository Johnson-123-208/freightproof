import { FormEvent, useState } from "react";
import { createInvoice, type InvoiceCreatePayload } from "../api";

interface Props {
  onCreated: () => void;
}

export function UploadPanel({ onCreated }: Props) {
  const [jsonMode, setJsonMode] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    setBusy(true);
    setMessage(null);
    try {
      if (jsonMode) {
        const raw = String(fd.get("json") ?? "");
        const parsed = JSON.parse(raw) as Record<string, string | number>;
        await createInvoice(parsed as InvoiceCreatePayload);
      } else {
        await createInvoice({
          invoice_number: String(fd.get("invoice_number")),
          carrier_name: String(fd.get("carrier_name")),
          ship_date: String(fd.get("ship_date")),
          origin_city: String(fd.get("origin_city")),
          origin_state: String(fd.get("origin_state")),
          dest_city: String(fd.get("dest_city")),
          dest_state: String(fd.get("dest_state")),
          miles: String(fd.get("miles")),
          billed_amount: String(fd.get("billed_amount")),
          fuel_surcharge: String(fd.get("fuel_surcharge") || "0"),
        });
      }
      setMessage("Invoice queued.");
      e.currentTarget.reset();
      onCreated();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="rounded-lg border border-steel-700 bg-steel-900/60">
      <div className="flex items-center justify-between border-b border-steel-700 px-4 py-3">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-steel-200">Upload invoice</h2>
        <button
          type="button"
          className="text-xs text-accent-light hover:underline"
          onClick={() => setJsonMode((v) => !v)}
        >
          {jsonMode ? "Form entry" : "Paste JSON"}
        </button>
      </div>
      <form onSubmit={onSubmit} className="space-y-3 p-4 text-sm">
        {jsonMode ? (
          <textarea
            name="json"
            rows={6}
            className="w-full rounded border border-steel-600 bg-steel-950 px-3 py-2 font-mono text-xs text-steel-100"
            placeholder='{"invoice_number":"...","carrier_name":"Continental Freight Lines",...}'
            required
          />
        ) : (
          <div className="grid gap-2 sm:grid-cols-2">
            <Field name="invoice_number" label="Invoice #" defaultValue="FLT-DEMO-001" />
            <Field name="carrier_name" label="Carrier" defaultValue="Continental Freight Lines" />
            <Field name="ship_date" label="Ship date" type="date" defaultValue="2024-06-15" />
            <Field name="miles" label="Miles" defaultValue="680" />
            <Field name="origin_city" label="Origin city" defaultValue="Dallas" />
            <Field name="origin_state" label="ST" defaultValue="TX" />
            <Field name="dest_city" label="Dest city" defaultValue="Chicago" />
            <Field name="dest_state" label="ST" defaultValue="IL" />
            <Field name="billed_amount" label="Billed total" defaultValue="2150.00" />
            <Field name="fuel_surcharge" label="Fuel line" defaultValue="185.00" />
          </div>
        )}
        <button
          type="submit"
          disabled={busy}
          className="w-full rounded border border-steel-500 bg-steel-800 py-2 text-xs font-semibold uppercase tracking-wide text-slate-100 hover:bg-steel-700 disabled:opacity-50"
        >
          {busy ? "Uploading…" : "Add to queue"}
        </button>
        {message && <p className="text-xs text-steel-300">{message}</p>}
      </form>
    </div>
  );
}

function Field({
  name,
  label,
  defaultValue,
  type = "text",
}: {
  name: string;
  label: string;
  defaultValue?: string;
  type?: string;
}) {
  return (
    <label className="block">
      <span className="text-[10px] uppercase text-steel-500">{label}</span>
      <input
        name={name}
        type={type}
        defaultValue={defaultValue}
        required
        className="mt-0.5 w-full rounded border border-steel-600 bg-steel-950 px-2 py-1.5 text-xs text-slate-100"
      />
    </label>
  );
}