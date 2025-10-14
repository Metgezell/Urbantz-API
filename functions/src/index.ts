import * as functions from "firebase-functions";
import {
  db,
  saveDelivery,
  saveTrainingSample,
  saveExtractionLog,
  getDeliveriesByIds,
  batchUpdateDeliveryStatus,
} from "./firebase";
import { extractPdfWithMetadata } from "./extractors/pdf";
import { extractExcelAsText } from "./extractors/excel";
import { extractEmailAsText } from "./extractors/email";
import { extractWithClaude } from "./ai/genkit";

/**
 * Analyze uploaded file or text and extract delivery information
 * Callable function that accepts file data or text
 */
export const analyzeFile = functions.https.onCall(async (data, context) => {
  try {
    const { fileType, text, fileBuffer, fileName } = data;

    if (!text && !fileBuffer) {
      throw new functions.https.HttpsError(
        "invalid-argument",
        "Either text or fileBuffer must be provided"
      );
    }

    let extractedText = text || "";
    let metadata: any = {};

    // Extract text based on file type
    if (fileBuffer) {
      const buffer = Buffer.from(fileBuffer, "base64");

      switch (fileType) {
        case "pdf":
          const pdfResult = await extractPdfWithMetadata(buffer);
          extractedText = pdfResult.text;
          metadata = pdfResult.metadata;
          break;

        case "excel":
        case "xlsx":
        case "xls":
          extractedText = extractExcelAsText(buffer);
          break;

        case "email":
        case "eml":
          extractedText = await extractEmailAsText(buffer.toString());
          break;

        default:
          // Assume text file
          extractedText = buffer.toString("utf-8");
      }
    }

    console.log(`🔍 Analyzing ${fileType || "text"}: ${fileName || "unnamed"}`);

    // Use Claude AI to extract deliveries
    const anthropicApiKey = process.env.ANTHROPIC_API_KEY;
    if (!anthropicApiKey) {
      throw new functions.https.HttpsError(
        "failed-precondition",
        "ANTHROPIC_API_KEY not configured"
      );
    }

    const deliveries = await extractWithClaude(extractedText, anthropicApiKey);

    // Save extraction log
    await saveExtractionLog({
      inputText: extractedText.substring(0, 1000), // Limit stored text
      extractedData: deliveries,
      confidence: deliveries.length > 0 ? 85 : 60,
      model: "claude-3-5-sonnet-20241022",
    });

    // Save deliveries to Firestore
    const deliveryIds: string[] = [];
    for (const delivery of deliveries) {
      const id = await saveDelivery({
        ...delivery,
        status: "draft",
        sourceType: fileType || "text",
      });
      deliveryIds.push(id);
    }

    console.log(
      `✅ Extracted ${deliveries.length} deliveries, saved to Firestore`
    );

    return {
      success: true,
      deliveries,
      deliveryIds,
      deliveryCount: deliveries.length,
      confidence: deliveries.length > 0 ? 85 : 60,
      metadata,
      extractedText: extractedText.substring(0, 500), // Return preview
    };
  } catch (error: any) {
    console.error("analyzeFile error:", error);
    throw new functions.https.HttpsError(
      "internal",
      error.message || "Analysis failed"
    );
  }
});

/**
 * Save correction/training data
 * Callable function to store user corrections for model improvement
 */
export const saveCorrection = functions.https.onCall(async (data, context) => {
  try {
    const { originalExtraction, correctedData, documentType } = data;

    if (!originalExtraction || !correctedData) {
      throw new functions.https.HttpsError(
        "invalid-argument",
        "originalExtraction and correctedData are required"
      );
    }

    // Get user ID from context (if authenticated)
    const userId = context.auth?.uid || "anonymous";

    // Save training sample
    const sampleId = await saveTrainingSample({
      originalExtraction,
      correctedData,
      documentType: documentType || "unknown",
      userId,
    });

    console.log(`💾 Saved training sample: ${sampleId}`);

    return {
      success: true,
      sampleId,
      message: "Correction saved successfully",
    };
  } catch (error: any) {
    console.error("saveCorrection error:", error);
    throw new functions.https.HttpsError(
      "internal",
      error.message || "Failed to save correction"
    );
  }
});

/**
 * Export deliveries to Urbantz
 * Callable function to send validated deliveries to Urbantz API
 */
