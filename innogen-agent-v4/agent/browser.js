import { chromium } from "playwright";

/**
 * Launches a persistent browser context for ChatGPT UI.
 * This preserves login state across runs.
 */
export async function launchBrowser() {
  const context = await chromium.launchPersistentContext(
    "./.gpt-session", // folder that stores cookies
    {
      headless: false, // MUST be false for first login
      viewport: { width: 1024, height: 768},
      args: ["--disable-blink-features=AutomationControlled"]
    }
  );

  const page = await context.newPage();
  return { context, page };
}
