import json

from langchain_core.messages import HumanMessage

from backend.app.agent.graph import build_graph

from backend.app.evaluation.correctness import (
    evaluate_correctness
)

from backend.app.evaluation.faithfulness import (
    evaluate_faithfulness
)
from backend.app.evaluation.retrieval import (
    evaluate_retrieval
)
from backend.app.evaluation.relevance import (
    evaluate_relevance
)


def load_evaluation_dataset(file_path: str):
    test_cases = []

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:
            if not line.strip():
                continue

            test_cases.append(
                json.loads(line)
            )

    return test_cases


def run_evaluation_case(test_case: dict):
    graph = build_graph()

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content=test_case["question"]
                )
            ],
            "tool_call_count": 0,
            "no_relevant_context": False
        }
    )

    
    

    final_message = result["messages"][-1]

    actual_answer = str(
        final_message.content
    ).strip()

    if actual_answer.startswith("assistant"):
        actual_answer = actual_answer[len("assistant"):].strip()

    expected_answer = test_case[
        "expected_answer"
    ]

    return {
        "id": test_case["id"],
        "question": test_case["question"],
        "expected_answer": expected_answer,
        "actual_answer": actual_answer,
        "retrieved_context": result.get(
            "retrieved_context",
            ""
        ),
        "run_id": result["trace"].run_id
    }

def evaluate_answer(
    expected_answer: str,
    actual_answer: str
):
    return (
        expected_answer.strip()
        == actual_answer.strip()
    )

def run_evaluation(file_path: str):

    test_cases = load_evaluation_dataset(
        file_path
    )

    results = []

    for test_case in test_cases:

        result = run_evaluation_case(
            test_case
        )

        keyword_result = evaluate_required_keywords(
            result["actual_answer"],
            test_case["required_keywords"]
        )

        retrieval_result = evaluate_retrieval(
                expected_source=test_case.get("expected_source"),
                retrieved_context=result["retrieved_context"],
                expected_keywords=test_case.get("required_keywords")
        )

        if (
            test_case.get("expected_source") is None
            and result["retrieved_context"]
            == "No relevant information was found."
        ):
            relevance_result = {
                "relevant": True,
                "reason": (
                    "No relevant context was expected "
                    "and no relevant context was retrieved."
                ),
                "matched_keywords": [],
                "missing_keywords": []
            }
        else:
            relevance_result = evaluate_relevance(
                question=test_case["question"],
                retrieved_context=result["retrieved_context"],
                expected_keywords=test_case.get(
                    "retrieval_keywords"
                )
            )

        correctness_result = evaluate_correctness(
            result["expected_answer"],
            result["actual_answer"]
        )

        if result["retrieved_context"] == "No relevant information was found.":

            faithfulness_result = {
                "passed": True,
                "reason": (
                    "No relevant context was retrieved; "
                    "no-context behavior is evaluated separately."
                )
            }
        

        else:

            faithfulness_result = evaluate_faithfulness(
                result["retrieved_context"],
                result["actual_answer"]
            )

        result["retrieval_passed"] = (
            retrieval_result["passed"]
        )

        result["retrieval_reason"] = (
            retrieval_result["reason"]
        )

        result["expected_source"] = (
            retrieval_result["expected_source"]
        )

        result["retrieved_source_found"] = (
            retrieval_result["source_found"]
        )

        result["retrieval_missing_keywords"] = (
            retrieval_result["missing_keywords"]
        )

        result["retrieval_content_relevant"] = (
            retrieval_result["content_relevant"]
        )

        result["relevance_passed"] = (
            relevance_result["relevant"]
        )

        result["relevance_reason"] = (
            relevance_result["reason"]
        )

        result["relevance_matched_keywords"] = (
            relevance_result["matched_keywords"]
        )

        result["relevance_missing_keywords"] = (
            relevance_result["missing_keywords"]
        )

        result["keyword_passed"] = (
            keyword_result["passed"]
        )

        result["missing_keywords"] = (
            keyword_result["missing_keywords"]
        )

        result["correctness_passed"] = (
            correctness_result["passed"]
        )

        result["correctness_reason"] = (
            correctness_result["reason"]
        )

        result["faithfulness_passed"] = (
            faithfulness_result["passed"]
        )

        result["faithfulness_reason"] = (
            faithfulness_result["reason"]
        )

        result["passed"] = (
            retrieval_result["passed"]
            and relevance_result["relevant"]
            and keyword_result["passed"]
            and correctness_result["passed"]
            and faithfulness_result["passed"]
        )

        results.append(result)

    return results

def evaluate_required_keywords(
    actual_answer: str,
    required_keywords: list[str]
):
    actual_text = actual_answer.lower()

    missing_keywords = []

    for keyword in required_keywords:
        if keyword.lower() not in actual_text:
            missing_keywords.append(keyword)

    return {
        "passed": len(missing_keywords) == 0,
        "missing_keywords": missing_keywords
    }