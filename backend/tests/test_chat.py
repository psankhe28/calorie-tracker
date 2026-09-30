from types import SimpleNamespace

import pytest

from app.services import chat_agent


class FakeCompletions:
    """Stands in for client.chat.completions: always answers with plain text, never calls tools."""

    def __init__(self):
        self.calls = 0

    def create(self, **kwargs):
        self.calls += 1
        message = SimpleNamespace(content=f"reply {self.calls}", tool_calls=None)
        return SimpleNamespace(choices=[SimpleNamespace(finish_reason="stop", message=message)])


@pytest.fixture()
def completions(monkeypatch):
    fake = FakeCompletions()
    monkeypatch.setattr(chat_agent, "get_client", lambda: SimpleNamespace(chat=SimpleNamespace(completions=fake)))
    return fake


def _send(client, headers, message, history):
    return client.post("/api/chat", json={"message": message, "history": history}, headers=headers)


def test_chat_allows_five_user_messages_then_rejects(client, auth_headers, completions):
    history = []
    for i in range(1, 6):
        resp = _send(client, auth_headers, f"message {i}", history)
        assert resp.status_code == 200
        history = resp.json()["history"]

    assert [m["role"] for m in history].count("user") == 5

    resp = _send(client, auth_headers, "message 6", history)
    assert resp.status_code == 429
    assert "limit of 5 messages" in resp.json()["detail"]
    assert completions.calls == 5  # the rejected message never reached the model


def test_chat_limit_counts_only_user_messages(client, auth_headers, completions):
    # 4 user turns padded with extra assistant turns: the next user message is only the 5th.
    history = []
    for i in range(1, 5):
        history.append({"role": "user", "content": f"question {i}"})
        history += [{"role": "assistant", "content": f"answer {i}"}] * 3

    resp = _send(client, auth_headers, "question 5", history)
    assert resp.status_code == 200
