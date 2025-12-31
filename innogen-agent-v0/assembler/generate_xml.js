// import fs from "fs";
// import { buildBlockXML } from "./xml_builder.js";

// // --------------------
// // Read validated block tree from Python output
// // --------------------
// const blockTree = JSON.parse(
//   fs.readFileSync("../agent/planner/output/block_tree.json", "utf-8")
// );

// // --------------------
// // Generate XML body
// // --------------------
// const xmlBody = buildBlockXML(blockTree);

// // --------------------
// // Wrap with Blockly root XML
// // --------------------
// const finalXML = `
// <xml xmlns="https://developers.google.com/blockly/xml">
//   ${xmlBody}
// </xml>
// `.trim();

// // --------------------
// // Save XML
// // --------------------
// // fs.mkdirSync("./output", { recursive: true });
// fs.writeFileSync("./output/program.xml", finalXML, "utf-8");

// console.log("✅ XML generated: assembler/output/program.xml");

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { buildBlockXML } from "./xml_builder.js";

// --------------------
// Resolve paths safely
// --------------------
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const BLOCK_TREE_PATH = path.resolve(
  __dirname,
  "../agent/planner/output/block_tree.json"
);

const OUTPUT_DIR = path.resolve(__dirname, "output");
const OUTPUT_XML = path.join(OUTPUT_DIR, "program.xml");

// --------------------
// Read validated block tree
// --------------------
if (!fs.existsSync(BLOCK_TREE_PATH)) {
  console.error("❌ block_tree.json not found. Planner may have failed.");
  process.exit(1);
}

const blockTree = JSON.parse(fs.readFileSync(BLOCK_TREE_PATH, "utf-8"));

// --------------------
// Generate XML body
// --------------------
const xmlBody = buildBlockXML(blockTree);

// --------------------
// Wrap with Blockly root XML
// --------------------
const finalXML = `
<xml xmlns="https://developers.google.com/blockly/xml">
  ${xmlBody}
</xml>
`.trim();

// --------------------
// Save XML
// --------------------
fs.mkdirSync(OUTPUT_DIR, { recursive: true });
fs.writeFileSync(OUTPUT_XML, finalXML, "utf-8");

console.log("✅ XML generated:", OUTPUT_XML);
