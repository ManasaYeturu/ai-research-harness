import pytest

from backend.app.evaluation.gate import (
    calculate_score,
    evaluate_gate
)


def test_calculate_score():

    score = calculate_score(
        passed=9,
        total=10
    )

    assert score == 0.9


def test_gate_passes_when_score_meets_threshold():

    result = evaluate_gate(
        passed=9,
        total=10,
        threshold=0.90
    )

    assert result.score == 0.90
    assert result.passed_gate is True


def test_gate_passes_when_score_exceeds_threshold():

    result = evaluate_gate(
        passed=95,
        total=100,
        threshold=0.90
    )

    assert result.score == 0.95
    assert result.passed_gate is True


def test_gate_fails_when_score_is_below_threshold():

    result = evaluate_gate(
        passed=8,
        total=10,
        threshold=0.90
    )

    assert result.score == 0.80
    assert result.passed_gate is False


def test_gate_rejects_invalid_threshold():

    with pytest.raises(ValueError):

        evaluate_gate(
            passed=9,
            total=10,
            threshold=1.5
        )


def test_gate_rejects_invalid_passed_count():

    with pytest.raises(ValueError):

        evaluate_gate(
            passed=11,
            total=10
        )


def test_zero_evaluations_fail_gate():

    result = evaluate_gate(
        passed=0,
        total=0,
        threshold=0.90
    )

    assert result.score == 0.0
    assert result.passed_gate is False