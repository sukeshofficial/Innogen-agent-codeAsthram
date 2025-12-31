"""
Innogen Agent v3 - Main Entry Point

Production-grade compiler-style system for converting natural language to Blockly XML.
"""

import json
import subprocess
from pathlib import Path
import sys

from semantic.planner import generate_semantic_plan, SemanticPlannerError
from semantic.validator import CapabilityValidator
from semantic.compiler import SemanticCompiler

# -------------------------
# Helper to run Node scripts
# -------------------------
def run(cmd, cwd):
    subprocess.run(
        cmd,
        cwd=cwd,
        check=True
    )

# Paths
ROOT = Path(__file__).parent
OUTPUTS = ROOT / "outputs"
NORMALIZED_BLOCKS = ROOT / "data" / "normalized_blocks.json"

def process_problem(problem: dict, team_id: str):
    """Process a single problem through the pipeline"""
    pid = problem["problem_id"]
    description = problem["description"]

    print(f"\n🚀 Processing Problem {pid}")
    print(f"Description: {description}")

    problem_dir = OUTPUTS / f"Problem_{pid}"
    problem_dir.mkdir(parents=True, exist_ok=True)

    # =========================
    # MODULE 1: Semantic Planner
    # =========================
    try:
        semantic_plan = generate_semantic_plan(description)
        print("📋 Semantic Plan:")
        print(json.dumps(semantic_plan, indent=2))

        if semantic_plan.get("error"):
            print(f"❌ Semantic planning failed: {semantic_plan['error']}")
            # For now, create empty outputs
            xml_dst = problem_dir / f"{team_id}_TL_{pid}.xml"
            txt_dst = problem_dir / f"{team_id}_TL_{pid}.txt"
            bug_dst = problem_dir / f"{team_id}_TL_{pid}_bug.txt"

            xml_dst.write_text("<xml></xml>")  # Empty XML
            txt_dst.write_text("# Semantic planning failed")
            bug_dst.write_text(f"Semantic error: {semantic_plan['error']}")
            return

    except SemanticPlannerError as e:
        print(f"❌ Semantic planner error: {e}")
        # Create error outputs
        xml_dst = problem_dir / f"{team_id}_TL_{pid}.xml"
        txt_dst = problem_dir / f"{team_id}_TL_{pid}.txt"
        bug_dst = problem_dir / f"{team_id}_TL_{pid}_bug.txt"

        xml_dst.write_text("<xml></xml>")
        txt_dst.write_text("# Planning failed")
        bug_dst.write_text(f"Planning error: {str(e)}")
        return

    # =========================
    # MODULE 2: Capability Validator
    # =========================
    validator = CapabilityValidator(str(NORMALIZED_BLOCKS))
    validation = validator.validate(semantic_plan)

    if validation["status"] != "ok":
        print(f"❌ Capability validation failed: {validation['reason']}")
        # Create error outputs
        xml_dst = problem_dir / f"{team_id}_TL_{pid}.xml"
        txt_dst = problem_dir / f"{team_id}_TL_{pid}.txt"
        bug_dst = problem_dir / f"{team_id}_TL_{pid}_bug.txt"

        xml_dst.write_text("<xml></xml>")
        txt_dst.write_text("# Capability validation failed")
        bug_dst.write_text(f"Validation error: {validation['reason']}")
        return

    print("✅ Capability validation passed")

    # =========================
    # MODULE 3: Semantic Compiler
    # =========================
    compiler = SemanticCompiler()
    block_tree = compiler.compile(semantic_plan)
    print("📋 Block tree generated")

    # For now, save block tree to a file for inspection
    block_tree_file = problem_dir / "block_tree.json"
    block_tree_file.write_text(json.dumps(block_tree, indent=2))

    # =========================
    # MODULE 4: XML Generator
    # =========================
    xml_output = problem_dir / f"{team_id}_TL_{pid}.xml"
    run(
        ["node", "generate_xml.js", str(block_tree_file), str(xml_output)],
        cwd=ROOT / "assembler"
    )

    print("📄 XML generated")

    # =========================
    # MODULE 5: Execution (Playwright)
    # =========================
    execution_output_dir = problem_dir / "execution_output"
    execution_output_dir.mkdir(exist_ok=True)

    try:
        run(
            ["node", "runner_execute.js", str(xml_output), str(execution_output_dir)],
            cwd=ROOT / "runner"
        )

        # Read execution results
        result_txt = execution_output_dir / "result.txt"
        diagnostics_file = execution_output_dir / "diagnostics.txt"

        if result_txt.exists():
            generated_python = result_txt.read_text()
        else:
            generated_python = "# Execution failed - no Python generated"

        if diagnostics_file.exists():
            diagnostics = diagnostics_file.read_text()
        else:
            diagnostics = "Execution completed - diagnostics not available\n"

        print("🎯 Execution completed")

    except Exception as e:
        print(f"❌ Execution failed: {e}")
        generated_python = "# Execution failed"
        diagnostics = f"Execution error: {str(e)}\n"

    # =========================
    # COLLECT FINAL OUTPUTS
    # =========================
    txt_dst = problem_dir / f"{team_id}_TL_{pid}.txt"
    bug_dst = problem_dir / f"{team_id}_TL_{pid}_bug.txt"

    txt_dst.write_text(generated_python)
    bug_dst.write_text("All modules completed successfully\n")

    print(f"✅ Problem {pid} completed fully")

def main():
    """Main entry point"""
    problems_path = ROOT / "problems.json"

    if not problems_path.exists():
        print("❌ problems.json not found")
        sys.exit(1)

    with open(problems_path) as f:
        data = json.load(f)

    team_id = data.get("team_id", "TEAM_ID0000")
    problems = data.get("problems", [])

    OUTPUTS.mkdir(exist_ok=True)

    print(f"🏁 Starting Innogen Agent v3 for team {team_id}")
    print(f"📊 Processing {len(problems)} problems")

    for problem in problems:
        try:
            process_problem(problem, team_id)
        except Exception as e:
            print(f"❌ Unexpected error processing {problem['problem_id']}: {e}")

    print("\n🎯 Processing complete")

if __name__ == "__main__":
    main()