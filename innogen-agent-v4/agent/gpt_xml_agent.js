import fs from "fs";
import path from "path";

const MAX_RETRIES = 3;
const GPT_URL = "https://chat.openai.com/";

export async function getXMLFromGPT(page, problem) {
  const promptTemplate = fs.readFileSync(
    path.join("prompts", "gpt_xml_prompt.txt"),
    "utf-8"
  );

  const prompt = promptTemplate.replace(
    "<<<PROBLEM_DESCRIPTION>>>",
    problem.description
  );

  let lastError = null;

  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    try {
      console.log(
        `🧠 GPT XML generation attempt ${attempt}/${MAX_RETRIES} for ${problem.problem_id}`
      );

      await sendPromptSafely(page, prompt);

      const result = await waitForXMLResponse(page);

      if (result.type === "xml") {
        const xml = extractBlocklyXML(result.text);

        if (!xml) {
          throw new Error(
            "Failed to extract Blockly XML from ChatGPT response"
          );
        }

        console.log("🧪 Extracted Blockly XML:\n", xml);

        return xml;
      }

      throw new Error(`Retryable GPT failure: ${result.type}`);
    } catch (err) {
      lastError = err;
      console.warn(`⚠️ GPT attempt ${attempt} failed: ${err.message}`);
      await page.waitForTimeout(1500);
    }
  }

  return lastError?.message?.includes("not_expressible")
    ? `<error>not_expressible</error>`
    : `<error>gpt_failed_after_retries: ${lastError?.message}</error>`;
}

/* ---------------- CORE HELPERS ---------------- */

async function sendPromptSafely(page, prompt) {
  await waitForAnyChatInput(page);

  // const inputSelector = getInputSelector();
  // Focus the REAL ChatGPT input from inside the page
  await page.evaluate(() => {
    const el =
      document.querySelector('div[contenteditable="true"]') ||
      document.querySelector('[data-testid="prompt-textarea"]');

    if (!el) {
      throw new Error("ChatGPT input element not found");
    }

    el.focus();
  });

  // Clear input
  await page.keyboard.down("Control");
  await page.keyboard.press("A");
  await page.keyboard.up("Control");
  await page.keyboard.press("Backspace");

  // ✅ PASTE FULL PROMPT AT ONCE
  await page.evaluate((text) => navigator.clipboard.writeText(text), prompt);

  await page.keyboard.down("Control");
  await page.keyboard.press("V");
  await page.keyboard.up("Control");

  await page.waitForTimeout(200);

  // Send
  await page.keyboard.press("Enter");

  await waitForUserMessageEcho(page, prompt);
}

async function waitForAnyChatInput(page) {
  await page.waitForFunction(
    () => {
      return (
        document.querySelector('div[contenteditable="true"]') ||
        document.querySelector('textarea[name="prompt-textarea"]') ||
        document.querySelector('[data-testid="prompt-textarea"]')
      );
    },
    { timeout: 60000 }
  );
}

/* ---------------- RESPONSE HANDLING ---------------- */

async function waitForUserMessageEcho(page, prompt) {
  const short = prompt.slice(0, 20);

  await page.waitForFunction(
    (text) => {
      return Array.from(
        document.querySelectorAll('div[data-message-author-role="user"]')
      ).some((el) => el.innerText.includes(text));
    },
    short,
    { timeout: 15000 }
  );
}

async function waitForXMLResponse(page, timeoutMs = 45000) {
  const start = Date.now();

  while (Date.now() - start < timeoutMs) {
    const text = await page.evaluate(() => {
      const nodes = document.querySelectorAll(
        'div[data-message-author-role="assistant"]'
      );
      const last = nodes[nodes.length - 1];
      return last ? last.textContent.trim() : "";
    });

    if (!text) {
      await page.waitForTimeout(500);
      continue;
    }

    // ✅ SUCCESS - wait for complete XML
    if (text.includes("<block") && text.includes("</xml>")) {
      return { type: "xml", text };
    }

    // 🔁 RETRYABLE ERROR
    if (text.includes("<error>not_expressible</error>")) {
      return { type: "not_expressible", text };
    }

    // ❌ INVALID RESPONSE (assistant replied, but useless)
    if (text.length > 20) {
      return { type: "invalid", text };
    }

    await page.waitForTimeout(500);
  }

  return { type: "timeout", text: "" };
}

function extractBlocklyXML(text) {
  if (!text) return null;

  // Remove code fences if present
  text = text
    .replace(/```xml/g, "")
    .replace(/```/g, "")
    .trim();

  const start = text.indexOf("<block");
  if (start === -1) return null;

  // Blockly XML may contain multiple blocks
  // We wrap it safely if needed
  const xmlContent = text.slice(start).trim();

  return xmlContent;
}
