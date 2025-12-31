/**
 * xml_builder.js
 *
 * Converts a JSON block tree into Blockly XML.
 * Pure function. No side effects.
 */

export function buildBlockXML(node) {
  if (!node || !node.type) {
    throw new Error("Invalid block node");
  }

  let xml = `<block type="${node.type}">`;

  // --------------------
  // Fields
  // --------------------
  if (node.fields) {
    for (const [fieldName, fieldValue] of Object.entries(node.fields)) {
      xml += `<field name="${fieldName}">${escapeXML(
        String(fieldValue)
      )}</field>`;
    }
  }

  // --------------------
  // Value inputs (expressions)
  // --------------------
  if (node.value_inputs) {
    for (const [inputName, childNode] of Object.entries(
      node.value_inputs
    )) {
      xml += `<value name="${inputName}">`;
      xml += buildBlockXML(childNode);
      xml += `</value>`;
    }
  }

  // --------------------
  // Statement inputs (control blocks)
  // --------------------
  if (node.statement_inputs) {
    for (const [stmtName, stmtNode] of Object.entries(
      node.statement_inputs
    )) {
      xml += `<statement name="${stmtName}">`;
      xml += buildBlockXML(stmtNode);
      xml += `</statement>`;
    }
  }

  xml += `</block>`;
  return xml;
}

/**
 * Escape XML safely
 */
function escapeXML(value) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}
