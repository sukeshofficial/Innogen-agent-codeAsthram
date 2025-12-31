import fs from "fs";
import path from "path";
import { launchBrowser } from "./agent/browser.js";
import { getXMLFromGPT } from "./agent/gpt_xml_agent.js";
import { parseGPTResponse } from "./agent/response_parser.js";
import { validateBlocks } from "./agent/block_validator.js";
import { runXML } from "./runner/runner_execute.js";
import { uploadBlockCatalog  } from "./agent/gpt_file_uploader.js";

function waitForEnter() {
  return new Promise((resolve) => {
    process.stdin.resume();
    process.stdin.once("data", () => resolve());
  });
}

async function main() {
  const problems = JSON.parse(fs.readFileSync("problems.json"));
  const normalizedBlocks = fs.readFileSync(
    path.join("data", "normalized_blocks.json"),
    "utf-8"
  );

  const { context, page } = await launchBrowser();

  await page.goto("https://chat.openai.com/");
  console.log("⚠️ If not logged in, login to ChatGPT and press ENTER");
  await waitForEnter();

  await uploadBlockCatalog(page);

  for (const problem of problems.problems) {
    const outDir = path.join("outputs", `Problem_${problem.problem_id}`);
    fs.mkdirSync(outDir, { recursive: true });

    const raw = await getXMLFromGPT(page, problem);

    const parsed = parseGPTResponse(raw);
    if (parsed.error) {
      fs.writeFileSync(
        path.join(outDir, `${problem.problem_id}_bug.txt`),
        parsed.error
      );
      continue;
    }

    const valid = validateBlocks(parsed.xml, normalizedBlocks);
    if (valid.error) {
      fs.writeFileSync(
        path.join(outDir, `${problem.problem_id}_bug.txt`),
        valid.error
      );
      continue;
    }

    // const result = await runXML(parsed.xml);
    let result = { python: "", error: "" };

    try {
      result = await runXML(parsed.xml);
    } catch (err) {
      result.error = `Runner crashed: ${err.message}`;
    }

    fs.writeFileSync(
      path.join(outDir, `${problem.problem_id}.xml`),
      parsed.xml
    );

    fs.writeFileSync(
      path.join(outDir, `${problem.problem_id}.txt`),
      result.python || ""
    );

    fs.writeFileSync(
      path.join(outDir, `${problem.problem_id}_bug.txt`),
      result.error ? result.error : ""
    );
  }

  // Optional: keep browser open
  // await context.close();
}

main();
