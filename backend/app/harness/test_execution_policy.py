from backend.app.harness.policies import can_execute_tool


tests = [
    0,
    1,
    2,
    3,
    4
]


for count in tests:

    result = can_execute_tool(count)

    print(
        f"tool_call_count={count} -> {result}"
    )