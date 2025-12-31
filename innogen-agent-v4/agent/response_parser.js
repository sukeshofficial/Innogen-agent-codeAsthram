export function parseGPTResponse(raw) {
  if (!raw) {
    return { error: "empty_response" };
  }

  const trimmed = raw.trim();

  if (trimmed === "<error>not_expressible</error>") {
    return { error: "not_expressible" };
  }

  if (!trimmed.includes("<block")) {
    return { error: "no_block_xml_detected" };
  }

  if (
    trimmed.includes("```") ||
    trimmed.toLowerCase().includes("explanation") ||
    trimmed.toLowerCase().includes("here is")
  ) {
    return { error: "gpt_pollution_detected" };
  }

  return { xml: trimmed };
}
