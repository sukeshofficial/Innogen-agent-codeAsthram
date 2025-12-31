import fs from "fs";

/**
 * INPUT:
 *  ../scrapper/output/blocks_db.json
 *
 * OUTPUT:
 *  ../assembler/output/normalized_blocks.json
 */

const INPUT_PATH = "../scrapper/output/blocks_db.json";
const OUTPUT_PATH = "../assembler/output/normalized_blocks.json";

// ------------------------------
// 1️⃣ Load scraped blocks DB
// ------------------------------
const rawBlocks = JSON.parse(
  fs.readFileSync(INPUT_PATH, "utf-8")
);

// ------------------------------
// 2️⃣ Detect block kind SAFELY
// ------------------------------
function detectKindFromPython(python) {
  if (!python) return "unknown";

  const code = python.trim();

  const statementStarters = [
    "print",
    "for ",
    "while ",
    "if ",
    "def ",
    "class ",
    "return",
    "try",
    "with "
  ];

  for (const kw of statementStarters) {
    if (code.startsWith(kw)) return "statement";
  }

  return "expression";
}

// ------------------------------
// 3️⃣ Normalize a single block
// ------------------------------
function normalizeBlock(block) {
  const fieldSchema = {};
  const valueInputSchema = {};
  const statementInputSchema = {};

  for (const fieldName of block.fields || []) {
    fieldSchema[fieldName] = "<value>";
  }

  for (const valueName of block.value_inputs || []) {
    valueInputSchema[valueName] = "<expression>";
  }

  for (const stmtName of block.statement_inputs || []) {
    statementInputSchema[stmtName] = "<statement>";
  }

  let cleanedXML = block.xml_template || "";
  cleanedXML = cleanedXML.replace(
    /\sxmlns="https:\/\/developers\.google\.com\/blockly\/xml"/g,
    ""
  );

  return {
    type: block.type,
    category: block.category,
    module: block.module,

    // 🔴 recompute kind, do NOT trust scraper
    kind: detectKindFromPython(block.python_sample),

    fields: fieldSchema,
    value_inputs: valueInputSchema,
    statement_inputs: statementInputSchema,

    xml_template: cleanedXML,
    python_sample: block.python_sample?.trim() || ""
  };
}

// ------------------------------
// 4️⃣ Patch known grammar gaps
// ------------------------------
function patchKnownBlocks(block) {
  // text_print always needs TEXT input
  if (block.type === "text_print") {
    block.kind = "statement";
    block.value_inputs.TEXT = "<expression>";
  }

  // You can add more patches later here
  return block;
}

// ------------------------------
// 5️⃣ Normalize all blocks
// ------------------------------
const normalizedBlocks = rawBlocks
  .map(normalizeBlock)
  .map(patchKnownBlocks);

// ------------------------------
// 6️⃣ Write output
// ------------------------------
fs.mkdirSync("../assembler/output", { recursive: true });

fs.writeFileSync(
  OUTPUT_PATH,
  JSON.stringify(normalizedBlocks, null, 2),
  "utf-8"
);

console.log(
  `✅ normalized_blocks.json generated (${normalizedBlocks.length} blocks)`
);
