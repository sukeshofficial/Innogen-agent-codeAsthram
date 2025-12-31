/**
 * page_scrapper.js
 *
 * Runs INSIDE the Code Asthram webpage.
 * Requires Blockly + Python generator to be already loaded.
 *
 * Exposes:
 *   window.scrapeBlock(blockMeta)
 */

(function () {
  /**
   * Utility: clear Blockly workspace safely
   */
  function clearWorkspace(ws) {
    try {
      ws.clear();
    } catch (e) {
      console.warn("Workspace clear failed:", e);
    }
  }

  /**
   * Utility: detect block kind from generated Python
   */
  function detectKindFromPython(python) {
    const code = python.trim();

    // Explicit statement keywords
    const statementStarters = [
      "print",
      "for ",
      "while ",
      "if ",
      "def ",
      "class ",
      "return",
      "try",
      "with ",
    ];

    for (const kw of statementStarters) {
      if (code.startsWith(kw)) {
        return "statement";
      }
    }

    return "expression";
  }

  /**
   * Core scraper
   */
  window.scrapeBlock = async function ({ type, category, module }) {
    if (!window.Blockly || !window.Python) {
      return {
        type,
        category,
        module,
        error: "Blockly or Python generator not available",
      };
    }

    const ws = Blockly.getMainWorkspace();
    if (!ws) {
      return {
        type,
        category,
        module,
        error: "Main workspace not found",
      };
    }

    clearWorkspace(ws);

    // ---- Create block ----
    let block;
    try {
      block = ws.newBlock(type);
      block.initSvg();
      block.render();
    } catch (e) {
      return {
        type,
        category,
        module,
        error: "Block creation failed",
        details: String(e),
      };
    }

    // ---- Extract XML (canonical) ----
    let xmlText = "";
    try {
      const dom = Blockly.Xml.blockToDom(block, true);
      xmlText = Blockly.Xml.domToText(dom);
    } catch (e) {
      return {
        type,
        category,
        module,
        error: "XML extraction failed",
        details: String(e),
      };
    }

    // ---- Parse XML structure ----
    let fields = [];
    let valueInputs = [];
    let statementInputs = [];

    try {
      const parser = new DOMParser();
      const doc = parser.parseFromString(xmlText, "text/xml");

      fields = Array.from(doc.getElementsByTagName("field"))
        .map((f) => f.getAttribute("name"))
        .filter(Boolean);

      valueInputs = Array.from(doc.getElementsByTagName("value"))
        .map((v) => v.getAttribute("name"))
        .filter(Boolean);

      statementInputs = Array.from(doc.getElementsByTagName("statement"))
        .map((s) => s.getAttribute("name"))
        .filter(Boolean);
    } catch (e) {
      // Parsing failure should not kill the block
      console.warn("XML parsing issue for block:", type, e);
    }

    // ---- Generate Python ----
    let pythonSample = "";
    let kind = "unknown";

    try {
      pythonSample = Python.workspaceToCode(ws);
      kind = detectKindFromPython(pythonSample);
    } catch (e) {
      pythonSample = "";
      kind = "unknown";
    }

    // ---- Final payload ----
    return {
      type,
      category,
      module,
      kind,
      fields,
      value_inputs: valueInputs,
      statement_inputs: statementInputs,
      xml_template: xmlText,
      python_sample: pythonSample,
    };
  };
})();
