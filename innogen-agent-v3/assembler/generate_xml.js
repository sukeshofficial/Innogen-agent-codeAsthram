import fs from "fs";
import path from "path";
import { buildBlockXML } from "./xml_builder.js";

// Input from Python compiler - block tree path passed as argument
const blockTreePath = process.argv[2];
const outputPath = process.argv[3] || "./output/program.xml";

const blockTree = JSON.parse(
  fs.readFileSync(blockTreePath, "utf-8")
);

// Build XML body
let xmlBody;
try {
  xmlBody = buildBlockXML(blockTree);
} catch (error) {
  console.error("Error building XML:", error.message);
  console.error("Block tree:", JSON.stringify(blockTree, null, 2));
  process.exit(1);
}

// Wrap with Blockly root
const finalXML = `
<xml xmlns="https://developers.google.com/blockly/xml">
${xmlBody}
</xml>
`.trim();

// Write output
fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, finalXML, "utf-8");

console.log(`✅ XML generated: ${outputPath}`);
