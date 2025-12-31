import path from "path";

/**
 * Uploads normalized_blocks.json to ChatGPT
 * and waits until the upload is fully ingested.
 */
export async function uploadBlockCatalog(page) {
  console.log("📎 Uploading normalized_blocks.json to ChatGPT...");

  const fileInputs = await page.$$('input[type="file"]');

  if (!fileInputs.length) {
    throw new Error("No file input found on ChatGPT page");
  }

  const filePath = path.resolve("data", "normalized_blocks.json");

  // Attach file
  await fileInputs[0].setInputFiles(filePath);

  // 1️⃣ Wait until filename appears in UI
  await page.waitForFunction(
    () => {
      return Array.from(document.querySelectorAll("*"))
        .some(el => el.textContent?.includes("normalized_blocks.json"));
    },
    { timeout: 20000 }
  );

  // 2️⃣ Wait until upload spinner / progress disappears
  await page.waitForFunction(
    () => {
      return !Array.from(document.querySelectorAll("*"))
        .some(el =>
          el.textContent?.toLowerCase().includes("uploading")
        );
    },
    { timeout: 20000 }
  );

  // 3️⃣ Small safety delay for ingestion
  await page.waitForTimeout(500);

  console.log("✅ Block catalog uploaded and ingested");
}
