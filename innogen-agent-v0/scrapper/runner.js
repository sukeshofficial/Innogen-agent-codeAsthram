import { chromium } from "playwright";
import fs from "fs";

const catalog = JSON.parse(
  fs.readFileSync("block_catalog.json", "utf-8")
);

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  await page.goto("https://hackpy.tarcin.in/");
  await page.waitForTimeout(5000);

  await page.addScriptTag({ path: "page_scrapper.js" });

  const results = [];

  for (const block of catalog) {
    const data = await page.evaluate(
      (block) => window.scrapeBlock(block),
      block
    );

    console.log("Scraped:", block.type);
    results.push(data);
  }

  fs.mkdirSync("output", { recursive: true });
  fs.writeFileSync(
    "output/blocks_db.json",
    JSON.stringify(results, null, 2)
  );

  await browser.close();
})();
