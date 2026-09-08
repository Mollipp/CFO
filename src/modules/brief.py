"""Morning Brief — change → why → impact → next."""

import html

import pandas as pd
import streamlit as st

from src import charts
from src.hud import clip_ui_text, investigate_url, navigate_to_module, render_html

BRIEF_COPILOT_PROMPT = (
    "Based on the latest CFO morning brief, explain what changed in NIM, "
    "deposits and credit, why the observed data may matter, quantify the "
    "financial impact available in the certified views, and recommend the next "
    "investigation. Separate facts from interpretation and do not invent "
    "causality."
)


def _flow_card(number, title, change_label, change, why, impact, next_copy, topic):
    """One movement, laid out as change / why / impact / next."""
    return f"""
    <div class="decision-flow-card">
        <div class="flow-title">{number} / {title}</div>
        <div class="flow-grid">
            <div class="flow-cell">
                <span class="flow-label">{change_label}</span>
                <span class="flow-copy">{change}</span>
            </div>
            <div class="flow-cell">
                <span class="flow-label">Why</span>
                <span class="flow-copy">{why}</span>
            </div>
            <div class="flow-cell">
                <span class="flow-label">Impact</span>
                <span class="flow-copy">{impact}</span>
            </div>
            <div class="flow-cell">
                <span class="flow-label">Next</span>
                <span class="flow-copy">{next_copy}</span>
                <a class="copilot-action" href="{investigate_url(topic)}" target="_self">Ask Copilot →</a>
            </div>
        </div>
    </div>
    """


def _news_card(article):
    escape = html.escape
    return f"""
    <div class="news-card">
        <div class="news-topline">
            <span class="news-badge">News</span>
            <span class="news-meta">{escape(str(article['source']))} · {pd.to_datetime(article['published_date']).strftime('%d %b')} · {escape(str(article.get('category', 'External development')))}</span>
        </div>
        <div class="news-headline">{escape(str(article['headline']))}</div>
        <div class="news-context-grid">
            <div class="news-context-line">
                <span class="news-context-label">Why it matters</span>
                <span class="news-context-copy">{escape(clip_ui_text(article.get('bank_impact_summary', ''), 112))}</span>
            </div>
            <div class="news-context-line">
                <span class="news-context-label">Potential metric</span>
                <span class="news-context-copy">{escape(str(article['primary_affected_metric']))}</span>
            </div>
            <div class="news-context-line">
                <span class="news-context-label">Next</span>
                <span class="news-context-copy">{escape(clip_ui_text(article.get('suggested_action', ''), 96))}</span>
            </div>
        </div>
        <div class="news-footer">
            <a class="news-source-link" href="{escape(str(article['source_url']), quote=True)}" target="_blank" rel="noopener noreferrer">Open article ↗</a>
            <span class="news-public-note">Public source · bank impact is prototype analysis</span>
        </div>
    </div>
    """


def render_brief(s):
    render_html(
        """
        <div class="module-code">Morning brief / executive view</div>
        <div class="section-title">What changed — and what should I do with it?</div>
        <div class="section-subtitle">
            Three movements worth reviewing this morning, each shown against its
            reference period with the financial implication and a direct path to
            investigate further.
        </div>
        """
    )

    render_html(
        f"""
        <div class="comparison-basis">
            <span class="comparison-chip"><strong>NIM</strong> vs {s.previous_month_label} / prior month</span>
            <span class="comparison-chip"><strong>Deposits</strong> vs 30 days prior</span>
            <span class="comparison-chip"><strong>Credit</strong> vs 30 days prior</span>
        </div>
        """
    )

    credit_change = (
        "comparison unavailable"
        if s.credit_hotspot_stage2_delta_pp is None
        else f"{s.credit_hotspot_stage2_delta_pp:+.2f}pp"
    )

    render_html(
        _flow_card(
            "01",
            "Net interest margin",
            "Change vs prior month",
            f"NIM {s.cert_current_nim:.2f}% · {s.nim_mom_bps:+.1f} bps vs {s.previous_month_label}",
            s.nim_why,
            s.nim_impact,
            s.nim_next,
            "nim",
        )
        + _flow_card(
            "02",
            "Deposits and funding",
            "Change vs 30 days prior",
            f"Deposits {s.total_deposit_30d_change_pct:+.2f}% · €{s.total_deposit_30d_change_m / 1000:+.2f}bn",
            s.deposit_why,
            s.deposit_impact,
            s.deposit_next,
            "deposits",
        )
        + _flow_card(
            "03",
            "Credit migration",
            "Change vs 30 days prior",
            f"{s.credit_signal_primary} · {credit_change}",
            s.credit_why,
            s.credit_impact,
            s.credit_next,
            "credit",
        )
    )

    left, right = st.columns([1.4, 1])

    with left:
        render_html(
            """<div class="module-code">Performance trend</div>
            <div class="section-title">NIM trajectory</div>"""
        )
        st.altair_chart(
            charts.build_nim_chart(s.monthly_nim, height=290),
            use_container_width=True,
        )

        render_html(
            """<div class="module-code" style="margin-top:.8rem;">Funding trend</div>
            <div class="section-title">30-day deposit movement by country</div>"""
        )
        st.altair_chart(
            charts.build_deposit_country_chart(s.deposit_country, height=235),
            use_container_width=True,
        )

    with right:
        render_html(
            """
            <div class="news-section-head">
                <div>
                    <div class="module-code">External news / public sources</div>
                    <div class="section-title">Latest developments</div>
                </div>
                <div class="news-section-copy">
                    Recent public news with a prepared view of why it may matter to the bank.
                </div>
            </div>
            """
        )

        if s.news_recent is not None and not s.news_recent.empty:
            for _, article in s.news_recent.head(3).iterrows():
                render_html(_news_card(article))
        else:
            st.caption("No recent public-news records available.")

        if st.button(
            "Investigate the morning brief with CFO Copilot →",
            key="brief_to_copilot",
            width="stretch",
        ):
            st.session_state["brief_copilot_prompt"] = BRIEF_COPILOT_PROMPT
            navigate_to_module("copilot")
