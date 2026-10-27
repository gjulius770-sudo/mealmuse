from unittest.mock import patch

from ai_service import get_ai_reply, AIUnavailableError


def test_raises_unavailable_when_no_api_key_set(app, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    try:
        get_ai_reply("hello", "fitness", ["rice"], 300)
        assert False, "expected AIUnavailableError to be raised"
    except AIUnavailableError:
        pass


def test_chat_endpoint_falls_back_when_ai_is_unavailable(client):
    client.post("/profile", data={"name": "Grace", "dietary_goal": "fitness"})
    client.post("/inventory", data={"ingredient_name": "rice", "quantity": "2"})
    client.post("/budget", data={"amount": "500", "period": "weekly"})

    with patch("app.get_ai_reply", side_effect=AIUnavailableError("simulated outage")):
        response = client.post(
            "/chat",
            data={"message": "what can I cook?", "meal_of_day": "lunch"},
        )

    assert response.status_code == 200
    assert b"AI unavailable" in response.data
