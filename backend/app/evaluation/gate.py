from dataclasses import dataclass


DEFAULT_THRESHOLD = 0.90


@dataclass
class EvaluationGateResult:
    total: int
    passed: int
    failed: int
    score: float
    threshold: float
    passed_gate: bool


def calculate_score(
    passed: int,
    total: int
) -> float:

    if total <= 0:
        return 0.0

    return passed / total


def evaluate_gate(
    passed: int,
    total: int,
    threshold: float = DEFAULT_THRESHOLD
) -> EvaluationGateResult:

    if total < 0:
        raise ValueError(
            "Total evaluations cannot be negative."
        )

    if passed < 0:
        raise ValueError(
            "Passed evaluations cannot be negative."
        )

    if passed > total:
        raise ValueError(
            "Passed evaluations cannot exceed total evaluations."
        )

    if not 0 <= threshold <= 1:
        raise ValueError(
            "Threshold must be between 0 and 1."
        )

    score = calculate_score(
        passed=passed,
        total=total
    )

    failed = total - passed

    passed_gate = (
        total > 0
        and score >= threshold
    )

    return EvaluationGateResult(
        total=total,
        passed=passed,
        failed=failed,
        score=score,
        threshold=threshold,
        passed_gate=passed_gate
    )