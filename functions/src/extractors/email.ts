import { simpleParser, ParsedMail, Attachment } from "mailparser";

/**
 * Extract email data from raw email string
 * @param raw Raw email content (RFC 822 format)
 * @returns Parsed email object
 */
export async function extractEmail(raw: string): Promise<ParsedMail> {
  try {
    const parsed = await simpleParser(raw);
    return parsed;
  } catch (error) {
    console.error("Email parsing error:", error);
    throw new Error(`Failed to parse email: ${error}`);
  }
}

/**
 * Extract email with formatted text output
 * @param raw Raw email content
 * @returns Object with structured email data
 */
export async function extractEmailData(raw: string): Promise<{
  subject: string | undefined;
  from: string | undefined;
  to: string | undefined;
  date: Date | undefined;
  text: string | undefined;
  html: string | undefined;
  attachments: Attachment[];
}> {
  try {
    const parsed = await simpleParser(raw);

    return {
      subject: parsed.subject,
      from: parsed.from?.text,
      to: Array.isArray(parsed.to) 
        ? parsed.to.map((addr) => addr.text).join(", ")
        : parsed.to?.text,
      date: parsed.date,
      text: parsed.text,
      html: parsed.html ? parsed.html.toString() : undefined,
      attachments: parsed.attachments,
    };
  } catch (error) {
    console.error("Email data extraction error:", error);
    throw new Error(`Failed to extract email data: ${error}`);
  }
}

/**
 * Extract email as formatted text for AI processing
 * @param raw Raw email content
 * @returns Formatted text representation
 */
export async function extractEmailAsText(raw: string): Promise<string> {
  try {
    const parsed = await simpleParser(raw);

    const parts: string[] = [];

    if (parsed.subject) {
      parts.push(`Subject: ${parsed.subject}`);
    }

    if (parsed.from) {
      parts.push(`From: ${parsed.from.text}`);
    }

    if (parsed.to) {
      const toText = Array.isArray(parsed.to)
        ? parsed.to.map((addr) => addr.text).join(", ")
        : parsed.to.text;
      parts.push(`To: ${toText}`);
    }

    if (parsed.date) {
      parts.push(`Date: ${parsed.date.toISOString()}`);
    }

    parts.push(""); // Empty line separator

    if (parsed.text) {
      parts.push(parsed.text);
    }

    if (parsed.attachments && parsed.attachments.length > 0) {
      parts.push("");
      parts.push("Attachments:");
      parsed.attachments.forEach((att) => {
        parts.push(`- ${att.filename} (${att.contentType})`);
      });
    }

    return parts.join("\n");
  } catch (error) {
    console.error("Email to text conversion error:", error);
    throw new Error(`Failed to convert email to text: ${error}`);
  }
}

/**
 * Extract attachments from email
 * @param raw Raw email content
 * @returns Array of attachment objects with content
 */
export async function extractEmailAttachments(raw: string): Promise<
  Array<{
    filename: string;
    contentType: string;
    size: number;
    content: Buffer;
  }>
> {
  try {
    const parsed = await simpleParser(raw);

    return parsed.attachments.map((att) => ({
      filename: att.filename || "unnamed",
      contentType: att.contentType,
      size: att.size,
      content: att.content,
    }));
  } catch (error) {
    console.error("Email attachments extraction error:", error);
    throw new Error(`Failed to extract email attachments: ${error}`);
  }
}

