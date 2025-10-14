import * as XLSX from "xlsx";

/**
 * Extract data from Excel buffer and convert to JSON
 * @param buffer Excel file buffer
 * @returns Array of row objects from first sheet
 */
export function extractExcelData(buffer: Buffer): any[] {
  try {
    const workbook = XLSX.read(buffer, { type: "buffer" });
    const firstSheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[firstSheetName];
    return XLSX.utils.sheet_to_json(worksheet);
  } catch (error) {
    console.error("Excel extraction error:", error);
    throw new Error(`Failed to extract data from Excel: ${error}`);
  }
}

/**
 * Extract data from all sheets in Excel file
 * @param buffer Excel file buffer
 * @returns Object with sheet names as keys and data arrays as values
 */
export function extractAllExcelSheets(buffer: Buffer): {
  [sheetName: string]: any[];
} {
  try {
    const workbook = XLSX.read(buffer, { type: "buffer" });
    const result: { [sheetName: string]: any[] } = {};

    for (const sheetName of workbook.SheetNames) {
      const worksheet = workbook.Sheets[sheetName];
      result[sheetName] = XLSX.utils.sheet_to_json(worksheet);
    }

    return result;
  } catch (error) {
    console.error("Excel all sheets extraction error:", error);
    throw new Error(`Failed to extract all sheets from Excel: ${error}`);
  }
}

/**
 * Extract Excel data as text (for AI processing)
 * @param buffer Excel file buffer
 * @returns Formatted text representation of Excel data
 */
export function extractExcelAsText(buffer: Buffer): string {
  try {
    const workbook = XLSX.read(buffer, { type: "buffer" });
    const firstSheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[firstSheetName];

    // Convert to CSV format for better text representation
    const csv = XLSX.utils.sheet_to_csv(worksheet);

    // Format as structured text
    const lines = csv.split("\n");
    if (lines.length === 0) return "";

    // Format as TABLE similar to the HTML table parser
    const header = lines[0];
    const rows = lines.slice(1).filter((line) => line.trim().length > 0);

    const formatted = [
      "TABLE:",
      `HEADER: ${header.split(",").join(" | ")}`,
      ...rows.map((row) => `ROW: ${row.split(",").join(" | ")}`),
    ];

    return formatted.join("\n");
  } catch (error) {
    console.error("Excel to text conversion error:", error);
    throw new Error(`Failed to convert Excel to text: ${error}`);
  }
}

/**
 * Extract Excel with metadata
 * @param buffer Excel file buffer
 * @returns Object with data and metadata
 */
export function extractExcelWithMetadata(buffer: Buffer): {
  data: any[];
  metadata: {
    sheetCount: number;
    sheetNames: string[];
    rowCount: number;
  };
} {
  try {
    const workbook = XLSX.read(buffer, { type: "buffer" });
    const firstSheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[firstSheetName];
    const data = XLSX.utils.sheet_to_json(worksheet);

    return {
      data,
      metadata: {
        sheetCount: workbook.SheetNames.length,
        sheetNames: workbook.SheetNames,
        rowCount: data.length,
      },
    };
  } catch (error) {
    console.error("Excel extraction with metadata error:", error);
    throw new Error(`Failed to extract Excel with metadata: ${error}`);
  }
}

