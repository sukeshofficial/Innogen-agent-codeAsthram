export function validateBlocks(xml, normalizedBlocks) {
  const allowed = new Set(
    JSON.parse(normalizedBlocks).map(b => b.type)
  );

  const regex = /type="([^"]+)"/g;
  let match;

  while ((match = regex.exec(xml)) !== null) {
    const blockType = match[1];
    if (!allowed.has(blockType)) {
      return {
        error: `unsupported_block_detected: ${blockType}`
      };
    }
  }

  return { ok: true };
}
