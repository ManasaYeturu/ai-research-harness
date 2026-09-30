from langchain_ollama import ChatOllama


MODEL_NAME = "llama3.2:3b"


evaluator_llm = ChatOllama(
    model=MODEL_NAME,
    temperature=0
)


CORRECTNESS_PROMPT = """
Evaluate whether the actual answer is factually correct relative to
the expected answer.

IMPORTANT:

The expected answer is a reference answer, NOT a strict template.

The actual answer may:
- use different wording
- be longer
- contain additional explanations
- contain examples
- contain additional correct facts

None of these are reasons for FAIL.

Return PASS when:
- the actual answer communicates the main information in the expected answer
- and it does not contain a significant factual error or contradiction.

Return FAIL only when:
- an essential part of the expected answer is missing, OR
- the actual answer contains a significant factual error, OR
- the actual answer contradicts the expected answer.

Do NOT compare the length of the answers.
Do NOT require the actual answer to contain only information from
the expected answer.
Do NOT fail because information is "not present in the expected answer".

EXPECTED ANSWER:
{expected_answer}

ACTUAL ANSWER:
{actual_answer}

Return exactly one of:

PASS
Reason: <short reason>

or

FAIL
Reason: <short reason>
"""


def evaluate_correctness(
    expected_answer: str,
    actual_answer: str
):
    prompt = CORRECTNESS_PROMPT.format(
        expected_answer=expected_answer,
        actual_answer=actual_answer
    )

    response = evaluator_llm.invoke(prompt)

    result = str(response.content).strip()

    if result.startswith("PASS"):
        passed = True
    elif result.startswith("FAIL"):
        passed = False
    else:
        passed = False

    reason = result

    if "Reason:" in result:
        reason = result.split(
            "Reason:",
            1
        )[1].strip()

    return {
        "passed": passed,
        "reason": reason
    }