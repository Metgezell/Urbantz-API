// Environment variable loader - works with or without .env file
function loadEnv(): Record<string, string> {
  // Use globalThis to access environment variables
  const globalEnv = (globalThis as any).process?.env || {};
  return globalEnv;
}

export type UrbantzConfig = {
  baseUrl: string;
  apiKey: string;
};

export type Address = {
  line1: string;
  postalCode?: string;
  city?: string;
  country?: string;
  contactName?: string;
  contactPhone?: string;
  contactEmail?: string;
};

export type Item = {
  sku?: string;
  description?: string;
  quantity?: number;
  weightKg?: number;
  volumeL?: number;
  tempClass?: "ambient" | "chilled" | "frozen";
};

export type AnnounceTaskPayload = {
  customerRef: string;
  pickupAddress?: Address | null;
  deliveryAddress: Address;
  serviceDate: string;            // YYYY-MM-DD
  timeWindowStart?: string | null; // HH:MM
  timeWindowEnd?: string | null;   // HH:MM
  items?: Item[];
  notes?: string | null;
};

export function getEnvConfig(): UrbantzConfig {
  const env = loadEnv();
  const baseUrl = env.URBANTZ_BASE_URL || "https://api.urbantz.com";
  const apiKey = env.URBANTZ_API_KEY;
  if (!apiKey) {
    throw new Error("URBANTZ_API_KEY ontbreekt. Zet deze in .env");
  }
  return { baseUrl, apiKey };
}

function assertIsoDate(d?: string) {
  if (!d) return;
  if (!/^\d{4}-\d{2}-\d{2}$/.test(d)) {
    throw new Error(`serviceDate moet YYYY-MM-DD zijn, kreeg: ${d}`);
  }
}

function assertIsoTime(t?: string | null) {
  if (!t) return;
  if (!/^\d{2}:\d{2}$/.test(t)) {
    throw new Error(`Time moet HH:MM zijn, kreeg: ${t}`);
  }
}

export async function announceTask(
  payload: AnnounceTaskPayload,
  cfg?: Partial<UrbantzConfig>
) {
  const { baseUrl, apiKey } = { ...getEnvConfig(), ...cfg };

  // minimale checks
  if (!payload.customerRef) throw new Error("customerRef is verplicht");
  if (!payload.deliveryAddress?.line1) throw new Error("deliveryAddress.line1 is verplicht");
  assertIsoDate(payload.serviceDate);
  assertIsoTime(payload.timeWindowStart);
  assertIsoTime(payload.timeWindowEnd);

  const res = await fetch(`${baseUrl}/v2/announce`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": apiKey,
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Urbantz ${res.status}: ${text}`);
  }
  return res.json();
}
