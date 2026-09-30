import sys

from backend.app.evaluation.regression import (
    run_regression
)


if len(sys.argv) != 2:
    print(
        "Usage: python -m "
        "backend.app.evaluation.run_regression "
        "<dataset_path>"
    )
    sys.exit(1)


dataset_path = sys.argv[1]

results = run_regression(
    dataset_path
)

print("\nAI Regression Test Results")
print("==========================")

total = len(results)
passed = 0

for result in results:

    status = (
        "PASS"
        if result["passed"]
        else "FAIL"
    )

    if result["passed"]:
        passed += 1

    print(
        f"\n[{status}] {result['id']}"
    )

    print(
        f"Question: {result['question']}"
    )

    print(
        f"Answer: {result['actual_answer']}"
    )

    print(
        "Answer keywords: "
        f"{'PASS' if result['answer_passed'] else 'FAIL'}"
    )

    if result["missing_keywords"]:
        print(
            "Missing answer keywords: "
            f"{result['missing_keywords']}"
        )

    print(
        "Retrieval: "
        f"{'PASS' if result['retrieval_passed'] else 'FAIL'}"
    )

    if result["expected_source"]:
        print(
            "Expected source: "
            f"{result['expected_source']}"
        )

        print(
            "Source found: "
            f"{result['source_found']}"
        )

    if result["required_tool"]:

        print(
            "Required tool: "
            f"{result['required_tool']}"
        )

        print(
            "Tool usage: "
            f"{'PASS' if result['tool_usage_passed'] else 'FAIL'}"
        )

        print(
            "Tools used: "
            f"{result['tool_names']}"
        )

    if result["missing_retrieval_keywords"]:
        print(
            "Missing retrieval keywords: "
            f"{result['missing_retrieval_keywords']}"
        )

    print(
        f"Run ID: {result['run_id']}"
    )


failed = total - passed

print("\nSummary")
print("=======")
print(f"Total cases: {total}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")

if total > 0:
    pass_rate = (
        passed / total
    ) * 100

    print(
        f"Pass rate: {pass_rate:.1f}%"
    )


if failed > 0:
    sys.exit(1)