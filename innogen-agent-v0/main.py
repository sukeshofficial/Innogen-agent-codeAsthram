import json
import subprocess
import shutil
from pathlib import Path

# ------------------------------
# CONFIG
# ------------------------------
TEAM_ID = "TEAM_ID0602"
ROLE = "TL"

ROOT = Path(__file__).parent
AGENT_DIR = ROOT / "agent"
ASSEMBLER_DIR = ROOT / "assembler"
SCRAPPER_DIR = ROOT / "scrapper"
SUBMISSIONS_DIR = ROOT / "submissions"

PLANNER_SCRIPT = AGENT_DIR / "planner" / "retry_loop.py"
GENERATE_XML_SCRIPT = ASSEMBLER_DIR / "generate_xml.js"
EXECUTE_XML_SCRIPT = SCRAPPER_DIR / "runner_execute.js"

BLOCK_TREE_PATH = AGENT_DIR / "planner" / "output" / "block_tree.json"
PROGRAM_XML_PATH = ASSEMBLER_DIR / "output" / "program.xml"

RESULT_XML = SCRAPPER_DIR / "output" / "result.xml"
RESULT_TXT = SCRAPPER_DIR / "output" / "result.txt"

# ------------------------------
# Helpers
# ------------------------------
def run(cmd, cwd=None):
    print(f"▶ Running: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)


def safe_copy(src, dst):
    if src.exists():
        shutil.copy(src, dst)


# ------------------------------
# Main Orchestrator
# ------------------------------
def main():
    problems_path = ROOT / "problems.json"

    if not problems_path.exists():
        raise FileNotFoundError("problems.json not found")

    with open(problems_path, "r", encoding="utf-8") as f:
        problems = json.load(f)

    SUBMISSIONS_DIR.mkdir(exist_ok=True)

    for problem in problems:
        pid = problem["problem_id"]
        description = problem["description"]

        print(f"\n==============================")
        print(f"🚀 Solving {pid}")
        print(f"==============================")

        # ------------------------------
        # 1️⃣ Planner (LLM + Retry)
        # ------------------------------
        run(
            ["python", str(PLANNER_SCRIPT), description],
            cwd=ROOT
        )

        if not BLOCK_TREE_PATH.exists():
            raise RuntimeError("Planner failed: block_tree.json missing")

        # ------------------------------
        # 2️⃣ Generate XML
        # ------------------------------
        run(
            ["node", str(GENERATE_XML_SCRIPT)],
            cwd=ASSEMBLER_DIR
        )

        if not PROGRAM_XML_PATH.exists():
            raise RuntimeError("XML generation failed")

        # ------------------------------
        # 3️⃣ Execute in CodeAsthram
        # ------------------------------
        run(
            ["node", str(EXECUTE_XML_SCRIPT)],
            cwd=SCRAPPER_DIR
        )

        # ------------------------------
        # 4️⃣ Create Submission Folder
        # ------------------------------
        problem_dir = SUBMISSIONS_DIR / pid
        problem_dir.mkdir(exist_ok=True)

        xml_name = f"{TEAM_ID}_{ROLE}_{pid}.xml"
        txt_name = f"{TEAM_ID}_{ROLE}_{pid}.txt"
        bug_name = f"{TEAM_ID}_{ROLE}_{pid}_bug.txt"

        safe_copy(PROGRAM_XML_PATH, problem_dir / xml_name)
        safe_copy(RESULT_TXT, problem_dir / txt_name)

        # Optional bug file
        if RESULT_XML.exists():
            safe_copy(RESULT_XML, problem_dir / bug_name)

        print(f"✅ {pid} completed")

    print("\n🏁 ALL PROBLEMS SOLVED")


# ------------------------------
if __name__ == "__main__":
    main()
