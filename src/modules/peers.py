"""Peers — directional European peer positioning."""

import streamlit as st

from src import charts
from src.hud import render_html


def render_peers(s):
    render_html(
        """
        <div class="module-code">Intelligence 06 / European peer positioning</div>
        <div class="section-title">Peer Benchmarking</div>
        <div class="section-subtitle">
            Directional comparison with public FY2025 peer disclosures. Peer
            profitability mixes ROE, RoTE and Net RoTE; our bank is shown using
            its annualised YTD ROE proxy, so return comparisons are not fully
            like-for-like.
        </div>
        """
    )

    p1, p2, p3 = st.columns(3)

    with p1:
        render_html(
            f"""<div class="kpi-card" data-module="RET / 06">
            <div class="kpi-label">OUR ROE PROXY</div>
            <div class="kpi-value">{s.ytd_roe_proxy:.1f}%</div>
            <div class="kpi-neutral">peer median {s.peer_profitability_median:.1f}%</div>
            <span class="micro-line"></span></div>"""
        )

    with p2:
        render_html(
            f"""<div class="kpi-card" data-module="CAP / 06">
            <div class="kpi-label">OUR CET1</div>
            <div class="kpi-value">{s.cet1_ratio:.1f}%</div>
            <div class="kpi-neutral">peer median {s.peer_cet1_median:.1f}%</div>
            <span class="micro-line"></span></div>"""
        )

    with p3:
        render_html(
            f"""<div class="kpi-card" data-module="EFF / 06">
            <div class="kpi-label">OUR COST / INCOME</div>
            <div class="kpi-value">{s.ytd_cost_income:.1f}%</div>
            <div class="kpi-neutral">peer median {s.peer_cost_income_median:.1f}%</div>
            <span class="micro-line"></span></div>"""
        )

    gap_word = "below" if s.roe_peer_gap_pp < 0 else "above"
    efficiency_word = (
        "better"
        if s.efficiency_peer_advantage_pp > 0
        else "worse"
        if s.efficiency_peer_advantage_pp < 0
        else "in line"
    )

    render_html(
        f"""
        <div class="decision-strip">
            <div class="decision-strip-item">
                <span class="flow-label">Gap</span>
                <strong>ROE proxy {abs(s.roe_peer_gap_pp):.1f}pp {gap_word} median</strong>
                <span>Directional only, because peers mix ROE, RoTE and Net RoTE.</span>
            </div>
            <div class="decision-strip-item">
                <span class="flow-label">Why</span>
                <strong>CET1 {s.cet1_peer_gap_pp:+.1f}pp vs median</strong>
                <span>Capital position and reported return should be read together, not as a one-dimensional ranking.</span>
            </div>
            <div class="decision-strip-item">
                <span class="flow-label">Impact</span>
                <strong>Cost/income {abs(s.efficiency_peer_advantage_pp):.1f}pp {efficiency_word} than median</strong>
                <span>Shows whether the return gap is accompanied by an efficiency gap.</span>
            </div>
            <div class="decision-strip-item">
                <span class="flow-label">Next</span>
                <strong>Investigate return levers</strong>
                <span>Separate revenue/NII, fee income, cost and capital-deployment drivers before drawing conclusions.</span>
            </div>
        </div>
        """
    )

    left, right = st.columns([1.45, 1])

    with left:
        render_html(
            """<div class="module-code">Position matrix / Return × capital</div>
            <div class="section-title">Where do we sit?</div>"""
        )
        st.altair_chart(
            charts.build_peer_positioning_chart(s.peer_plot, height=400),
            use_container_width=True,
        )

    with right:
        render_html(
            """<div class="module-code">Peer ledger / Public disclosures</div>
            <div class="section-title">Comparison set</div>"""
        )
        peers = s.peer_benchmark
        if peers is not None and not peers.empty:
            display = peers[
                [
                    "bank_name",
                    "reported_return_pct",
                    "return_metric_type",
                    "cet1_ratio_pct",
                    "cost_income_ratio_pct",
                ]
            ].copy()
            display.columns = [
                "Bank",
                "Return (%)",
                "Metric",
                "CET1 (%)",
                "Cost / income (%)",
            ]
            st.dataframe(
                display, width="stretch", hide_index=True, height=410
            )
        else:
            st.caption("No peer disclosures available.")
