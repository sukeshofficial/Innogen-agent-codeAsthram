"""
Capability Validator (Module 2)

Determines if a semantic plan can be expressed using available Blockly blocks.
Checks against normalized_blocks.json to ensure feasibility.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Set

class CapabilityValidator:
    """
    Validates whether a semantic plan can be implemented with available blocks.
    """

    # Supported operations based on normalized_blocks.json analysis
    SUPPORTED_ARITH_OPS = {"+", "-", "*", "/"}  # Basic arithmetic
    SUPPORTED_COMP_OPS = {">", "<", ">=", "<=", "==", "!="}  # Comparisons
    SUPPORTED_LOGICAL_OPS = {"and", "or"}  # Logical operators

    def __init__(self, normalized_blocks_path: str):
        self.blocks = self._load_blocks(normalized_blocks_path)
        self.block_types = {b["type"] for b in self.blocks}
        self.capabilities = self._analyze_capabilities()

    def _load_blocks(self, path: str) -> List[Dict[str, Any]]:
        """Load normalized blocks from JSON file"""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Blocks file not found: {path}")
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _analyze_capabilities(self) -> Dict[str, Any]:
        """Analyze what operations are supported by the blocks"""
        capabilities = {
            "has_arithmetic": False,
            "has_comparisons": False,
            "has_logic": False,
            "has_print": False,
            "has_variables": False,
            "has_input": False,
            "supported_functions": set()
        }

        for block in self.blocks:
            block_type = block["type"]

            # Check for arithmetic operations
            if "arithmetic" in block_type.lower() or "math" in block_type.lower():
                capabilities["has_arithmetic"] = True

            # Check for comparisons
            if "compare" in block_type.lower() or "comparison" in block_type.lower():
                capabilities["has_comparisons"] = True

            # Check for logical operations
            if "logic" in block_type.lower() or "boolean" in block_type.lower():
                capabilities["has_logic"] = True

            # Check for print operations
            if "print" in block_type.lower():
                capabilities["has_print"] = True

            # Check for variables
            if "var" in block_type.lower() or "variable" in block_type.lower():
                capabilities["has_variables"] = True

            # Check for input
            if "input" in block_type.lower():
                capabilities["has_input"] = True

            # Collect function names from python_sample
            python_sample = block.get("python_sample", "")
            if python_sample:
                # Extract function calls like min(, max(, len(, etc.
                functions = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', python_sample)
                capabilities["supported_functions"].update(functions)

        return capabilities

    def validate(self, semantic_plan: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate if the semantic plan can be implemented.

        Returns:
            {"status": "ok"} or {"status": "error", "reason": "..."}
        """
        try:
            # Check if plan has error from planner
            if semantic_plan.get("error"):
                return {"status": "error", "reason": semantic_plan["error"]}

            # Validate inputs
            self._validate_inputs(semantic_plan.get("inputs", []))

            # Validate derived calculations
            self._validate_derived(semantic_plan.get("derived", []))

            # Validate condition
            self._validate_condition(semantic_plan.get("condition"))

            # Validate actions
            self._validate_actions(semantic_plan.get("actions", {}))

            return {"status": "ok"}

        except ValidationError as e:
            return {"status": "error", "reason": str(e)}

    def _validate_inputs(self, inputs: List[str]):
        """Validate input variables"""
        if not isinstance(inputs, list):
            raise ValidationError("inputs must be a list")

        # For now, assume all inputs are valid (numbers/strings)
        # Could add type checking later if needed
        pass

    def _validate_derived(self, derived: List[str]):
        """Validate derived calculations"""
        if not isinstance(derived, list):
            raise ValidationError("derived must be a list")

        for calc in derived:
            if not isinstance(calc, str):
                raise ValidationError(f"derived calculation must be string: {calc}")

            # Check if calculation uses supported operations
            if not self._is_supported_calculation(calc):
                raise ValidationError(f"unsupported calculation: {calc}")

    def _validate_condition(self, condition):
        """Validate condition expression"""
        if condition is None:
            return  # No condition is valid

        if not isinstance(condition, str):
            raise ValidationError("condition must be a string or null")

        # Parse and validate condition
        if not self._is_supported_condition(condition):
            raise ValidationError(f"unsupported condition: {condition}")

    def _validate_actions(self, actions: Dict[str, List]):
        """Validate actions"""
        if not isinstance(actions, dict):
            raise ValidationError("actions must be a dict")

        required_keys = {"then", "else"}
        if not all(key in actions for key in required_keys):
            raise ValidationError("actions must have 'then' and 'else' keys")

        for branch in ["then", "else"]:
            if not isinstance(actions[branch], list):
                raise ValidationError(f"actions.{branch} must be a list")

            for action in actions[branch]:
                if not isinstance(action, str):
                    raise ValidationError(f"action must be string: {action}")

                if not self._is_supported_action(action):
                    raise ValidationError(f"unsupported action: {action}")

    def _is_supported_calculation(self, calc: str) -> bool:
        """Check if a calculation can be expressed"""
        # Simple check: look for basic arithmetic
        # This is a simplified check - could be more sophisticated
        calc = calc.strip()

        # Check for basic arithmetic patterns
        if re.search(r'[+\-*/]', calc):
            return self.capabilities["has_arithmetic"]

        # Check for function calls
        func_match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', calc)
        if func_match:
            func_name = func_match.group(1)
            return func_name in self.capabilities["supported_functions"]

        # Simple variable assignments
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*', calc):
            return True

        return False

    def _is_supported_condition(self, condition: str) -> bool:
        """Check if a condition can be expressed"""
        if not condition:
            return True

        # For now, assume conditions are supported if we have comparison and logic capabilities
        # This is a simplified check - in a real implementation we'd parse the expression
        if self.capabilities["has_comparisons"] and self.capabilities["has_logic"]:
            return True

        # Fallback: if we have comparisons, accept simple conditions
        if self.capabilities["has_comparisons"]:
            return True

        return False

    def _is_supported_action(self, action: str) -> bool:
        """Check if an action can be expressed"""
        action = action.strip().lower()

        # Check for print actions (any action containing print)
        if "print" in action:
            return self.capabilities["has_print"]

        # For now, accept any action if print is available
        # This allows for semantic descriptions that will be mapped to print later
        return self.capabilities["has_print"]

class ValidationError(Exception):
    """Raised when validation fails"""
    pass