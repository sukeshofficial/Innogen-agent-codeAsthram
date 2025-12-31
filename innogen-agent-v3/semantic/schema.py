"""
Semantic Schema for Innogen Agent v3

This defines the pure semantic representation that the LLM outputs.
No Blockly, no XML, no block names - just semantic meaning.
"""

# Semantic Plan Schema
# The LLM outputs this exact structure
SEMANTIC_SCHEMA = {
    "inputs": [],        # List of input variable names (strings)
    "derived": [],       # List of derived calculations (strings describing operations)
    "condition": None,   # Condition expression as string, or None
    "actions": {
        "then": [],      # List of actions to take if condition is true
        "else": []       # List of actions to take if condition is false
    }
}

def validate_semantic_plan(plan: dict) -> bool:
    """
    Basic validation that the plan matches the expected schema.
    """
    if not isinstance(plan, dict):
        return False

    required_keys = ["inputs", "derived", "condition", "actions"]
    if not all(key in plan for key in required_keys):
        return False

    if not isinstance(plan["inputs"], list):
        return False

    if not isinstance(plan["derived"], list):
        return False

    if plan["condition"] is not None and not isinstance(plan["condition"], str):
        return False

    if not isinstance(plan["actions"], dict):
        return False

    if "then" not in plan["actions"] or "else" not in plan["actions"]:
        return False

    if not isinstance(plan["actions"]["then"], list):
        return False

    if not isinstance(plan["actions"]["else"], list):
        return False

    return True