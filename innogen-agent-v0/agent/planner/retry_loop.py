# import json
# import subprocess
# from typing import Dict, List

# MAX_RETRIES = 3

# def export_tree(tree, path="./output/block_tree.json"):
#     with open(path, "w") as f:
#         json.dump(tree, f, indent=2)

# def call_planner(problem_text: str, repair_instruction: str = "") -> Dict:
#     result = subprocess.run(
#         ["python", "planner.py", problem_text],
#         input=repair_instruction,
#         capture_output=True,
#         text=True
#     )

#     if result.returncode != 0:
#         raise RuntimeError(result.stderr)

#     try:
#         return json.loads(result.stdout.strip())
#     except json.JSONDecodeError:
#         raise ValueError(
#             f"Planner returned invalid JSON:\n{result.stdout}"
#         )


# def validate_with_node(tree: Dict) -> List[str]:
#     result = subprocess.run(
#         ["node", "../validate_tree_cli.js"],
#         input=json.dumps(tree),
#         capture_output=True,
#         text=True
#     )

#     if not result.stdout.strip():
#         raise RuntimeError(
#             "Node validator returned empty output.\n"
#             f"STDERR:\n{result.stderr}"
#         )

#     try:
#         data = json.loads(result.stdout)
#     except json.JSONDecodeError:
#         raise RuntimeError(
#             "Node validator returned invalid JSON.\n"
#             f"STDOUT:\n{result.stdout}\n"
#             f"STDERR:\n{result.stderr}"
#         )

#     return data["errors"]



# def generate_valid_block_tree(problem_text: str) -> Dict:
#     last_errors: List[str] = []

#     for attempt in range(1, MAX_RETRIES + 1):
#         print(f"\n🔁 Planner attempt {attempt}")

#         repair_prompt = ""
#         if last_errors:
#             repair_prompt = (
#                 "The previous block tree was INVALID.\n\n"
#                 "Validator errors:\n"
#                 + "\n".join(f"- {e}" for e in last_errors)
#                 + "\n\nFix the block tree.\n"
#                 "Return ONLY the corrected block tree JSON.\n"
#                 "Do not explain anything."
#             )

#         tree = call_planner(problem_text, repair_prompt)
#         errors = validate_with_node(tree)

#         if not errors:
#             print("✅ Valid block tree generated")
#             return tree

#         print("❌ Validation errors:")
#         for e in errors:
#             print("  -", e)

#         last_errors = errors

#     raise RuntimeError(
#         "Failed to generate valid block tree.\n"
#         + "\n".join(last_errors)
#     )


# # tree = generate_valid_block_tree("A candidate qualifies only if written score is at least 60 interview score at least 15 and total does not exceed 100.")
# # export_tree(tree)
# -----------------------------------------------------------------------------------------------------------------------------------

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

MAX_RETRIES = 3

# ------------------------------
# Path Resolution (IMPORTANT)
# ------------------------------
BASE_DIR = Path(__file__).parent
PROJECT_ROOT = BASE_DIR.parent.parent

PLANNER_SCRIPT = BASE_DIR / "planner.py"
VALIDATOR_CLI = PROJECT_ROOT / "agent" / "validate_tree_cli.js"
OUTPUT_DIR = BASE_DIR / "output"
BLOCK_TREE_PATH = OUTPUT_DIR / "block_tree.json"


# ------------------------------
def export_tree(tree: Dict):
    OUTPUT_DIR.mkdir(exist_ok=True)
    with open(BLOCK_TREE_PATH, "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=2)

def extract_json(text: str) -> dict:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in planner output")

    json_str = text[start:end + 1]
    return json.loads(json_str)

last_tree = None

# ------------------------------
def call_planner(problem_text: str) -> Dict:
    try:
        result = subprocess.run(
            ["python", str(PLANNER_SCRIPT), problem_text],
            capture_output=True,
            text=True,
            # timeout=50
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("Planner timed out (LLM took too long)")
    
    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    try:
        return extract_json(result.stdout)
    except json.JSONDecodeError:
        raise ValueError(
            f"Planner returned invalid JSON:\n{result.stdout}"
        )


# ------------------------------
def validate_with_node(tree: Dict) -> List[str]:
    result = subprocess.run(
        ["node", str(VALIDATOR_CLI)],
        input=json.dumps(tree),
        capture_output=True,
        text=True
    )

    if not result.stdout.strip():
        raise RuntimeError(
            "Node validator returned empty output.\n"
            f"STDERR:\n{result.stderr}"
        )

    try:
        data = extract_json(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(
            "Node validator returned invalid JSON.\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )

    return data["errors"]


# ------------------------------
def generate_valid_block_tree(problem_text: str) -> Dict:
    last_errors: List[str] = []

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\n🔁 Planner attempt {attempt}")

        tree = call_planner(problem_text)
        last_tree = tree
        if isinstance(tree, dict) and tree.get("error") == "not_expressible":
            raise RuntimeError("Problem is not expressible with current block grammar")

        errors = validate_with_node(tree)

        if not errors:
            print("✅ Valid block tree generated")
            export_tree(tree)
            return tree

        print("❌ Validation errors:")
        for e in errors:
            print("  -", e)

        last_errors = errors

    raise RuntimeError(
        "Failed to generate valid block tree.\n"
        + "\n".join(last_errors)
    )


# ------------------------------
# CLI ENTRY (REQUIRED FOR main.py)
# ------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "missing_problem"}))
        sys.exit(1)

    problem_text = sys.argv[1]
    generate_valid_block_tree(problem_text)
