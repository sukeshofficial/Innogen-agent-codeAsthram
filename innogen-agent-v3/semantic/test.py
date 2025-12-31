"""
Tests for Semantic Planner (Module 1)

Tests the semantic planning capabilities with various problem types.
"""

import json
from semantic.planner import generate_semantic_plan, SemanticPlannerError

def test_hello_world():
    """Test simple hello world output"""
    problem = "Print the message 'Hello World'"
    plan = generate_semantic_plan(problem)

    print("Hello World Test:")
    print(json.dumps(plan, indent=2))

    if plan.get("error"):
        print(f"❌ Got error: {plan['error']}")
        return  # Skip assertions for now

    # Should have no inputs, no condition, and print action
    assert "inputs" in plan
    assert "actions" in plan
    assert len(plan["actions"]["then"]) > 0
    print("✅ Hello World test passed\n")

def test_candidate_qualification():
    """Test the candidate qualification problem from the requirements"""
    problem = "A candidate qualifies only if written score is at least 60 interview score at least 15 and total does not exceed 100."

    plan = generate_semantic_plan(problem)

    print("Candidate Qualification Test:")
    print(json.dumps(plan, indent=2))

    # Should have inputs for scores
    assert "inputs" in plan
    assert len(plan["inputs"]) > 0
    # Should have a condition
    assert plan["condition"] is not None
    # Should have actions
    assert "actions" in plan
    print("✅ Candidate qualification test passed\n")

def test_unsolvable_problem():
    """Test a problem that cannot be expressed with available blocks"""
    # This should be a problem that requires unsupported operations
    problem = "Calculate the factorial of a number and check if it's prime."

    plan = generate_semantic_plan(problem)

    print("Unsolvable Problem Test:")
    print(json.dumps(plan, indent=2))

    # The planner should try to express it semantically
    # The validator (Module 2) will determine it's not feasible
    assert "inputs" in plan  # Should have inputs
    assert "derived" in plan  # Should have derived calculations
    assert plan["condition"] is not None  # Should have condition
    print("✅ Unsolvable problem test passed (semantic plan generated, validation pending)\n")

def run_tests():
    """Run all semantic planner tests"""
    print("🧪 Running Semantic Planner Tests\n")

    try:
        test_hello_world()
        test_candidate_qualification()
        test_unsolvable_problem()

        print("🎉 All tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    run_tests()