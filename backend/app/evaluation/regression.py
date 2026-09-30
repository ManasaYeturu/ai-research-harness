import json

from langchain_core.messages import HumanMessage

from backend.app.agent.graph import build_graph


def load_regression_dataset(file_path: str):
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


def evaluate_regression_case(
    test_case: dict,
    graph
):

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

    retrieved_context = result.get(
        "retrieved_context",
        ""
    )

    trace_events = result["trace"].events

    tool_names = []

    for event in trace_events:

        if event.event_type == "TOOL_REQUEST":

            tool_name = event.data.get(
                "tool"
            )

            if tool_name:
                tool_names.append(
                    tool_name
                )

    required_tool = test_case.get(
        "required_tool"
    )

    tool_usage_passed = True

    if required_tool:

        tool_usage_passed = (
            required_tool in tool_names
        )

    actual_lower = actual_answer.lower()

    missing_keywords = [
        keyword
        for keyword in test_case.get(
            "required_keywords",
            []
        )
        if keyword.lower()
        not in actual_lower
    ]

    expected_source = test_case.get(
        "expected_source"
    )

    source_found = True

    if expected_source:

        source_found = (
            expected_source
            in retrieved_context
        )

    expected_retrieval_keywords = (
        test_case.get(
            "retrieval_keywords",
            []
        )
    )

    missing_retrieval_keywords = [
        keyword
        for keyword in expected_retrieval_keywords
        if keyword.lower()
        not in retrieved_context.lower()
    ]

    retrieval_passed = (
        source_found
        and not missing_retrieval_keywords
    )

    answer_passed = not missing_keywords

    passed = (
        answer_passed
        and retrieval_passed
        and tool_usage_passed
    )

    return {
        "id": test_case["id"],
        "question": test_case["question"],
        "expected_answer": test_case["expected_answer"],
        "actual_answer": actual_answer,
        "missing_keywords": missing_keywords,
        "expected_source": expected_source,
        "source_found": source_found,
        "missing_retrieval_keywords": (
            missing_retrieval_keywords
        ),
        "retrieval_passed": retrieval_passed,
        "answer_passed": answer_passed,
        "required_tool": required_tool,
        "tool_names": tool_names,
        "tool_usage_passed": tool_usage_passed,
        "passed": passed,
        "run_id": result["trace"].run_id
    }


def run_regression(file_path: str):

    test_cases = load_regression_dataset(
        file_path
    )

    graph = build_graph()

    results = []

    for test_case in test_cases:

        result = evaluate_regression_case(
            test_case,
            graph
        )

        results.append(result)

    return results