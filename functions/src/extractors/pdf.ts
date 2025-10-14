import { extractText } from "unpdf";

/**
 * Extract text from PDF buffer using unpdf
 * @param buffer PDF file buffer
 * @returns Extracted text content
 */
export async function extractPdfText(buffer: Buffer): Promise<string> {
  try {
    const result = await extractText(buffer);
    // unpdf returns an array of text strings, join them
    const text = Array.isArray(result.text) 
      ? result.text.join("\n") 
      : result.text;
    return text;
  } catch (error) {
    console.error("PDF extraction error:", error);
    throw new Error(`Failed to extract text from PDF: ${error}`);
  }
}

/**
 * Extract text from PDF with metadata
 * @param buffer PDF file buffer
 * @returns Object with text and metadata
 */
export async function extractPdfWithMetadata(buffer: Buffer): Promise<{
  text: string;
  metadata?: {
    pages?: number;
    title?: string;
    author?: string;
  };
}> {
  try {
    const result = await extractText(buffer, {
      mergePages: true,
    });

    // unpdf returns an array of text strings, join them
    const text = Array.isArray(result.text) 
      ? result.text.join("\n") 
      : result.text;

    return {
      text,
      metadata: {
        pages: result.totalPages,
      },
    };
  } catch (error) {
    console.error("PDF extraction with metadata error:", error);
    throw new Error(`Failed to extract PDF with metadata: ${error}`);
  }
}