export const exportToUrbantz = functions.https.onCall(async (data, context) => {
  try {
    const { deliveryIds } = data;

    if (!Array.isArray(deliveryIds) || deliveryIds.length === 0) {
      throw new functions.https.HttpsError(
        "invalid-argument",
        "deliveryIds array is required"
      );
    }

    console.log(`📦 Exporting ${deliveryIds.length} deliveries to Urbantz...`);

    // Get deliveries from Firestore
    const deliveries = await getDeliveriesByIds(deliveryIds);

    if (deliveries.length === 0) {
      throw new functions.https.HttpsError(
        "not-found",
        "No deliveries found with provided IDs"
      );
    }

    // Get Urbantz API configuration
    const urbantzApiKey = process.env.URBANTZ_API_KEY;
    const urbantzBaseUrl =
      process.env.URBANTZ_BASE_URL || "https://api.urbantz.com";

    if (!urbantzApiKey) {
      throw new functions.https.HttpsError(
        "failed-precondition",
        "URBANTZ_API_KEY not configured"
      );
    }

    const results: any[] = [];
    const errors: any[] = [];

    // Export each delivery to Urbantz
    for (const delivery of deliveries) {
      try {
        // Validate required fields
        if (!delivery.customerRef || !delivery.deliveryAddress?.line1) {
          errors.push({
            deliveryId: delivery.id,
            customerRef: delivery.customerRef || "Unknown",
            error: "Missing required fields: customerRef or deliveryAddress",
          });
          continue;
        }

        // Create Urbantz task payload
        const urbantzPayload = {
          customerRef: delivery.customerRef,
          deliveryAddress: delivery.deliveryAddress,
          serviceDate: delivery.serviceDate,
          timeWindowStart: delivery.timeWindowStart,
          timeWindowEnd: delivery.timeWindowEnd,
          items: delivery.items || [
            { description: "Pakket", quantity: 1, tempClass: "ambient" },
          ],
          notes: delivery.notes || "",
          priority: delivery.priority || "normal",
        };

        // Call Urbantz API
        const response = await fetch(`${urbantzBaseUrl}/tasks`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${urbantzApiKey}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(urbantzPayload),
        });

        if (response.ok) {
          const result: any = await response.json();
          results.push({
            success: true,
            deliveryId: delivery.id,
            customerRef: delivery.customerRef,
            urbantzTaskId: result.taskId || result.id,
            message: "Task created successfully",
          });
        } else {
          const errorText = await response.text();
          errors.push({
            deliveryId: delivery.id,
            customerRef: delivery.customerRef,
            error: `Urbantz API error: ${response.status} - ${errorText}`,
          });
        }
      } catch (error: any) {
        errors.push({
          deliveryId: delivery.id,
          customerRef: delivery.customerRef || "Unknown",
          error: error.message,
        });
      }
    }

    // Update status of successfully exported deliveries
    const successfulIds = results.map((r) => r.deliveryId);
    if (successfulIds.length > 0) {
      await batchUpdateDeliveryStatus(successfulIds, "exported");
    }

    console.log(
      `✅ Export completed: ${results.length} successful, ${errors.length} failed`
    );

    return {
      success: true,
      totalDeliveries: deliveries.length,
      successful: results.length,
      failed: errors.length,
      results,
      errors,
    };
  } catch (error: any) {
    console.error("exportToUrbantz error:", error);
    throw new functions.https.HttpsError(
      "internal",
      error.message || "Export failed"
    );
  }
});

/**
 * Get deliveries by status
 * Callable function to retrieve deliveries filtered by status
 */
export const getDeliveries = functions.https.onCall(async (data, context) => {
  try {
    const { status, limit = 50 } = data;

    let query = db.collection("deliveries").orderBy("createdAt", "desc");

    if (status) {
      query = query.where("status", "==", status) as any;
    }

    const snapshot = await query.limit(limit).get();

    const deliveries = snapshot.docs.map((doc) => ({
      id: doc.id,
      ...doc.data(),
    }));

    return {
      success: true,
      deliveries,
      count: deliveries.length,
    };
  } catch (error: any) {
    console.error("getDeliveries error:", error);
    throw new functions.https.HttpsError(
      "internal",
      error.message || "Failed to get deliveries"
    );
  }
});

/**
 * Get training samples
 * Callable function to retrieve training data for analysis
 */
export const getTrainingSamples = functions.https.onCall(
  async (data, context) => {
    try {
      const { limit = 100 } = data;

      const snapshot = await db
        .collection("trainingSamples")
        .orderBy("createdAt", "desc")
        .limit(limit)
        .get();

      const samples = snapshot.docs.map((doc) => ({
        id: doc.id,
        ...doc.data(),
      }));

      return {
        success: true,
        samples,
        count: samples.length,
      };
    } catch (error: any) {
      console.error("getTrainingSamples error:", error);
      throw new functions.https.HttpsError(
        "internal",
        error.message || "Failed to get training samples"
      );
    }
  }
);

