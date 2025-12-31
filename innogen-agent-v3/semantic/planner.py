"""
Semantic Planner (Module 1)

Generates pure semantic JSON from natural language problems.
No Blockly, no XML, no code - just semantic meaning.
"""

import json
import os
from typing import Dict, Union, Any

from dotenv import load_dotenv
from openai import OpenAI

from semantic.prompt import system_prompt, user_prompt
from semantic.schema import validate_semantic_plan

# Load environment variables
load_dotenv()

class SemanticPlannerError(Exception):
    """Raised when the semantic planner fails unexpectedly."""


def generate_semantic_plan(problem_text: str) -> Dict[str, Any]:
    """
    Generate a semantic plan from a natural language problem.

    Args:
        problem_text: The natural language problem description

    Returns:
        Semantic plan dict matching the schema, or {"error": "not_expressible"}

    Raises:
        SemanticPlannerError on unexpected failures
    """

    if not problem_text or not isinstance(problem_text, str):
        raise SemanticPlannerError("Problem text must be a non-empty string")

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise SemanticPlannerError("OPENROUTER_API_KEY not set")

    # Initialize OpenRouter client
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )

    # Build prompts
    sys_prompt = system_prompt()
    usr_prompt = user_prompt(problem_text)

    # Call LLM
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-3-8b-instruct",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": usr_prompt}
            ],
            temperature=0
        )
    except Exception as e:
        raise SemanticPlannerError(f"LLM call failed: {e}")

    raw_output = response.choices[0].message.content.strip()

    # Extract and parse JSON
    try:
        # Try to find JSON in the response
        json_start = raw_output.find('{')
        json_end = raw_output.rfind('}') + 1
        if json_start == -1 or json_end == 0:
            json_text = raw_output
        else:
            json_text = raw_output[json_start:json_end]

        parsed = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise SemanticPlannerError(
            f"LLM did not return valid JSON. Raw output: {raw_output[:500]}"
        )

    # Validate the semantic plan structure
    if not validate_semantic_plan(parsed):
        return {"error": "not_expressible"}

    return parsed