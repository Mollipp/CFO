import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.data_generator import generate_bank_history
from src.metrics import calculate_metrics
from src.scenarios import run_scenario
from src.forecasting import forecast_metrics
from src.ai_partner import answer_question, build_morning_briefing
from src.gemini_partner import build_cockpit_facts, generate_gemini_response
from src.extended_data_loader import datasets_available
from src.tab_news_intelligence import render_news_intelligence_tab
from src.tab_treasury import render_treasury_tab
from src.tab_peer_benchmarking import render_peer_benchmarking_tab
from src.tab_strategic_radar import render_strategic_radar_tab

from src.news_partner import load_articles, extract_signals
from src.news_ui import (
    apply_pending_signals,
    render_overnight_signals_panel,
    render_signal_apply_panel,
    render_provenance_banner,
    add_horizon_signal_annotation,
)

st.set_page_config(
    page_title="AI-Native Morning Cockpit",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_data():
    raw_history = generate_bank_history(months=48, seed=20260826)
    return calculate_metrics(raw_history)


def metric_delta(current, previous, suffix="", decimals=2):
    """Return a display-ready metric delta."""
    difference = current - previous
    return f"{difference:+.{decimals}f}{suffix}"


def status_label(value, amber_threshold, red_threshold, lower_is_better=False):
    """
    Return Green / Amber / Red based on a metric threshold.

    For CET1 and LCR, a lower value is worse.
    For cost-to-income and Stage 3 ratio, a higher value is worse.
    """
    if lower_is_better:
        if value >= red_threshold:
            return "🔴 Red"
        if value >= amber_threshold:
            return "🟠 Amber"
        return "🟢 Green"

    if value <= red_threshold:
        return "🔴 Red"
    if value <= amber_threshold:
        return "🟠 Amber"
    return "🟢 Green"


def format_eur_millions(value):
    return f"€{value:,.0f}m"


@st.cache_data(show_spinner="Extracting overnight news signals...")
def load_extracted_signals():
    """
    Run the Gemini news-signal extractor over the fixture articles.
    Cached so Gemini is called once per session, not on every rerun.
    """
    articles = load_articles()
    all_signals = []
    for article in articles:
        try:
            signals = extract_signals(article)
        except Exception:
            signals = []
        for sig in signals:
            sig["_article"] = article
        all_signals.extend(signals)
    return all_signals


df = load_data()
latest = df.iloc[-1]
previous = df.iloc[-2]

try:
    extracted_signals = load_extracted_signals()
except Exception as error:
    extracted_signals = []
    st.sidebar.warning(f"News signal extraction unavailable: {error}")

st.title("🏦 AI-Native Morning Cockpit")
st.caption(
    "The shaded band is a 95% confidence interval around the estimated "
    "mean linear trend. It is not a full stress-test range or prediction interval."
)

with st.sidebar:
    st.header("Cockpit controls")

    selected_period = st.selectbox(
        "Trend history",
        options=[12, 24, 48],
        index=1,
        format_func=lambda months: f"Last {months} months",
    )

    st.divider()
    st.caption("Dashboard status")
    st.success("Data refresh complete")
    st.caption("Synthetic data — not for financial decisions")

    st.divider()
    st.caption("Extended datasets")
    dataset_status = datasets_available()
    missing_datasets = [name for name, ok in dataset_status.items() if not ok]
    if missing_datasets:
        st.warning(
            f"{len(missing_datasets)} extended dataset(s) not yet generated. "
            "Run `python -m src.generators.generate_all_data`."
        )
    else:
        st.success("All extended datasets loaded.")

tab_health, tab_scenario, tab_horizon, tab_ai, tab_news, tab_treasury, tab_peers, tab_strategy = st.tabs(
    [
        "Morning Health Check",
        "What-If Engine",
        "Horizon View",
        "AI Financial Partner",
        "News Intelligence",
        "Treasury & Hedging",
        "Peer Benchmarking",
        "Strategic Radar",
    ]
)

with tab_health:
    st.subheader("Executive snapshot")

    health_col1, health_col2, health_col3, health_col4 = st.columns(4)

    health_col1.metric(
        "CET1 ratio",
        f"{latest['cet1_ratio_pct']:.2f}%",
        metric_delta(
            latest["cet1_ratio_pct"],
            previous["cet1_ratio_pct"],
            " pp",
        ),
    )

    health_col2.metric(
        "Liquidity Coverage Ratio",
        f"{latest['lcr_pct']:.0f}%",
        metric_delta(
            latest["lcr_pct"],
            previous["lcr_pct"],
            " pp",
            decimals=0,
        ),
    )

    health_col3.metric(
        "Net Interest Margin",
        f"{latest['nim_pct']:.2f}%",
        metric_delta(
            latest["nim_pct"],
            previous["nim_pct"],
            " pp",
        ),
    )

    health_col4.metric(
        "Cost-to-Income Ratio",
        f"{latest['cost_to_income_pct']:.1f}%",
        metric_delta(
            latest["cost_to_income_pct"],
            previous["cost_to_income_pct"],
            " pp",
            decimals=1,
        ),
    )

    st.divider()

    render_overnight_signals_panel(extracted_signals)

    st.divider()

    st.subheader("Risk status")

    status_data = pd.DataFrame(
        {
            "Pillar": [
                "Capital",
                "Liquidity",
                "Earnings",
                "Asset Quality",
            ],
            "Key metric": [
                "CET1 ratio",
                "LCR",
                "Cost-to-income",
                "Stage 3 ratio",
            ],
            "Current value": [
                f"{latest['cet1_ratio_pct']:.2f}%",
                f"{latest['lcr_pct']:.0f}%",
                f"{latest['cost_to_income_pct']:.1f}%",
                f"{latest['stage_3_ratio_pct']:.2f}%",
            ],
            "Status": [
                status_label(
                    latest["cet1_ratio_pct"],
                    amber_threshold=14.5,
                    red_threshold=13.75,
                ),
                status_label(
                    latest["lcr_pct"],
                    amber_threshold=130,
                    red_threshold=110,
                ),
                status_label(
                    latest["cost_to_income_pct"],
                    amber_threshold=60,
                    red_threshold=70,
                    lower_is_better=True,
                ),
                status_label(
                    latest["stage_3_ratio_pct"],
                    amber_threshold=2.5,
                    red_threshold=3.5,
                    lower_is_better=True,
                ),
            ],
        }
    )

    st.dataframe(status_data, hide_index=True, use_container_width=True)

    selected_history = df.tail(selected_period).copy()

    left_chart, right_chart = st.columns(2)

    with left_chart:
        st.subheader("Capital and liquidity trend")

        capital_liquidity = selected_history[
            [
                "cet1_ratio_pct",
                "tier1_ratio_pct",
                "total_capital_ratio_pct",
                "lcr_pct",
            ]
        ].rename(
            columns={
                "cet1_ratio_pct": "CET1 ratio",
                "tier1_ratio_pct": "Tier 1 ratio",
                "total_capital_ratio_pct": "Total capital ratio",
                "lcr_pct": "LCR",
            }
        )

        fig_capital = px.line(
            capital_liquidity,
            x=capital_liquidity.index,
            y=capital_liquidity.columns,
            labels={"value": "Percent", "date": "Month-end"},
        )

        fig_capital.add_hline(
            y=13.75,
            line_dash="dash",
            line_color="red",
            annotation_text="Illustrative CET1 threshold",
        )

        fig_capital.update_layout(
            height=390,
            legend_title_text="Metric",
            margin=dict(l=10, r=10, t=30, b=10),
        )

        st.plotly_chart(fig_capital, use_container_width=True)

    with right_chart:
        st.subheader("Earnings and efficiency trend")

        earnings_efficiency = selected_history[
            [
                "nim_pct",
                "cost_to_income_pct",
                "pre_tax_profit_margin_pct",
            ]
        ].rename(
            columns={
                "nim_pct": "NIM",
                "cost_to_income_pct": "Cost-to-income",
                "pre_tax_profit_margin_pct": "Pre-tax profit margin",
            }
        )

        fig_earnings = px.line(
            earnings_efficiency,
            x=earnings_efficiency.index,
            y=earnings_efficiency.columns,
            labels={"value": "Percent", "date": "Month-end"},
        )

        fig_earnings.update_layout(
            height=390,
            legend_title_text="Metric",
            margin=dict(l=10, r=10, t=30, b=10),
        )

        st.plotly_chart(fig_earnings, use_container_width=True)

    left_chart, right_chart = st.columns(2)

    with left_chart:
        st.subheader("Balance-sheet movements")

        balance_sheet = selected_history[
            ["loans", "deposits"]
        ].rename(
            columns={
                "loans": "Loans",
                "deposits": "Deposits",
            }
        )

        fig_balance_sheet = px.line(
            balance_sheet,
            x=balance_sheet.index,
            y=balance_sheet.columns,
            labels={"value": "EUR millions", "date": "Month-end"},
        )

        fig_balance_sheet.update_layout(
            height=360,
            legend_title_text="Metric",
            margin=dict(l=10, r=10, t=30, b=10),
        )

        st.plotly_chart(fig_balance_sheet, use_container_width=True)

    with right_chart:
        st.subheader("Asset quality")

        asset_quality = selected_history[
            [
                "stage_2_share_pct",
                "stage_3_ratio_pct",
                "coverage_ratio_pct",
            ]
        ].rename(
            columns={
                "stage_2_share_pct": "Stage 2 ratio",
                "stage_3_ratio_pct": "Stage 3 ratio",
                "coverage_ratio_pct": "Provision coverage",
            }
        )

        fig_asset_quality = px.line(
            asset_quality,
            x=asset_quality.index,
            y=asset_quality.columns,
            labels={"value": "Percent", "date": "Month-end"},
        )

        fig_asset_quality.update_layout(
            height=360,
            legend_title_text="Metric",
            margin=dict(l=10, r=10, t=30, b=10),
        )

        st.plotly_chart(fig_asset_quality, use_container_width=True)

    st.subheader("Latest underlying drivers")

    driver_col1, driver_col2, driver_col3, driver_col4 = st.columns(4)

    driver_col1.metric("Loans", format_eur_millions(latest["loans"]))
    driver_col2.metric("Deposits", format_eur_millions(latest["deposits"]))
    driver_col3.metric("RWA", format_eur_millions(latest["rwa"]))
    driver_col4.metric("Provisions", format_eur_millions(latest["provisions"]))

    driver_col1, driver_col2, driver_col3, driver_col4 = st.columns(4)

    driver_col1.metric("EAD", format_eur_millions(latest["ead"]))
    driver_col2.metric("GCA", format_eur_millions(latest["gca"]))
    driver_col3.metric(
        "Loan growth, YoY",
        f"{latest['loan_growth_yoy_pct']:.2f}%",
    )
    driver_col4.metric(
        "Deposit movement",
        format_eur_millions(latest["deposit_movement"]),
    )

with tab_scenario:
    apply_pending_signals()  # MUST run before any slider with a matching key is created

    st.subheader("What-If Engine")
    st.caption(
        "Illustrative balance-sheet stress simulation. "
        "The shock changes underlying drivers, then recalculates metrics."
    )

    scenario_left, scenario_right = st.columns([1, 2])

    with scenario_left:
        rate_shock_bps = st.slider(
            "ECB rate shock (bps)",
            min_value=-200,
            max_value=200,
            value=-50,
            step=25,
            key="scenario_rate_shock_bps",
        )

        deposit_outflow_pct = st.slider(
            "Deposit outflow (%)",
            min_value=0.0,
            max_value=25.0,
            value=8.0,
            step=0.5,
            key="scenario_deposit_outflow_pct",
        )

        stage_2_increase = st.slider(
            "Stage 2 migration (percentage points)",
            min_value=0.0,
            max_value=10.0,
            value=2.0,
            step=0.5,
            key="scenario_stage_2_increase",
        )

        stage_3_increase = st.slider(
            "Stage 3 migration (percentage points)",
            min_value=0.0,
            max_value=5.0,
            value=0.5,
            step=0.25,
            key="scenario_stage_3_increase",
        )

        st.divider()

        with st.expander("📰 Apply a news-driven scenario", expanded=False):
            actionable_signals = [s for s in extracted_signals if s.get("engine_param")]
            render_signal_apply_panel(actionable_signals)

        if "applied_signal" in st.session_state:
            render_provenance_banner(st.session_state["applied_signal"])

    scenario_df = run_scenario(
        history=df,
        rate_shock_bps=rate_shock_bps,
        deposit_outflow_pct=deposit_outflow_pct,
        stage_2_increase_pct_points=stage_2_increase,
        stage_3_increase_pct_points=stage_3_increase,
    )

    baseline = scenario_df.loc["Baseline"]
    stressed = scenario_df.loc["Scenario"]

    with scenario_right:
        scenario_col1, scenario_col2, scenario_col3, scenario_col4 = st.columns(4)

        scenario_col1.metric(
            "CET1 ratio",
            f"{stressed['cet1_ratio_pct']:.2f}%",
            metric_delta(
                stressed["cet1_ratio_pct"],
                baseline["cet1_ratio_pct"],
                " pp",
            ),
        )

        scenario_col2.metric(
            "LCR",
            f"{stressed['lcr_pct']:.0f}%",
            metric_delta(
                stressed["lcr_pct"],
                baseline["lcr_pct"],
                " pp",
                decimals=0,
            ),
        )

        scenario_col3.metric(
            "NIM",
            f"{stressed['nim_pct']:.2f}%",
            metric_delta(
                stressed["nim_pct"],
                baseline["nim_pct"],
                " pp",
            ),
        )

        scenario_col4.metric(
            "Provisions",
            format_eur_millions(stressed["provisions"]),
            format_eur_millions(
                stressed["provisions"] - baseline["provisions"]
            ),
        )

        scenario_comparison = pd.DataFrame(
            {
                "Metric": [
                    "CET1 ratio (%)",
                    "LCR (%)",
                    "NIM (%)",
                    "Stage 3 ratio (%)",
                    "RWA (EUR m)",
                    "Provisions (EUR m)",
                    "Deposits (EUR m)",
                ],
                "Baseline": [
                    baseline["cet1_ratio_pct"],
                    baseline["lcr_pct"],
                    baseline["nim_pct"],
                    baseline["stage_3_ratio_pct"],
                    baseline["rwa"],
                    baseline["provisions"],
                    baseline["deposits"],
                ],
                "Scenario": [
                    stressed["cet1_ratio_pct"],
                    stressed["lcr_pct"],
                    stressed["nim_pct"],
                    stressed["stage_3_ratio_pct"],
                    stressed["rwa"],
                    stressed["provisions"],
                    stressed["deposits"],
                ],
            }
        )

        scenario_comparison["Change"] = (
            scenario_comparison["Scenario"]
            - scenario_comparison["Baseline"]
        )

        st.dataframe(
            scenario_comparison.style.format(
                {
                    "Baseline": "{:,.2f}",
                    "Scenario": "{:,.2f}",
                    "Change": "{:+,.2f}",
                }
            ),
            hide_index=True,
            use_container_width=True,
        )

        impact_chart = scenario_comparison[
            scenario_comparison["Metric"].isin(
                ["CET1 ratio (%)", "LCR (%)", "NIM (%)", "Stage 3 ratio (%)"]
            )
        ]

        fig_impact = go.Figure()

        fig_impact.add_trace(
            go.Bar(
                name="Baseline",
                x=impact_chart["Metric"],
                y=impact_chart["Baseline"],
            )
        )

        fig_impact.add_trace(
            go.Bar(
                name="Scenario",
                x=impact_chart["Metric"],
                y=impact_chart["Scenario"],
            )
        )

        fig_impact.update_layout(
            barmode="group",
            title="Baseline vs Scenario",
            yaxis_title="Percent",
            height=360,
            margin=dict(l=10, r=10, t=50, b=10),
        )

        st.plotly_chart(fig_impact, use_container_width=True)

with tab_horizon:
    st.subheader("Horizon View")
    st.caption(
        "12-month trend-based forecast versus management targets. "
        "Forecasts are illustrative and trained on the selected historical window."
    )

    horizon_left, horizon_right, horizon_settings, horizon_confidence = st.columns([1, 1, 1, 1])

    with horizon_left:
        forecast_horizon = st.selectbox(
            "Forecast horizon",
            options=[6, 12, 18],
            index=1,
            format_func=lambda value: f"{value} months",
            key="forecast_horizon",
        )

    with horizon_right:
        forecast_lookback = st.selectbox(
            "Historical training window",
            options=[12, 24, 36],
            index=1,
            format_func=lambda value: f"Last {value} months",
            key="forecast_lookback",
        )

    with horizon_settings:
        st.caption("Forecast method")
        st.info("Linear trend model")

    with horizon_confidence:
        confidence_level = st.selectbox(
            "Confidence level",
            options=[0.80, 0.90, 0.95],
            index=2,
            format_func=lambda value: f"{value:.0%}",
            key="forecast_confidence",
        )

    st.divider()

    st.subheader("Management budget / target assumptions")

    budget_col1, budget_col2, budget_col3, budget_col4, budget_col5 = st.columns(5)

    with budget_col1:
        cet1_target = st.number_input(
            "CET1 target (%)",
            min_value=10.0,
            max_value=25.0,
            value=15.0,
            step=0.1,
        )

    with budget_col2:
        lcr_target = st.number_input(
            "LCR target (%)",
            min_value=100.0,
            max_value=300.0,
            value=150.0,
            step=5.0,
        )

    with budget_col3:
        nim_target = st.number_input(
            "NIM target (%)",
            min_value=0.5,
            max_value=5.0,
            value=2.0,
            step=0.05,
        )

    with budget_col4:
        cost_income_target = st.number_input(
            "Maximum cost-to-income (%)",
            min_value=30.0,
            max_value=100.0,
            value=60.0,
            step=1.0,
        )

    with budget_col5:
        stage_3_target = st.number_input(
            "Maximum Stage 3 ratio (%)",
            min_value=0.5,
            max_value=10.0,
            value=2.5,
            step=0.1,
        )

    metrics_to_forecast = [
        "cet1_ratio_pct",
        "lcr_pct",
        "nim_pct",
        "cost_to_income_pct",
        "stage_3_ratio_pct",
    ]

    forecasts = forecast_metrics(
        history=df,
        metrics=metrics_to_forecast,
        horizon_months=forecast_horizon,
        lookback_months=forecast_lookback,
        confidence_level=confidence_level,
    )

    target_map = {
        "cet1_ratio_pct": {
            "name": "CET1 ratio",
            "target": cet1_target,
            "direction": "minimum",
            "unit": "%",
        },
        "lcr_pct": {
            "name": "Liquidity Coverage Ratio",
            "target": lcr_target,
            "direction": "minimum",
            "unit": "%",
        },
        "nim_pct": {
            "name": "Net Interest Margin",
            "target": nim_target,
            "direction": "minimum",
            "unit": "%",
        },
        "cost_to_income_pct": {
            "name": "Cost-to-Income Ratio",
            "target": cost_income_target,
            "direction": "maximum",
            "unit": "%",
        },
        "stage_3_ratio_pct": {
            "name": "Stage 3 ratio",
            "target": stage_3_target,
            "direction": "maximum",
            "unit": "%",
        },
    }

    st.subheader("Forecast versus target")

    summary_rows = []

    for metric, settings in target_map.items():
        forecast_df = forecasts[metric]
        latest_actual = forecast_df.loc[
            forecast_df["series_type"] == "Historical",
            "value",
        ].iloc[-1]

        final_forecast = forecast_df.loc[
            forecast_df["series_type"] == "Forecast",
            "value",
        ].iloc[-1]

        target = settings["target"]

        if settings["direction"] == "minimum":
            gap_to_target = final_forecast - target
            status = "🟢 On track" if final_forecast >= target else "🔴 Below target"
        else:
            gap_to_target = target - final_forecast
            status = "🟢 On track" if final_forecast <= target else "🔴 Above limit"

        summary_rows.append(
            {
                "Metric": settings["name"],
                "Latest actual": latest_actual,
                f"Forecast ({forecast_horizon}m)": final_forecast,
                "Target": target,
                "Headroom / shortfall": gap_to_target,
                "Status": status,
            }
        )

    forecast_summary = pd.DataFrame(summary_rows)

    st.dataframe(
        forecast_summary.style.format(
            {
                "Latest actual": "{:.2f}%",
                f"Forecast ({forecast_horizon}m)": "{:.2f}%",
                "Target": "{:.2f}%",
                "Headroom / shortfall": "{:+.2f} pp",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )

    st.divider()

    chart_col1, chart_col2 = st.columns(2)

    displayed_metrics = [
        "cet1_ratio_pct",
        "lcr_pct",
        "nim_pct",
        "cost_to_income_pct",
    ]

    for chart_position, metric in zip(
        [chart_col1, chart_col2, chart_col1, chart_col2],
        displayed_metrics,
    ):
        settings = target_map[metric]
        chart_data = forecasts[metric]

        with chart_position:
            st.subheader(settings["name"])

            historical_data = chart_data[
                chart_data["series_type"] == "Historical"
                ]

            forecast_data = chart_data[
                chart_data["series_type"] == "Forecast"
                ]

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=historical_data["date"],
                    y=historical_data["value"],
                    mode="lines",
                    name="Historical",
                    line=dict(color="#1f77b4", width=2),
                )
            )

            # Upper bound first; it becomes the invisible boundary of the shaded band.
            fig.add_trace(
                go.Scatter(
                    x=forecast_data["date"],
                    y=forecast_data["upper_bound"],
                    mode="lines",
                    name=f"{confidence_level:.0%} confidence interval",
                    line=dict(width=0),
                    showlegend=True,
                )
            )

            # Lower bound fills the area back to the upper bound.
            fig.add_trace(
                go.Scatter(
                    x=forecast_data["date"],
                    y=forecast_data["lower_bound"],
                    mode="lines",
                    line=dict(width=0),
                    fill="tonexty",
                    fillcolor="rgba(255, 127, 14, 0.20)",
                    name="",
                    showlegend=False,
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=forecast_data["date"],
                    y=forecast_data["value"],
                    mode="lines",
                    name="Forecast",
                    line=dict(color="#ff7f0e", width=2, dash="dash"),
                )
            )

            fig.add_hline(
                y=settings["target"],
                line_dash="dash",
                line_color="#d62728",
                annotation_text=f"Target: {settings['target']:.2f}%",
                annotation_position="bottom right",
            )

            add_horizon_signal_annotation(fig, metric)

            fig.update_layout(
                height=340,
                margin=dict(l=10, r=10, t=20, b=10),
                xaxis_title="Month-end",
                yaxis_title="Percent",
                legend_title_text="",
            )

            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Forward-looking management message")

    breaches = forecast_summary[
        forecast_summary["Status"] != "🟢 On track"
    ]["Metric"].tolist()

    if breaches:
        st.warning(
            "The current trend forecast indicates that the following target(s) "
            f"may be missed within {forecast_horizon} months: "
            + ", ".join(breaches)
            + "."
        )
    else:
        st.success(
            f"All selected metrics are forecast to remain within their "
            f"management targets over the next {forecast_horizon} months."
        )

with tab_ai:
    st.subheader("AI Financial Partner")
    st.caption(
        "Conversational decision support grounded in the synthetic cockpit "
        "data and scenario engine. No banking action is executed."
    )

    use_gemini = st.toggle(
        "Use Gemini executive narrative",
        value=False,
        help=(
            "Gemini receives only a compact, verified synthetic-metrics payload. "
            "It cannot access bank systems, execute actions, or use live news."
        ),
    )

    ai_left, ai_right = st.columns([2, 1])

    with ai_right:
        st.subheader("30-second briefing")

        if st.button("Generate morning briefing", use_container_width=True):
            st.session_state["ai_briefing"] = build_morning_briefing(df)

        if "ai_briefing" in st.session_state:
            st.info(st.session_state["ai_briefing"])

        st.subheader("Suggested questions")

        st.code("Why did NIM change?", language=None)
        st.code("Explain the CET1 ratio and RWA movement", language=None)
        st.code("Assess liquidity and deposit movements", language=None)
        st.code("Simulate a further 50 bps rate cut", language=None)
        st.code("What actions do you recommend?", language=None)

        if st.button("Clear conversation", use_container_width=True):
            st.session_state["ai_messages"] = []
            st.rerun()

    with ai_left:
        if "ai_messages" not in st.session_state:
            st.session_state["ai_messages"] = [
                {
                    "role": "assistant",
                    "content": (
                        "I am your AI Financial Partner. I can explain current "
                        "metrics, run rate-shock simulations, and propose "
                        "decision-support actions based on the cockpit data."
                    ),
                }
            ]

        for message in st.session_state["ai_messages"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        question = st.chat_input(
            "Ask about capital, liquidity, NIM, RWA, or a rate scenario...",
            key="ai_partner_input",
        )

        if question:
            st.session_state["ai_messages"].append(
                {"role": "user", "content": question}
            )

            with st.chat_message("user"):
                st.markdown(question)

            if use_gemini:
                try:
                    facts = build_cockpit_facts(df)

                    response = generate_gemini_response(
                        user_question=question,
                        facts=facts,
                    )
                except Exception as error:
                    response = (
                            f"⚠️ Gemini is unavailable: `{error}`\n\n"
                            "Showing the controlled analytics response instead.\n\n"
                            + answer_question(question, df)
                    )
            else:
                response = answer_question(question, df)

            st.session_state["ai_messages"].append(
                {"role": "assistant", "content": response}
            )

            with st.chat_message("assistant"):
                st.markdown(response)

with tab_news:
    render_news_intelligence_tab()

with tab_treasury:
    render_treasury_tab()

with tab_peers:
    render_peer_benchmarking_tab({
        "cet1_ratio_pct": float(latest["cet1_ratio_pct"]),
        "cost_to_income_pct": float(latest["cost_to_income_pct"]),
    })

with tab_strategy:
    render_strategic_radar_tab()
