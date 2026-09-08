import os

from dotenv import load_dotenv
from google import genai

load_dotenv()


def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to the .env file in the "
            "project root, then restart Streamlit."
        )

    return genai.Client(api_key=api_key)


def build_cockpit_facts(df) -> dict:
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
            "total_capital_ratio_pct": round(float(latest["total_capital_ratio_pct"]), 2),
            "lcr_pct": round(float(latest["lcr_pct"]), 1),
            "nim_pct": round(float(latest["nim_pct"]), 2),
            "cost_to_income_pct": round(float(latest["cost_to_income_pct"]), 1),
            "stage_3_ratio_pct": round(float(latest["stage_3_ratio_pct"]), 2),
            "loan_growth_yoy_pct": round(float(latest["loan_growth_yoy_pct"]), 2),
            "deposit_growth_yoy_pct": round(float(latest["deposit_growth_yoy_pct"]), 2),
            "deposit_movement_eur_m": round(float(latest["deposit_movement"]), 0),
            "rwa_eur_m": round(float(latest["rwa"]), 0),
            "ead_eur_m": round(float(latest["ead"]), 0),
            "gca_eur_m": round(float(latest["gca"]), 0),
            "provisions_eur_m": round(float(latest["provisions"]), 0),
            "nii_monthly_eur_m": round(float(latest["nii"]), 0),
        },
        "monthly_changes": {
            "cet1_ratio_pp": round(float(latest["cet1_ratio_pct"] - previous["cet1_ratio_pct"]), 2),
            "lcr_pp": round(float(latest["lcr_pct"] - previous["lcr_pct"]), 1),
            "nim_pp": round(float(latest["nim_pct"] - previous["nim_pct"]), 2),
            "cost_to_income_pp": round(float(latest["cost_to_income_pct"] - previous["cost_to_income_pct"]), 1),
            "stage_3_ratio_pp": round(float(latest["stage_3_ratio_pct"] - previous["stage_3_ratio_pct"]), 2),
        },
    }


def build_executive_prompt(user_question: str, facts: dict) -> str:
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


def generate_gemini_response(user_question: str, facts: dict, model: str = "gemini-3.6-flash") -> str:
    client = get_gemini_client()
    prompt = build_executive_prompt(user_question, facts)
    response = client.models.generate_content(model=model, contents=prompt)

    if not response.text:
        return (
            "Gemini returned an empty response. Please retry or check "
            "the API key, quota, and selected model in Google AI Studio."
        )

    return response.text
