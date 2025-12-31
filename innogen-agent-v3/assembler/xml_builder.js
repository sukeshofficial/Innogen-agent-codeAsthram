/**
 * Recursively converts a validated block tree into Blockly XML
 * @param {Object} block
 * @returns {string}
 */
export function buildBlockXML(block) {
  if (!block || typeof block !== "object") {
    throw new Error("Invalid block node");
  }

  if (!block.type) {
    throw new Error("Block missing type");
  }

  let xml = `<block type="${block.type}">`;

  // Fields
  if (block.fields) {
    for (const [name, value] of Object.entries(block.fields)) {
      xml += `<field name="${name}">${String(value)}</field>`;
    }
  }

  // Value inputs (expressions)
  if (block.value_inputs) {
    for (const [name, child] of Object.entries(block.value_inputs)) {
      xml += `<value name="${name}">`;
      xml += buildBlockXML(child);
      xml += `</value>`;
    }
  }

  // Statement inputs
  if (block.statement_inputs) {
    for (const [name, child] of Object.entries(block.statement_inputs)) {
      xml += `<statement name="${name}">`;
      xml += buildBlockXML(child);
      xml += `</statement>`;
    }
  }

  // Next block (sequential execution)
  if (block.next) {
    xml += `<next>`;
    xml += buildBlockXML(block.next);
    xml += `</next>`;
  }

  xml += `</block>`;
  return xml;
}
