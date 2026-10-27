"""
Talks to an AI API to answer the user's chat message (e.g. "I have
500 on a budget, what can I cook?"). If anything goes wrong - no API
key set, the request times out, the service is down - we raise
AIUnavailableError so app.py can fall back to the rule-based matcher
in services.py instead of crashing. This is the reliability
behaviour described in the SRS (non-functional requirement 3).
"""

import os
import requests

AI_API_URL = "https://api.openai.com/v1/chat/completions"
AI_MODEL = "gpt-4o-mini"
REQUEST_TIMEOUT_SECONDS = 8


class AIUnavailableError(Exception):
    pass


def build_prompt(message, dietary_goal, inventory_names, budget_amount):
    """Turn the user's message + their stored context into one prompt string."""

    ingredients_text = ", ".join(inventory_names) if inventory_names else "nothing specific"

    return (
        f"The user's dietary goal is: {dietary_goal or 'none specified'}.\n"
        f"They currently have these ingredients at home: {ingredients_text}.\n"
        f"Their budget is: {budget_amount}.\n"
        f"User's message: \"{message}\"\n\n"
        "Suggest 2-3 simple meal ideas that fit their budget and goal, using "
        "different preparation styles rather than repeating the same dish. "
        "Keep the answer short and practical."
    )


def get_ai_reply(message, dietary_goal, inventory_names, budget_amount):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise AIUnavailableError("No AI API key configured")

    prompt = build_prompt(message, dietary_goal, inventory_names, budget_amount)

    try:
        response = requests.post(
            AI_API_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": AI_MODEL,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    except (requests.RequestException, KeyError, IndexError) as error:
        # Covers: no internet, timeout, bad response shape, API error, etc.
        raise AIUnavailableError(str(error))
