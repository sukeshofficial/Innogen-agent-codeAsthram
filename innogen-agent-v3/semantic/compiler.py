"""
Semantic → Block Tree Compiler (Module 3)

Converts validated semantic JSON into block tree JSON for XML generation.
"""

import re
from typing import Dict, List, Any

class SemanticCompiler:
    """
    Compiles semantic plans into block trees.
    """

    def __init__(self):
        self.variable_counter = 0

    def compile(self, semantic_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compile semantic plan to block tree.

        Args:
            semantic_plan: Validated semantic plan

        Returns:
            Block tree JSON
        """
        # Start with input blocks
        head = None
        current = None

        # 1. Create input variables
        for var_name in semantic_plan.get("inputs", []):
            input_block = self._create_input_block(var_name)
            head, current = self._chain_blocks(head, current, input_block)

        # 2. Create derived calculations
        for derived_expr in semantic_plan.get("derived", []):
            derived_block = self._create_derived_block(derived_expr)
            if derived_block:
                head, current = self._chain_blocks(head, current, derived_block)

        # 3. Create conditional logic with actions
        condition = semantic_plan.get("condition")
        if condition:
            condition_block = self._create_condition_block(condition, semantic_plan.get("actions", {}))
            if condition_block:
                head, current = self._chain_blocks(head, current, condition_block)

        # 4. If no condition, just execute the then actions
        elif semantic_plan.get("actions", {}).get("then"):
            for action in semantic_plan["actions"]["then"]:
                action_block = self._create_action_block(action)
                if action_block:
                    head, current = self._chain_blocks(head, current, action_block)

        return head if head else {"type": "text_print", "value_inputs": {"TEXT": {"type": "text_literal", "fields": {"TEXT": "No operations"}}}}  # Fallback

    def _chain_blocks(self, head: Dict, current: Dict, new_block: Dict) -> tuple:
        """Chain a new block to the sequence"""
        if head is None:
            return new_block, new_block
        current["next"] = new_block
        return head, new_block

    def _create_input_block(self, var_name: str) -> Dict[str, Any]:
        """Create a block to read input into a variable"""
        return {
            "type": "essentials_var_set",
            "fields": {"VAR": var_name},
            "value_inputs": {
                "VALUE": {
                    "type": "essentials_safe_input",
                    "fields": {"TYPE": "str"}
                }
            }
        }

    def _create_derived_block(self, derived_expr: str) -> Dict[str, Any]:
        """Create a block for a derived calculation"""
        # Parse expressions like "total = a + b"
        match = re.match(r'^(\w+)\s*=\s*(.+)$', derived_expr.strip())
        if not match:
            return None

        var_name = match.group(1)
        expression = match.group(2)

        # Create the calculation block
        calc_block = self._parse_expression(expression)

        return {
            "type": "essentials_var_set",
            "fields": {"VAR": var_name},
            "value_inputs": {"VALUE": calc_block}
        }

    def _parse_expression(self, expr: str) -> Dict[str, Any]:
        """Parse a mathematical expression into blocks"""
        expr = expr.strip()

        # Handle parentheses
        if expr.startswith('(') and expr.endswith(')'):
            expr = expr[1:-1]

        # Simple binary operations
        for op in ['+', '-', '*', '/']:
            if op in expr:
                parts = expr.split(op, 1)
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip()

                    op_field = {
                        '+': '+',
                        '-': '-',
                        '*': '*',
                        '/': '/'
                    }.get(op)

                    return {
                        "type": "essentials_num_arithmetic",
                        "fields": {"OP": op_field},
                        "value_inputs": {
                            "A": self._parse_operand(left),
                            "B": self._parse_operand(right)
                        }
                    }

        # Single operand
        return self._parse_operand(expr)

    def _parse_operand(self, operand: str) -> Dict[str, Any]:
        """Parse a single operand (variable or number)"""
        operand = operand.strip()

        # Check if it's a number
        try:
            float(operand)
            return {
                "type": "essentials_num_literal",
                "fields": {"NUM": operand}
            }
        except ValueError:
            pass

        # Assume it's a variable
        return {
            "type": "essentials_var_get",
            "fields": {"VAR": operand}
        }

    def _create_condition_block(self, condition: str, actions: Dict[str, List[str]]) -> Dict[str, Any]:
        """Create an if-else block with condition and actions"""
        condition_block = self._parse_condition(condition)

        # Create then branch
        then_head = None
        then_current = None
        for action in actions.get("then", []):
            action_block = self._create_action_block(action)
            if action_block:
                then_head, then_current = self._chain_blocks(then_head, then_current, action_block)

        # Create else branch
        else_head = None
        else_current = None
        for action in actions.get("else", []):
            action_block = self._create_action_block(action)
            if action_block:
                else_head, else_current = self._chain_blocks(else_head, else_current, action_block)

        # Create if block
        if_block = {
            "type": "control_if_truthy",
            "value_inputs": {"EXPR": condition_block},
            "statement_inputs": {}
        }

        if then_head:
            if_block["statement_inputs"]["THEN"] = then_head

        if else_head:
            if_block["statement_inputs"]["ELSE"] = else_head

        return if_block

    def _parse_condition(self, condition: str) -> Dict[str, Any]:
        """Parse a condition expression"""
        condition = condition.strip()

        # Handle logical operators
        for logic_op in ['and', 'or']:
            if f' {logic_op} ' in condition:
                parts = condition.split(f' {logic_op} ', 1)
                if len(parts) == 2:
                    left = self._parse_condition(parts[0])
                    right = self._parse_condition(parts[1])

                    op_type = "essentials_logic_and" if logic_op == "and" else "essentials_logic_or"
                    return {
                        "type": op_type,
                        "value_inputs": {"A": left, "B": right}
                    }

        # Handle comparison operators
        for comp_op in ['>=', '<=', '>', '<', '==', '!=']:
            if comp_op in condition:
                parts = condition.split(comp_op, 1)
                if len(parts) == 2:
                    left = self._parse_operand(parts[0].strip())
                    right = self._parse_operand(parts[1].strip())

                    return {
                        "type": "essentials_compare",
                        "fields": {"OP": self._map_comparison_op(comp_op)},
                        "value_inputs": {"A": left, "B": right}
                    }

        # Fallback: treat as variable
        return self._parse_operand(condition)

    def _map_comparison_op(self, op: str) -> str:
        """Map comparison operator to block field value"""
        mapping = {
            '>': 'GT',
            '<': 'LT',
            '>=': 'GTE',
            '<=': 'LTE',
            '==': 'EQ',
            '!=': 'NEQ'
        }
        return mapping.get(op, 'EQ')

    def _create_action_block(self, action: str) -> Dict[str, Any]:
        """Create a block for an action"""
        action = action.strip()

        # Handle print actions
        if action.startswith('print '):
            message = action[6:].strip()
            return {
                "type": "text_print",
                "value_inputs": {
                    "TEXT": {
                        "type": "text_literal",
                        "fields": {"TEXT": message}
                    }
                }
            }

        # Default: assume it's a print action
        return {
            "type": "text_print",
            "value_inputs": {
                "TEXT": {
                    "type": "text_literal",
                    "fields": {"TEXT": action}
                }
            }
        }