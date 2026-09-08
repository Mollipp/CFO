"""Strategy — opportunity radar and capability-gap intelligence."""

import html

import streamlit as st

from src import charts
from src.hud import clip_ui_text, render_html, safe_float


def render_strategy(s):
    escape = html.escape

    render_html(
        """
        <div class="module-code">Intelligence 07 / Strategic opportunity radar</div>
        <div class="section-title">Strategy Radar</div>
        <div class="section-subtitle">
            Public company facts are separated from synthetic management
            assessments. Strategic fit, attractiveness and capability scores are
            prototype decision-support inputs — not claims that a company is for
            sale, nor transaction recommendations.
        </div>
        """
    )

    top = s.top_strategy
    second = s.second_strategy

    if top is None:
        st.caption("No strategic radar data available.")
        return

    k1, k2, k3 = st.columns(3)

    with k1:
        render_html(
            f"""<div class="kpi-card" data-module="TOP / 07">
            <div class="kpi-label">TOP OPPORTUNITY</div>
            <div class="kpi-value" style="font-size:1.75rem;">{escape(str(top['company_name']))}</div>
            <div class="kpi-neutral">rank #{int(top['opportunity_rank'])} · {safe_float(top['overall_opportunity_score']):.1f}/100</div>
            <span class="micro-line"></span></div>"""
        )

    with k2:
        render_html(
            f"""<div class="kpi-card" data-module="FIT / 07">
            <div class="kpi-label">STRATEGIC FIT</div>
            <div class="kpi-value">{safe_float(top['strategic_fit_score']):.0f}</div>
            <div class="kpi-neutral">synthetic management score</div>
            <span class="micro-line"></span></div>"""
        )

    with k3:
        gap = s.top_capability_gap
        gap_name = escape(str(gap["capability"])) if gap is not None else "—"
        gap_value = safe_float(gap["capability_gap"]) if gap is not None else 0.0
        render_html(
            f"""<div class="kpi-card" data-module="GAP / 07">
            <div class="kpi-label">LARGEST CAPABILITY GAP</div>
            <div class="kpi-value" style="font-size:1.55rem;">{gap_name}</div>
            <div class="kpi-neutral">gap {gap_value:.0f} points</div>
            <span class="micro-line"></span></div>"""
        )

    if second is not None:
        pills = "".join(
            f'<span class="strategy-delta-pill">{escape(item)}</span>'
            for item in s.strategy_advantage_pills
        )
        render_html(
            f"""
            <div class="strategy-explainer">
                <div class="strategy-explainer-grid">
                    <div>
                        <div class="module-code">Why rank #1?</div>
                        <div class="strategy-score-bridge">
                            {escape(str(top['company_name']))} <span>{safe_float(top['overall_opportunity_score']):.1f}</span>
                            vs {escape(str(second['company_name']))} {safe_float(second['overall_opportunity_score']):.1f}
                        </div>
                    </div>
                    <div class="strategy-explainer-copy">
                        The opportunity map below shows only <strong>strategic fit</strong> and
                        <strong>financial attractiveness</strong>, which together represent 45% of the
                        composite score. The rank uses seven weighted dimensions, so the leader can
                        give up points on the two map axes and still rank first through integration
                        feasibility, affordability and time to value.
                        <div class="strategy-delta-strip">{pills}</div>
                    </div>
                </div>
            </div>
            """
        )

    render_html(
        f"""
        <div class="decision-strip">
            <div class="decision-strip-item">
                <span class="flow-label">Why #1</span>
                <strong>{escape(str(top['company_name']))} / {safe_float(top['overall_opportunity_score']):.1f}</strong>
                <span>Full seven-factor composite, not just the two map axes.</span>
            </div>
            <div class="decision-strip-item">
                <span class="flow-label">Impact</span>
                <strong>{escape(clip_ui_text(top['strategic_gap_addressed'], 72))}</strong>
                <span>{escape(clip_ui_text(top['strategic_rationale'], 110))}</span>
            </div>
            <div class="decision-strip-item">
                <span class="flow-label">Route</span>
                <strong>{escape(str(top['preferred_route']))}</strong>
                <span>Prototype management route, not a statement that the company is for sale.</span>
            </div>
            <div class="decision-strip-item">
                <span class="flow-label">Key risk</span>
                <strong>{escape(clip_ui_text(top['key_risk'], 78))}</strong>
                <span>Read alongside affordability, integration and regulatory complexity.</span>
            </div>
        </div>
        """
    )

    left, right = st.columns([1.35, 1])

    with left:
        render_html(
            """<div class="module-code">Opportunity matrix / 2 of 7 scoring dimensions</div>
            <div class="section-title">Strategic opportunity map</div>
            <div class="section-subtitle">
                X/Y show fit and financial attractiveness. Bubble size represents
                the full seven-factor composite score used for ranking.
            </div>"""
        )
        st.altair_chart(
            charts.build_strategy_radar_chart(s.strategic_radar, height=410),
            use_container_width=True,
        )

    with right:
        render_html(
            """<div class="module-code">Composite bridge / #1 vs #2</div>
            <div class="section-title">What drives the ranking?</div>"""
        )
        if second is not None and not s.strategy_delta.empty:
            st.altair_chart(
                charts.build_strategy_delta_chart(
                    s.strategy_delta,
                    str(top["company_name"]),
                    str(second["company_name"]),
                    height=250,
                ),
                use_container_width=True,
            )

        render_html(
            """<div class="module-code" style="margin-top:0.8rem;">Capability vector / Current-to-target gap</div>
            <div class="section-title">Capability gaps</div>"""
        )
        st.altair_chart(
            charts.build_capability_gap_chart(s.capability_gaps, height=245),
            use_container_width=True,
        )

    radar = s.strategic_radar
    if radar is not None and not radar.empty:
        display = radar[
            [
                "opportunity_rank",
                "company_name",
                "capability_domain",
                "strategic_fit_score",
                "financial_attractiveness_score",
                "integration_feasibility_score",
                "affordability_score",
                "time_to_value_score",
                "overall_opportunity_score",
            ]
        ].head(7).copy()
        display.columns = [
            "Rank",
            "Company",
            "Capability",
            "Strategic fit",
            "Financial attractiveness",
            "Integration",
            "Affordability",
            "Time to value",
            "Overall score",
        ]
        st.dataframe(display, width="stretch", hide_index=True)
