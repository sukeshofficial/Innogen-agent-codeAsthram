import { chromium } from "playwright";
import path from "path";

/**
 * Executes Blockly XML in CodeAsthram and returns Python code + errors
 * @param {string} xmlText
 * @returns {{ python: string, error: string }}
 */
export async function runXML(xmlText) {
  let browser;

  try {
    browser = await chromium.launch({
      headless: true // set false for debugging
    });

    const page = await browser.newPage();

    // 1️⃣ Open CodeAsthram
    await page.goto("https://hackpy.tarcin.in/", {
      waitUntil: "networkidle",
      timeout: 60000
    });

    // 2️⃣ Wait for Blockly to load
    await page.waitForSelector("svg.blocklySvg", {
      timeout: 30000
    });

    // 3️⃣ Inject helper (execute_xml.js)
    await page.addScriptTag({
      path: path.resolve("./runner/execute_xml.js")
    });

    // 4️⃣ Execute XML inside browser
    const result = await page.evaluate(
      xml => window.executeXML(xml),
      xmlText
    );

    if (result.status !== "success") {
      return {
        python: "",
        error: `Execution failed: ${result.status}\n${result.error || ""}`
      };
    }

    return {
      python: result.python || "",
      error: ""
    };

  } catch (err) {
    return {
      python: "",
      error: `Runner error: ${err.message}`
    };
  } finally {
    if (browser) await browser.close();
  }
}
