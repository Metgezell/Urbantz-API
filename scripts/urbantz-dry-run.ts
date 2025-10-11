import { announceTask } from "../src/clients/urbantz";

async function main() {
  const payload = {
    customerRef: "TEST-REF-123",
    deliveryAddress: { 
      line1: "Rue de Test 10, 1000 Bruxelles", 
      contactName: "Test", 
      contactPhone: "+32 470 00 00 00" 
    },
    serviceDate: "2025-10-12",
    timeWindowStart: "09:00",
    timeWindowEnd: "12:00",
    items: [{ 
      description: "Box", 
      quantity: 1, 
      tempClass: "ambient" as const 
    }],
    notes: "Dry-run voorbeeld",
  };
  
  try {
    const out = await announceTask(payload);
    console.log("Urbantz response:", out);
  } catch (error) {
    console.error("Error calling Urbantz API:", error);
  }
}

main().catch((e) => {
  console.error(e);
  (globalThis as any).process.exit(1);
});
