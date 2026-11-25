export interface Invoice {
  id: number;
  invoice_number: string;
  carrier_name: string;
  ship_date: string;
  origin_city: string;
  origin_state: string;
  dest_city: string;
  dest_state: string;
  miles: string;
  billed_amount: string;
  fuel_surcharge: string;
  status: string;
  uploaded_at: string;
}

export interface Finding {
  id: number;
  rule_code: string;
  severity: string;
  title: string;
  description: string;
  expected_value: string;
  actual_value: string;
  evidence_source: string;
  evidence_excerpt: string;
  citation: string;
}

export interface AuditRun {
  id: number;
  invoice_id: number;
  run_at: string;
  expected_amount: string;
  variance_amount: string;
  verdict: string;
  findings: Finding[];
}

export interface DisputeLetter {
  audit_run_id: number;
  subject: string;
  body: string;
}

export interface ContractRate {
  id: number;
  origin_city: string;
  origin_state: string;
  dest_city: string;
  dest_state: string;
  rate_per_mile: string;
  min_charge: string;
  fuel_surcharge_pct: string;
  clause_ref: string;
}