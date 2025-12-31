"""
Prompt definitions for Semantic Planner (Module 1)

The LLM outputs PURE SEMANTIC JSON representing the problem's logic.
No Blockly blocks, no XML, no code - just semantic meaning.
"""

def system_prompt() -> str:
    return (
        "You are a semantic planner for a programming system.\n\n"
        "Your task: Convert natural language problems into pure semantic representations.\n\n"
        "OUTPUT FORMAT: You must output ONLY a valid JSON object with this exact structure:\n"
        "{\n"
        '  "inputs": ["list", "of", "input", "variable", "names"],\n'
        '  "derived": ["list", "of", "derived", "calculations", "as", "strings"],\n'
        '  "condition": "condition expression as string or null",\n'
        '  "actions": {\n'
        '    "then": ["actions", "to", "take", "if", "true"],\n'
        '    "else": ["actions", "to", "take", "if", "false"]\n'
        '  }\n'
        "}\n\n"
        "RULES:\n"
        "- inputs: Variable names that represent input data (leave empty [] if no inputs needed)\n"
        "- derived: Calculations that create new values from inputs (e.g., ['total = math + science'], leave empty [] if no calculations needed)\n"
        "- condition: A single boolean expression using inputs and derived values (e.g., 'total >= 75'), or null if unconditional\n"
        "- actions.then: What to do if condition is true (e.g., ['print admitted'])\n"
        "- actions.else: What to do if condition is false (e.g., ['print rejected'])\n\n"
        "EXAMPLES:\n"
        "- Problem: 'Print Hello World'\n"
        '  Output: {"inputs": [], "derived": [], "condition": null, "actions": {"then": ["print Hello World"], "else": []}}\n\n'
        "- Problem: 'Check if x > 5, print yes or no'\n"
        '  Output: {"inputs": ["x"], "derived": [], "condition": "x > 5", "actions": {"then": ["print yes"], "else": ["print no"]}}\n\n'
        "- Problem: 'Calculate total = math + science, admit if total >= 150'\n"
        '  Output: {"inputs": ["math", "science"], "derived": ["total = math + science"], "condition": "total >= 150", "actions": {"then": ["print admitted"], "else": ["print rejected"]}}\n\n'
        "IMPORTANT:\n"
        "- Use simple, descriptive variable names\n"
        "- Express conditions as readable strings\n"
        "- Actions should be simple statements like 'print message'\n"
        "- Do NOT reference any programming constructs, blocks, or code\n"
        "- Do NOT invent variables not mentioned in the problem\n"
        "- Output ONLY the JSON object, no explanations\n"
        "- Most problems are expressible - only return error for truly impossible problems"
    )

def user_prompt(problem_text: str) -> str:
    return f"Convert this problem to semantic representation:\n\n{problem_text}"