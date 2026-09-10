import os
from typing import Any

import requests

PURPOSE = "hcktgpt56terra"

URL = (
    f"https://xdp-bifrost-atls-a.nl.eu.abnamro.com/"
    f"aigwacc/openai/v1/openai/deployments/{PURPOSE}/chat/completions"
    "?api-version=2024-10-21"
)


BEARER_TOKEN = ""

def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"{name} is missing. Configure it as an application "
            "environment variable or Streamlit secret."
        )

    return value


def _post_chat_completions(
    messages: list[dict],
    model: str | None = None,
) -> str:

    purpose = model or PURPOSE

    url = URL

    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        url=url,
        json={"messages": messages},
        headers=headers,
        timeout=60,
        verify=False,
    )

    response.raise_for_status()

    data = response.json()

    choices = data.get("choices", [])

    if not choices:
        raise RuntimeError(
            f"The corporate LLM returned no choices: {data}"
        )

    text = choices[0].get("message", {}).get("content")

    if not text:
        raise RuntimeError(
            "The corporate LLM returned an empty response."
        )

    return text


def build_cockpit_facts(df) -> dict[str, Any]:
    latest = df.iloc[-1]
    previous = df.iloc[-2]

    return {
        "reporting_date": str(df.index[-1].date()),
        "data_notice": (
            "All data are synthetic and illustrative, calibrated only to the "
            "approximate scale of a Dutch universal bank. They are not "
            "actual ABN AMRO data."
        ),
        "current_metrics": {
            "cet1_ratio_pct": round(float(latest["cet1_ratio_pct"]), 2),
            "tier1_ratio_pct": round(float(latest["tier1_ratio_pct"]), 2),
            "total_capital_ratio_pct": round(
                float(latest["total_capital_ratio_pct"]), 2
            ),
            "lcr_pct": round(float(latest["lcr_pct"]), 1),
            "nim_pct": round(float(latest["nim_pct"]), 2),
            "cost_to_income_pct": round(
                float(latest["cost_to_income_pct"]), 1
            ),
            "stage_3_ratio_pct": round(
                float(latest["stage_3_ratio_pct"]), 2
            ),
            "loan_growth_yoy_pct": round(
                float(latest["loan_growth_yoy_pct"]), 2
            ),
            "deposit_growth_yoy_pct": round(
                float(latest["deposit_growth_yoy_pct"]), 2
            ),
            "deposit_movement_eur_m": round(
                float(latest["deposit_movement"]), 0
            ),
            "rwa_eur_m": round(float(latest["rwa"]), 0),
            "ead_eur_m": round(float(latest["ead"]), 0),
            "gca_eur_m": round(float(latest["gca"]), 0),
            "provisions_eur_m": round(float(latest["provisions"]), 0),
            "nii_monthly_eur_m": round(float(latest["nii"]), 0),
        },
        "monthly_changes": {
            "cet1_ratio_pp": round(
                float(latest["cet1_ratio_pct"] - previous["cet1_ratio_pct"]), 2
            ),
            "lcr_pp": round(
                float(latest["lcr_pct"] - previous["lcr_pct"]), 1
            ),
            "nim_pp": round(
                float(latest["nim_pct"] - previous["nim_pct"]), 2
            ),
            "cost_to_income_pp": round(
                float(latest["cost_to_income_pct"] - previous["cost_to_income_pct"]), 1
            ),
            "stage_3_ratio_pp": round(
                float(latest["stage_3_ratio_pct"] - previous["stage_3_ratio_pct"]), 2
            ),
        },
    }


def build_executive_prompt(user_question: str, facts: dict[str, Any]) -> str:
    return f"""
You are an AI Financial Partner assisting a European bank CFO.

This is a hackathon prototype. All supplied data are SYNTHETIC and
ILLUSTRATIVE. They are not actual ABN AMRO data.

Strict rules:
1. Use ONLY the dashboard facts supplied below.
2. Never invent numbers, market news, peer comparisons, regulations,
   targets, root causes, or data sources.
3. Do not perform new calculations. Use values already supplied.
4. If the question cannot be answered from the facts, state precisely
   which missing data would be required.
5. You cannot execute actions. Frame recommendations as options for
   CFO review only.
6. Keep the response concise, CFO-ready, and fact-based.
7. Use short headings and bullets where they improve readability.
8. Explicitly call the output illustrative when giving recommendations.

CFO question:
{user_question}

Verified dashboard facts:
{facts}
"""


def generate_openai_response(
    user_question: str,
    facts: dict[str, Any],
) -> str:

    headers = {
        "Authorization": "Bearer " + BEARER_TOKEN,
        "Content-Type": "application/json",
    }

    request_body = {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an AI Financial Partner assisting "
                    "a European bank CFO."
                ),
            },
            {
                "role": "user",
                "content": build_executive_prompt(
                    user_question,
                    facts,
                ),
            },
        ]
    }

    response = requests.post(
        verify=False,
        url=URL,
        json=request_body,
        headers=headers,
        timeout=60,
    )

    response.raise_for_status()

    response_data = response.json()

    return response_data["choices"][0]["message"]["content"]


def generate_prompt_response(prompt: str, model: str | None = None) -> str:
    """Call the corporate LLM with a single user-turn prompt."""
    return _post_chat_completions(
        [{"role": "user", "content": prompt}], model
    )


def test_llm() -> dict:
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "say hello in dutch"},
    ]
    text = _post_chat_completions(messages)
    return {"status": "ok", "response": text}