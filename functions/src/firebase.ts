import * as admin from "firebase-admin";

// Initialize Firebase Admin
admin.initializeApp();

// Firestore database instance
export const db = admin.firestore();

// Storage bucket instance
export const storage = admin.storage();

// Firestore collections
export const collections = {
  deliveries: "deliveries",
  trainingSamples: "trainingSamples",
  extractionLogs: "extractionLogs",
};

// Delivery interface
export interface Delivery {
  id?: string;
  customerRef: string;
  deliveryAddress: {
    line1: string;
    contactName: string;
    contactPhone: string;
  };
  serviceDate: string;
  timeWindowStart: string;
  timeWindowEnd: string;
  items: Array<{
    description: string;
    quantity: number;
    tempClass: string;
  }>;
  notes?: string;
  priority?: string;
  status: "draft" | "validated" | "exported";
  sourceType: "pdf" | "excel" | "email" | "text";
  createdAt: admin.firestore.Timestamp;
  updatedAt: admin.firestore.Timestamp;
}

// Training sample interface
export interface TrainingSample {
  id?: string;
  originalExtraction: object;
  correctedData: object;
  documentType: string;
  userId: string;
  createdAt: admin.firestore.Timestamp;
}

// Extraction log interface
export interface ExtractionLog {
  id?: string;
  inputText: string;
  extractedData: object;
  confidence: number;
  model: string;
  timestamp: admin.firestore.Timestamp;
}

// Save delivery to Firestore
export async function saveDelivery(
  data: Omit<Delivery, "id" | "createdAt" | "updatedAt">
): Promise<string> {
  const deliveryRef = await db.collection(collections.deliveries).add({
    ...data,
    createdAt: admin.firestore.FieldValue.serverTimestamp(),
    updatedAt: admin.firestore.FieldValue.serverTimestamp(),
  });
  return deliveryRef.id;
}

// Update delivery
export async function updateDelivery(
  id: string,
  data: Partial<Delivery>
): Promise<void> {
  await db
    .collection(collections.deliveries)
    .doc(id)
    .update({
      ...data,
      updatedAt: admin.firestore.FieldValue.serverTimestamp(),
    });
}

// Get delivery by ID
export async function getDelivery(id: string): Promise<Delivery | null> {
  const doc = await db.collection(collections.deliveries).doc(id).get();
  if (!doc.exists) {
    return null;
  }
  return { id: doc.id, ...doc.data() } as Delivery;
}

// Get deliveries by status
export async function getDeliveriesByStatus(
  status: string
): Promise<Delivery[]> {
  const snapshot = await db
    .collection(collections.deliveries)
    .where("status", "==", status)
    .orderBy("createdAt", "desc")
    .get();

  return snapshot.docs.map((doc) => ({
    id: doc.id,
    ...doc.data(),
  })) as Delivery[];
}

// Save training sample
export async function saveTrainingSample(
  data: Omit<TrainingSample, "id" | "createdAt">
): Promise<string> {
  const sampleRef = await db.collection(collections.trainingSamples).add({
    ...data,
    createdAt: admin.firestore.FieldValue.serverTimestamp(),
  });
  return sampleRef.id;
}

// Save extraction log
export async function saveExtractionLog(
  data: Omit<ExtractionLog, "id" | "timestamp">
): Promise<string> {
  const logRef = await db.collection(collections.extractionLogs).add({
    ...data,
    timestamp: admin.firestore.FieldValue.serverTimestamp(),
  });
  return logRef.id;
}

// Get multiple deliveries by IDs
export async function getDeliveriesByIds(ids: string[]): Promise<Delivery[]> {
  if (ids.length === 0) return [];

  const deliveries: Delivery[] = [];
  for (const id of ids) {
    const delivery = await getDelivery(id);
    if (delivery) {
      deliveries.push(delivery);
    }
  }
  return deliveries;
}

// Batch update delivery statuses
export async function batchUpdateDeliveryStatus(
  ids: string[],
  status: "draft" | "validated" | "exported"
): Promise<void> {
  const batch = db.batch();
  for (const id of ids) {
    const ref = db.collection(collections.deliveries).doc(id);
    batch.update(ref, {
      status,
      updatedAt: admin.firestore.FieldValue.serverTimestamp(),
    });
  }
  await batch.commit();
}

