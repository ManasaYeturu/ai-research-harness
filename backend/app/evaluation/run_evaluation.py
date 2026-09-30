import sys

from backend.app.evaluation.evaluator import run_evaluation
from backend.app.evaluation.gate import evaluate_gate


if len(sys.argv) != 2:
    print(
        "Usage: python -m backend.app.evaluation.run_evaluation "
        "<dataset_path>"
    )
    sys.exit(1)


dataset_path = sys.argv[1]


results = run_evaluation(
    dataset_path
)


print("\nEvaluation Results")
print("==================")


total = len(results)
passed = 0


for result in results:

    status = "PASS" if result["passed"] else "FAIL"

    if result["passed"]:
        passed += 1

    print(f"\n[{status}] {result['id']}")
    print(f"Question: {result['question']}")
    print(f"Expected: {result['expected_answer']}")
    print(f"Actual:   {result['actual_answer']}")

    if result["missing_keywords"]:
        print(
            f"Missing keywords: "
            f"{result['missing_keywords']}"
        )
    else:
        print("Missing keywords: None")

    print(
        f"Retrieval evaluation: "
        f"{'PASS' if result['retrieval_passed'] else 'FAIL'}"
    )

    print(
        f"Expected source: "
        f"{result['expected_source']}"
    )

    print(
        f"Expected source found: "
        f"{result['retrieved_source_found']}"
    )

    print(
        f"Retrieval missing keywords: "
        f"{result['retrieval_missing_keywords']}"
    )

    print(
        f"Retrieval content relevant: "
        f"{result['retrieval_content_relevant']}"
    )

    print(
        f"Retrieval reason: "
        f"{result['retrieval_reason']}"
    )

    print(
        f"Relevance evaluation: "
        f"{'PASS' if result['relevance_passed'] else 'FAIL'}"
    )

    print(
        f"Relevance matched keywords: "
        f"{result['relevance_matched_keywords']}"
    )

    print(
        f"Relevance missing keywords: "
        f"{result['relevance_missing_keywords']}"
    )

    print(
        f"Relevance reason: "
        f"{result['relevance_reason']}"
    )

    print(
        f"Keyword evaluation: "
        f"{'PASS' if result['keyword_passed'] else 'FAIL'}"
    )

    print(
        f"Correctness evaluation: "
        f"{'PASS' if result['correctness_passed'] else 'FAIL'}"
    )

    print(
        f"Correctness reason: "
        f"{result['correctness_reason']}"
    )

    print(
        f"Faithfulness evaluation: "
        f"{'PASS' if result['faithfulness_passed'] else 'FAIL'}"
    )

    print(
        f"Faithfulness reason: "
        f"{result['faithfulness_reason']}"
    )

    print(f"Run ID: {result['run_id']}")


print("\nSummary")
print("=======")
print(f"Total cases: {total}")
print(f"Passed: {passed}")
print(f"Failed: {total - passed}")


if total > 0:
    pass_rate = (passed / total) * 100
    print(f"Pass rate: {pass_rate:.1f}%")
else:
    pass_rate = 0.0
    print("Pass rate: 0.0%")


# --------------------------------------------------
# Evaluation Gate
# --------------------------------------------------

gate_result = evaluate_gate(
    passed=passed,
    total=total,
    threshold=0.90
)


print("\nEvaluation Gate")
print("===============")

print(
    f"Score: "
    f"{gate_result.score * 100:.1f}%"
)

print(
    f"Threshold: "
    f"{gate_result.threshold * 100:.1f}%"
)

print(
    f"Gate: "
    f"{'PASSED' if gate_result.passed_gate else 'FAILED'}"
)


if not gate_result.passed_gate:
    print(
        "\nEvaluation gate failed. "
        "CI/CD pipeline should stop."
    )
    sys.exit(1)


print(
    "\nEvaluation gate passed. "
    "CI/CD pipeline may continue."
)

sys.exit(0)