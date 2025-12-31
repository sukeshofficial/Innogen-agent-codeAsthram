import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ✅ CORRECT PATH (matches your folder)
const BLOCKS_DB_PATH = path.join(__dirname, "data", "normalized_blocks.json");

if (!fs.existsSync(BLOCKS_DB_PATH)) {
  throw new Error(`normalized_blocks.json not found at ${BLOCKS_DB_PATH}`);
}

const BLOCKS = JSON.parse(fs.readFileSync(BLOCKS_DB_PATH, "utf-8"));

// Convert array → map for O(1) lookup
const BLOCK_MAP = Object.fromEntries(BLOCKS.map((b) => [b.type, b]));

/**
 * Validate a block tree recursively
 */
export function validateTree(node, context = "root") {
  const errors = [];

  // ---- Rule 1: Block must exist ----
  const schema = BLOCK_MAP[node.type];
  if (!schema) {
    errors.push(`Unknown block type: ${node.type}`);
    return errors;
  }

  // ---- Rule 2: Validate fields ----
  const requiredFields = Object.keys(schema.fields || {});
  const providedFields = Object.keys(node.fields || {});

  for (const field of requiredFields) {
    if (!providedFields.includes(field)) {
      errors.push(`Missing field '${field}' in block '${node.type}'`);
    }
  }

  for (const field of providedFields) {
    if (!requiredFields.includes(field)) {
      errors.push(`Invalid field '${field}' in block '${node.type}'`);
    }
  }

  // ---- Rule 3: Validate value inputs (expressions) ----
  const requiredValues = Object.keys(schema.value_inputs || {});
  const providedValues = Object.keys(node.value_inputs || {});

  for (const input of requiredValues) {
    if (!providedValues.includes(input)) {
      errors.push(`Missing value input '${input}' in block '${node.type}'`);
    }
  }

  for (const input of providedValues) {
    if (!requiredValues.includes(input)) {
      errors.push(`Invalid value input '${input}' in block '${node.type}'`);
    } else {
      // Recurse into child
      const child = node.value_inputs[input];
      const childErrors = validateTree(child, "expression");
      errors.push(...childErrors);
    }
  }

  // ---- Rule 4: Validate statement inputs ----
  const requiredStatements = Object.keys(schema.statement_inputs || {});
  const providedStatements = Object.keys(node.statement_inputs || {});

  for (const stmt of requiredStatements) {
    if (!providedStatements.includes(stmt)) {
      errors.push(`Missing statement input '${stmt}' in block '${node.type}'`);
    }
  }

  for (const stmt of providedStatements) {
    if (!requiredStatements.includes(stmt)) {
      errors.push(`Invalid statement input '${stmt}' in block '${node.type}'`);
    } else {
      const child = node.statement_inputs[stmt];
      const childErrors = validateTree(child, "statement");
      errors.push(...childErrors);
    }
  }

  // ---- Rule 5: Expression / Statement mismatch ----
  if (context === "expression" && schema.kind === "statement") {
    errors.push(`Statement block '${node.type}' used in expression context`);
  }

  if (context === "statement" && schema.kind === "expression") {
    errors.push(`Expression block '${node.type}' used in statement context`);
  }

  // if (schema.kind === "expression" && tree.statement_inputs) {
  //   errors.push(
  //     `Expression block '${node.type}' cannot have statement inputs`
  //   );
  // }

  return errors;
}
