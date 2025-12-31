import fs from "fs";
import JSON5 from "json5";

// 1️⃣ Read raw file
let rawText = fs.readFileSync("./raw_j.txt", "utf8");

// 2️⃣ FIX JS-only boolean hacks
rawText = rawText
  .replace(/\b!0\b/g, "true")
  .replace(/\b!1\b/g, "false");

// 3️⃣ Parse safely
const data = JSON5.parse(rawText);

// 4️⃣ Normalize into block catalog
const catalog = [];

for (const category of data) {
  const categoryName = category.themeKey;

  for (const module of category.modules || []) {
    const moduleName = module.name;

    for (const block of module.blocks || []) {
      if (!block.type) continue;

      catalog.push({
        type: block.type,
        category: categoryName,
        module: moduleName,
      });
    }
  }
}

// 5️⃣ Write output
fs.writeFileSync(
  "./block_catalog.json",
  JSON.stringify(catalog, null, 2),
  "utf8"
);

console.log(`✅ block_catalog.json generated (${catalog.length} blocks)`);
