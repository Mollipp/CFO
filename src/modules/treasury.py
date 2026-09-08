"""Treasury — portfolio sensitivity, scenarios and hedge alternatives."""

import html

import streamlit as st

from src import charts
from src.cockpit_views import load_treasury_portfolio
from src.hud import render_html, safe_float


def render_treasury(s):
    render_html(
        """
        <div class="module-code">Intelligence 05 / Treasury and hedge intelligence</div>
        <div class="section-title">Treasury Pulse</div>
        <div class="section-subtitle">
            Portfolio sensitivity, predefined market-risk scenarios and
            deterministic hedge alternatives. Economic value, OCI and immediate
            P&amp;L remain explicitly separated.
        </div>
        """
    )

    hedge = s.strongest_hedge
    hedge_name = (
        html.escape(str(hedge["hedge_name"]))
        if hedge is not None
        else "No predefined hedge available"
    )
    hedge_reduction = safe_float(hedge["dv01_reduction_pct"]) if hedge is not None else 0.0
    hedge_carry = (
        safe_float(hedge["estimated_annual_carry_m"]) if hedge is not None else 0.0
    )

    change_copy = (
        f"Market value {s.treasury_market_trend_text} ({s.treasury_market_trend_label})"
        if s.treasury_market_change_m is not None
        else (
            "No prior treasury snapshot is available, so day-over-day "
            "market-value change cannot yet be measured."
        )
    )

    render_html(
        f"""
        <div class="decision-strip">
            <div class="decision-strip-item">
                <span class="flow-label">Change</span>
                <strong>{change_copy}</strong>
                <span>Trend appears automatically once a prior snapshot exists.</span>
            </div>
            <div class="decision-strip-item">
                <span class="flow-label">Why</span>
                <strong>Duration {s.treasury_duration:.2f}y · DV01 €{s.treasury_dv01:.1f}m/bp</strong>
                <span>These sensitivity measures explain why parallel rate moves affect economic value.</span>
            </div>
            <div class="decision-strip-item">
                <span class="flow-label">Impact</span>
                <strong>+50bp → {s.treasury_rate50_text}</strong>
                <span>Economic-value impact; OCI and immediate P&amp;L are reported separately below.</span>
            </div>
            <div class="decision-strip-item">
                <span class="flow-label">Next option</span>
                <strong>{hedge_name}</strong>
                <span>Largest predefined DV01 reduction: {hedge_reduction:.0f}% · carry €{hedge_carry:+,.0f}m/year. Prototype option, not a trading recommendation.</span>
            </div>
        </div>
        """
    )

    t1, t2, t3, t4 = st.columns(4)

    with t1:
        render_html(
            f"""<div class="kpi-card" data-module="MKT / 05">
            <div class="kpi-label">MARKET VALUE</div>
            <div class="kpi-value">€{s.treasury_market_value_m / 1000:.1f}bn</div>
            <div class="{s.treasury_market_trend_css}">{s.treasury_market_trend_label}: {s.treasury_market_trend_text}</div>
            <span class="micro-line"></span></div>"""
        )

    with t2:
        render_html(
            f"""<div class="kpi-card" data-module="RISK / 05">
            <div class="kpi-label">PORTFOLIO DV01</div>
            <div class="kpi-value">€{s.treasury_dv01:.1f}m</div>
            <div class="kpi-neutral">per 1 bp parallel rate move</div>
            <span class="micro-line"></span></div>"""
        )

    with t3:
        render_html(
            f"""<div class="kpi-card" data-module="DUR / 05">
            <div class="kpi-label">MODIFIED DURATION</div>
            <div class="kpi-value">{s.treasury_duration:.2f}y</div>
            <div class="kpi-neutral">market-value weighted</div>
            <span class="micro-line"></span></div>"""
        )

    with t4:
        impact_css = "kpi-alert" if s.treasury_rate50_impact_m < 0 else "kpi-track"
        render_html(
            f"""<div class="kpi-card" data-module="SIM / 05">
            <div class="kpi-label">RATES +50BP</div>
            <div class="kpi-value">{s.treasury_rate50_text}</div>
            <div class="{impact_css}">economic-value impact</div>
            <span class="micro-line"></span></div>"""
        )

    left, right = st.columns([1.25, 1])

    with left:
        render_html(
            """<div class="module-code">Scenario lattice / Portfolio outputs</div>
            <div class="section-title">Market-risk scenarios</div>"""
        )
        st.altair_chart(
            charts.build_treasury_scenario_chart(s.treasury_scenarios, height=300),
            use_container_width=True,
        )
        st.caption(
            "Scenario outputs come straight from the treasury scenario dataset; "
            "the UI does not reprice the portfolio."
        )

        portfolio = load_treasury_portfolio()
        composition_left, composition_right = st.columns(2)
        with composition_left:
            render_html("""<div class="module-code">Market value by asset class</div>""")
            st.altair_chart(
                charts.build_treasury_asset_class_chart(portfolio, height=230),
                use_container_width=True,
            )
        with composition_right:
            render_html("""<div class="module-code">DV01 by maturity bucket</div>""")
            st.altair_chart(
                charts.build_treasury_dv01_chart(portfolio, height=230),
                use_container_width=True,
            )

    with right:
        render_html(
            """<div class="module-code">Hedge lattice / Predefined alternatives</div>
            <div class="section-title">Hedge options</div>"""
        )

        hedges = s.hedge_options
        if hedges is not None and not hedges.empty:
            best = hedges.sort_values("dv01_reduction_pct", ascending=False).iloc[0]
            render_html(
                f"""
                <div class="feature-callout">
                    <div class="feature-callout-title">Largest DV01 reduction / {html.escape(str(best['hedge_name']))}</div>
                    <div class="feature-callout-copy">
                        Indicative notional €{safe_float(best['hedge_notional_m']) / 1000:.1f}bn ·
                        DV01 reduction {safe_float(best['dv01_reduction_pct']):.0f}% ·
                        annual carry €{safe_float(best['estimated_annual_carry_m']):+,.0f}m.
                        Prototype estimate, not an executable trading recommendation.
                    </div>
                </div>
                """
            )

            display = hedges[
                [
                    "hedge_name",
                    "hedge_notional_m",
                    "dv01_reduction_pct",
                    "rates_plus_50bp_pnl_after_m",
                    "estimated_annual_carry_m",
                ]
            ].copy()
            display.columns = [
                "Hedge",
                "Notional (€m)",
                "DV01 reduction (%)",
                "+50bp impact after hedge (€m)",
                "Annual carry (€m)",
            ]
            st.dataframe(display, width="stretch", hide_index=True)
        else:
            st.caption("No hedge alternatives available.")

    if s.treasury_market_change_m is None:
        st.info(
            "The treasury dataset contains a single snapshot, so a genuine "
            "day-over-day move cannot be shown yet. The cockpit is wired to "
            "display the change automatically once a previous snapshot exists."
        )
