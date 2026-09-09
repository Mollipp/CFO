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


def _domain_tile(tile):
    """One KPI: the number, its movement, and the first line of the reading."""
    return f"""
        <div class="domain-tile tone-{tile['tone']}" data-tile="{tile['index']}" tabindex="0">
            <div class="domain-tile-top">
                <span class="domain-tile-label">{tile['label']}</span>
                <span class="domain-tile-code">{tile['code']}</span>
            </div>
            <div class="domain-tile-value">{tile['value']}</div>
            <div class="domain-tile-delta"><span class="domain-tile-dot"></span>{tile['delta']}</div>
            <div class="domain-tile-why"><span>Why</span>{tile['why_short']}</div>
            <span class="domain-tile-more">Impact + action</span>
        </div>
    """


def _domain_detail(tile):
    """The full reading, revealed in the panel's stage when a tile is held."""
    return f"""
        <div class="domain-detail" data-tile="{tile['index']}">
            <div class="domain-detail-head">
                <span>{tile['label']}</span>
                <span class="domain-tile-code">{tile['code']}</span>
            </div>
            <div class="domain-detail-row">
                <span class="domain-detail-tag">Why</span>
                <p class="domain-detail-copy">{tile['why']}</p>
            </div>
            <div class="domain-detail-row">
                <span class="domain-detail-tag">Impact</span>
                <p class="domain-detail-copy">{tile['impact']}</p>
            </div>
            <div class="domain-detail-row">
                <span class="domain-detail-tag">Next</span>
                <p class="domain-detail-copy">{tile['next']}</p>
            </div>
            <a class="copilot-action" href="{investigate_url(tile['topic'])}" target="_self">Ask Copilot →</a>
        </div>
    """


def _domain_panel(domain):
    """One supervisory domain: its KPIs above a shared explanation stage."""
    tiles = "".join(_domain_tile(tile) for tile in domain["tiles"])
    details = "".join(_domain_detail(tile) for tile in domain["tiles"])

    return f"""
    <section class="domain-panel">
        <div class="domain-panel-head">
            <span class="domain-panel-code">{domain['code']}</span>
            <span class="domain-panel-metrics">{domain['metrics']}</span>
        </div>
        <div class="domain-panel-title">{domain['name']}</div>
        <div class="domain-panel-body">
            {tiles}
            <div class="domain-stage">
                <div class="domain-stage-hint">
                    <span class="domain-stage-glyph">◎</span>
                    Hover to preview · select a KPI to keep impact and action open
                </div>
                {details}
            </div>
        </div>
    </section>
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
        <div class="section-title">The bank this morning, by domain</div>
        <div class="section-subtitle">
            Earnings, balance sheet, capital and risk, each read against its own
            reference period. Hover a KPI for why it moved, what it is worth and
            what to do next; select it to keep that reading open.
        </div>
        """
    )

    render_html(
        '<div class="domain-grid">'
        + "".join(_domain_panel(domain) for domain in s.domain_grid)
        + "</div>"
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
