from backend.app.harness.policies import (
    validate_calculator_expression
)


tests = [
    "125 * 37",
    "100 / 4",
    "(10 + 5) * 2",
    "PostgreSQL is a relational database"
]


for expression in tests:

    result = validate_calculator_expression(expression)

    print(
        f"{expression!r} -> {result}"
    )