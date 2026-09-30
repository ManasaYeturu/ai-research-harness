from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_chat_rejects_empty_question():

    response = client.post(
        "/chat",
        json={
            "question": ""
        }
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Invalid question."
    )


def test_chat_rejects_whitespace_question():

    response = client.post(
        "/chat",
        json={
            "question": "   "
        }
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Invalid question."
    )


def test_chat_rejects_question_that_is_too_long():

    response = client.post(
        "/chat",
        json={
            "question": "a" * 2001
        }
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Invalid question."
    )