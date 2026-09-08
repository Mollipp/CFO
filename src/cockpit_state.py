"""
Derived cockpit state.

One pass over the certified views produces every value the HUD renders: the
headline ratios, the month-on-month and 30-day changes, the change/why/impact/
next narrative strings, and the slices each module charts.

Keeping this in one place means the shell and the modules read the same numbers,
and the presentation layer never reaches into a dataframe itself.
"""

import html
from types import SimpleNamespace

import pandas as pd
import streamlit as st

from src import cockpit_views as views
from src.engines import build_horizon_baseline
from src.hud import clip_ui_text, safe_float

# The reference cockpit's lookback windows.
DEPOSIT_LOOKBACK_DAYS = 30
CREDIT_LOOKBACK_DAYS = 30
DAILY_RATE_LOOKBACK_DAYS = 30
NEWS_LOOKBACK_DAYS = 13

# The baseline runs to the end of the reporting year.
HORIZON_MONTHS_AHEAD = 4


def _latest_rows(frame, date_column="date"):
    """Rows on the most recent observed date."""
    if frame is None or frame.empty:
        return frame
    return frame[frame[date_column] == frame[date_column].max()]


def _deposit_by_country():
    """Latest deposit balance and 30-day change, aggregated to country."""
    signals = _latest_rows(views.cfo_deposit_signals())
    if signals is None or signals.empty:
        return pd.DataFrame()

    by_country = signals.groupby("country", as_index=False).agg(
        deposit_balance_m=("deposit_balance_m", "sum"),
        deposit_change_30d_m=("deposit_change_30d_m", "sum"),
    )

    prior = by_country["deposit_balance_m"] - by_country["deposit_change_30d_m"]
    by_country["deposit_change_30d_pct"] = (
        100.0 * by_country["deposit_change_30d_m"] / prior.replace(0, pd.NA)
    ).astype(float)

    return by_country.sort_values("deposit_change_30d_pct", ascending=False)


def _credit_detail():
    """Latest country / business-line credit rows, worst first."""
    detail = _latest_rows(views.cfo_credit_signals())
    if detail is None or detail.empty:
        return pd.DataFrame()

    return detail.sort_values(
        [
            "credit_watch_flag",
            "weighted_stage_2_share_pct",
            "weighted_stage_3_share_pct",
        ],
        ascending=[False, False, False],
    )


def _credit_trend():
    """The latest credit observation and its counterpart 30 days earlier."""
    signals = views.cfo_credit_signals()
    if signals is None or signals.empty:
        return pd.DataFrame()

    latest_date = signals["date"].max()
    prior_date = latest_date - pd.Timedelta(days=CREDIT_LOOKBACK_DAYS)

    return signals[signals["date"].isin([latest_date, prior_date])]


def _recent_news():
    """
    One row per article over the trailing news window.

    A story maps to several countries; the certified feed keeps the highest
    geographic impact row so the same headline is not listed repeatedly.
    """
    intelligence = views.cfo_news_intelligence()
    if intelligence is None or intelligence.empty:
        return pd.DataFrame()

    latest = intelligence["published_date"].max()
    recent = intelligence[
        intelligence["published_date"]
        >= latest - pd.Timedelta(days=NEWS_LOOKBACK_DAYS)
    ]

    ranked = recent.sort_values(
        ["news_id", "geo_impact_score", "country"], ascending=[True, False, True]
    ).drop_duplicates(subset="news_id", keep="first")

    return ranked.sort_values(
        ["relevance_score", "published_date"], ascending=[False, False]
    ).reset_index(drop=True)


@st.cache_data
def build_state():
    """Compute every derived cockpit value. Cached; returns a namespace."""
    s = SimpleNamespace()

    # ----------------------------------------------------------
    # Current position
    # ----------------------------------------------------------
    current_position = views.cfo_current_position().iloc[0]

    s.reporting_date_ts = pd.to_datetime(current_position["as_of_date"])
    s.reporting_date = s.reporting_date_ts.strftime("%d %B %Y")

    s.cet1_ratio = safe_float(current_position["cet1_ratio_pct"])
    s.total_capital_ratio = safe_float(current_position["total_capital_ratio_pct"])
    s.lcr_ratio = safe_float(current_position["lcr_pct"])
    s.loan_to_deposit_ratio = safe_float(current_position["loan_to_deposit_pct"])
    s.ytd_roe_proxy = safe_float(current_position["annualised_ytd_roe_proxy_pct"])
    s.ytd_cost_income = safe_float(current_position["ytd_cost_income_ratio_pct"])
    s.ytd_nii = safe_float(current_position["ytd_nii_m"])
    s.current_loans_m = safe_float(current_position["loans_m"])
    s.current_deposits_m = safe_float(current_position["deposits_m"])
    s.total_assets = safe_float(current_position["total_assets_m"])
    s.cet1_capital = safe_float(current_position["cet1_capital_m"])
    s.hqla = safe_float(current_position["hqla_m"])
    s.months_observed = int(safe_float(current_position["months_observed"], 0))
    s.stage_2_share_pct = safe_float(current_position["stage_2_share_pct"])
    s.stage_3_share_pct = safe_float(current_position["stage_3_share_pct"])
    s.ecb_rate_pct = safe_float(current_position["ecb_rate_pct"])

    # ----------------------------------------------------------
    # Month-on-month change context
    # ----------------------------------------------------------
    history = views.cfo_financial_history().sort_values("date").reset_index(drop=True)
    s.history = history

    latest_history = history.iloc[-1]
    previous_history = history.iloc[-2] if len(history) >= 2 else latest_history

    s.latest_history = latest_history
    s.previous_history = previous_history
    s.previous_month_label = pd.to_datetime(previous_history["date"]).strftime("%b")
    s.cet1_mom_pp = s.cet1_ratio - safe_float(previous_history["cet1_ratio_pct"])
    s.lcr_mom_pp = s.lcr_ratio - safe_float(previous_history["lcr_pct"])

    prev_roe, prev_ci = ytd_metrics_through(history, previous_history["date"])
    s.ytd_roe_delta_pp = s.ytd_roe_proxy - safe_float(prev_roe, s.ytd_roe_proxy)
    s.ytd_ci_delta_pp = s.ytd_cost_income - safe_float(prev_ci, s.ytd_cost_income)

    # ----------------------------------------------------------
    # Certified NIM
    # ----------------------------------------------------------
    monthly_nim = views.cfo_monthly_nim()
    valid_nim = monthly_nim.dropna(subset=["nim_pct"]).sort_values("month")
    s.monthly_nim = monthly_nim

    latest_nim_row = valid_nim.iloc[-1]
    previous_nim_row = valid_nim.iloc[-2] if len(valid_nim) >= 2 else latest_nim_row

    s.previous_cert_nim = safe_float(previous_nim_row["nim_pct"])
    s.cert_current_nim = safe_float(latest_nim_row["nim_pct"])
    s.cert_current_monthly_nii = safe_float(latest_nim_row["monthly_nii_m"])
    s.cert_nim_months = int(monthly_nim["month"].nunique())
    s.nim_mom_bps = (s.cert_current_nim - s.previous_cert_nim) * 100.0
    s.monthly_nii_change_m = s.cert_current_monthly_nii - safe_float(
        previous_nim_row["monthly_nii_m"]
    )

    # ----------------------------------------------------------
    # Daily pricing signals
    # ----------------------------------------------------------
    daily = views.cfo_daily_bank().sort_values("date")
    s.daily = daily

    s.latest_daily_nim = s.cert_current_nim
    s.latest_daily_nii = 0.0
    s.daily_anomaly_flag = 0
    s.loan_rate_30d_bps = 0.0
    s.deposit_rate_30d_bps = 0.0
    s.spread_30d_bps = 0.0

    if not daily.empty:
        latest_daily = daily.iloc[-1]
        s.latest_daily_nim = safe_float(latest_daily["annualised_daily_nim_pct"])
        s.latest_daily_nii = safe_float(latest_daily["daily_nii_m"])
        s.daily_anomaly_flag = int(safe_float(latest_daily["has_anomaly"], 0))

        window_start = daily["date"].max() - pd.Timedelta(
            days=DAILY_RATE_LOOKBACK_DAYS
        )
        recent = daily[daily["date"] >= window_start].dropna(
            subset=["weighted_loan_rate_pct", "weighted_deposit_rate_pct"]
        )

        if not recent.empty:
            first, last = recent.iloc[0], recent.iloc[-1]
            s.loan_rate_30d_bps = (
                safe_float(last["weighted_loan_rate_pct"])
                - safe_float(first["weighted_loan_rate_pct"])
            ) * 100.0
            s.deposit_rate_30d_bps = (
                safe_float(last["weighted_deposit_rate_pct"])
                - safe_float(first["weighted_deposit_rate_pct"])
            ) * 100.0
            s.spread_30d_bps = s.loan_rate_30d_bps - s.deposit_rate_30d_bps

    # ----------------------------------------------------------
    # Deposits by country
    # ----------------------------------------------------------
    deposit_country = _deposit_by_country()
    s.deposit_country = deposit_country

    s.deposit_leader = None
    s.deposit_laggard = None
    s.negative_deposit_countries = 0
    s.total_deposit_30d_change_m = 0.0
    s.total_deposit_30d_change_pct = 0.0

    if not deposit_country.empty:
        s.deposit_leader = deposit_country.iloc[0]
        s.deposit_laggard = deposit_country.iloc[-1]
        s.negative_deposit_countries = int(
            (deposit_country["deposit_change_30d_pct"] < 0).sum()
        )
        current_deposits = deposit_country["deposit_balance_m"].sum()
        s.total_deposit_30d_change_m = deposit_country["deposit_change_30d_m"].sum()
        prior_deposits = current_deposits - s.total_deposit_30d_change_m
        if prior_deposits:
            s.total_deposit_30d_change_pct = (
                s.total_deposit_30d_change_m / prior_deposits * 100.0
            )

    # ----------------------------------------------------------
    # Credit migration
    # ----------------------------------------------------------
    credit_detail = _credit_detail()
    s.credit_detail = credit_detail

    s.current_credit_watch_count = 0
    s.credit_hotspot = None
    s.credit_hotspot_stage2_delta_pp = None

    if not credit_detail.empty:
        s.current_credit_watch_count = int(credit_detail["credit_watch_flag"].sum())
        s.credit_hotspot = credit_detail.iloc[0]

        trend = _credit_trend()
        if not trend.empty:
            match = trend[
                (trend["country"] == s.credit_hotspot["country"])
                & (trend["business_line"] == s.credit_hotspot["business_line"])
            ].sort_values("date")
            if len(match) >= 2:
                s.credit_hotspot_stage2_delta_pp = safe_float(
                    match.iloc[-1]["weighted_stage_2_share_pct"]
                ) - safe_float(match.iloc[0]["weighted_stage_2_share_pct"])

    # ----------------------------------------------------------
    # External intelligence
    # ----------------------------------------------------------
    news_recent = _recent_news()
    geo_news = views.cfo_geo_news_summary()
    if not geo_news.empty:
        geo_news = geo_news.sort_values("geo_attention_score", ascending=False)

    s.news_recent = news_recent
    s.geo_news = geo_news
    s.high_impact_news_count = 0
    s.top_news = None
    s.geo_focus = None

    if not news_recent.empty:
        levels = news_recent["potential_impact_level"].fillna("").astype(str).str.upper()
        s.high_impact_news_count = int((levels == "HIGH").sum())
        s.top_news = news_recent.iloc[0]

    if not geo_news.empty:
        s.geo_focus = geo_news.iloc[0]

    # ----------------------------------------------------------
    # Treasury
    # ----------------------------------------------------------
    treasury_summary_df = views.cfo_treasury_summary()
    s.treasury_summary = (
        treasury_summary_df.iloc[0] if not treasury_summary_df.empty else None
    )
    s.treasury_market_value_m = 0.0
    s.treasury_unrealised_pnl_m = 0.0
    s.treasury_duration = 0.0
    s.treasury_dv01 = 0.0

    if s.treasury_summary is not None:
        s.treasury_market_value_m = safe_float(s.treasury_summary["market_value_m"])
        s.treasury_unrealised_pnl_m = safe_float(
            s.treasury_summary["unrealized_pnl_m"]
        )
        s.treasury_duration = safe_float(
            s.treasury_summary["weighted_modified_duration"]
        )
        s.treasury_dv01 = safe_float(s.treasury_summary["portfolio_dv01_m_per_bp"])

    scenarios = views.cfo_treasury_scenarios()
    s.treasury_scenarios = scenarios

    s.treasury_rate50_impact_m = 0.0
    rate50 = scenarios[scenarios["scenario_name"].str.contains("50bps", na=False)]
    rate50 = rate50[rate50["rate_shock_bps"] == 50]
    rate50 = rate50[rate50["credit_spread_shock_bps"].fillna(0).abs() < 0.001]
    if not rate50.empty:
        s.treasury_rate50_impact_m = safe_float(
            rate50.iloc[0]["economic_value_impact_m"]
        )

    impact = s.treasury_rate50_impact_m
    s.treasury_rate50_text = (
        f"-€{abs(impact) / 1000:.2f}bn"
        if impact < 0
        else f"+€{impact / 1000:.2f}bn"
        if impact > 0
        else "—"
    )

    # The local portfolio carries a single snapshot, so no day-over-day move
    # exists yet. The UI shows the change automatically once one does.
    s.treasury_market_change_m = None
    s.treasury_market_change_pct = None
    s.treasury_market_trend_label = "Prior snapshot"
    s.treasury_market_trend_css = "trend-flat"
    s.treasury_market_trend_text = "— / unavailable"

    s.hedge_options = views.cfo_hedge_options()
    s.strongest_hedge = (
        s.hedge_options.sort_values("dv01_reduction_pct", ascending=False).iloc[0]
        if s.hedge_options is not None and not s.hedge_options.empty
        else None
    )

    # ----------------------------------------------------------
    # Peers
    # ----------------------------------------------------------
    peers = views.cfo_peer_benchmark()
    s.peer_benchmark = peers
    s.peer_count = len(peers) if peers is not None else 0
    s.peer_profitability_median = 0.0
    s.peer_cet1_median = 0.0
    s.peer_cost_income_median = 0.0
    s.peer_plot = pd.DataFrame()

    if peers is not None and not peers.empty:
        for column, attribute in [
            ("profitability_peer_median_pct", "peer_profitability_median"),
            ("cet1_peer_median_pct", "peer_cet1_median"),
            ("cost_income_peer_median_pct", "peer_cost_income_median"),
        ]:
            values = peers[column].dropna()
            if not values.empty:
                setattr(s, attribute, safe_float(values.iloc[0]))

        plot = peers[
            [
                "bank_name",
                "reported_return_pct",
                "cet1_ratio_pct",
                "cost_income_ratio_pct",
                "total_assets_m",
                "return_metric_type",
            ]
        ].copy()
        plot["is_our_bank"] = "Peer"

        our_row = pd.DataFrame(
            [
                {
                    "bank_name": "Our Bank",
                    "reported_return_pct": s.ytd_roe_proxy,
                    "cet1_ratio_pct": s.cet1_ratio,
                    "cost_income_ratio_pct": s.ytd_cost_income,
                    "total_assets_m": s.total_assets,
                    "return_metric_type": "Annualised YTD ROE proxy",
                    "is_our_bank": "Our Bank",
                }
            ]
        )
        s.peer_plot = pd.concat([plot, our_row], ignore_index=True)

    s.roe_peer_gap_pp = s.ytd_roe_proxy - s.peer_profitability_median
    s.cet1_peer_gap_pp = s.cet1_ratio - s.peer_cet1_median
    s.efficiency_peer_advantage_pp = s.peer_cost_income_median - s.ytd_cost_income

    # ----------------------------------------------------------
    # Strategy
    # ----------------------------------------------------------
    radar = views.cfo_strategic_radar()
    gaps = views.cfo_capability_gaps()
    s.strategic_radar = radar
    s.capability_gaps = gaps
    s.top_strategy = radar.iloc[0] if radar is not None and not radar.empty else None
    s.top_capability_gap = (
        gaps.sort_values("capability_gap", ascending=False).iloc[0]
        if gaps is not None and not gaps.empty
        else None
    )

    s.second_strategy = None
    s.strategy_score_gap = 0.0
    s.strategy_delta = pd.DataFrame()
    s.strategy_advantage_pills = []

    if radar is not None and len(radar) >= 2:
        s.second_strategy = radar.iloc[1]
        s.strategy_score_gap = safe_float(
            s.top_strategy["overall_opportunity_score"]
        ) - safe_float(s.second_strategy["overall_opportunity_score"])

        # The opportunity map plots only fit against attractiveness; the rank
        # itself is this seven-factor composite, so the gap is broken out.
        component_spec = [
            ("Strategic fit", "strategic_fit_score", 0.30, False),
            ("Financial attractiveness", "financial_attractiveness_score", 0.15, False),
            ("Integration feasibility", "integration_feasibility_score", 0.15, False),
            ("Affordability", "affordability_score", 0.10, False),
            ("Innovation", "innovation_score", 0.15, False),
            ("Time to value", "time_to_value_score", 0.10, False),
            ("Regulatory simplicity", "regulatory_complexity_score", 0.05, True),
        ]

        rows = []
        for label, column, weight, inverse in component_spec:
            top_value = safe_float(s.top_strategy[column])
            second_value = safe_float(s.second_strategy[column])
            if inverse:
                top_value, second_value = 100.0 - top_value, 100.0 - second_value
            rows.append(
                {"Component": label, "Weighted delta": weight * (top_value - second_value)}
            )

        s.strategy_delta = pd.DataFrame(rows)
        positive = s.strategy_delta[s.strategy_delta["Weighted delta"] > 0]
        for _, row in positive.sort_values(
            "Weighted delta", ascending=False
        ).head(3).iterrows():
            s.strategy_advantage_pills.append(
                f"{row['Component']} +{row['Weighted delta']:.1f} pts"
            )

    # ----------------------------------------------------------
    # Horizon baseline
    # ----------------------------------------------------------
    s.current_loan_rate_pct = 0.0
    s.current_deposit_rate_pct = 0.0
    if not daily.empty:
        latest_rates = daily.iloc[-1]
        s.current_loan_rate_pct = safe_float(latest_rates["weighted_loan_rate_pct"])
        s.current_deposit_rate_pct = safe_float(
            latest_rates["weighted_deposit_rate_pct"]
        )

    s.horizon_baseline, horizon_metrics = build_horizon_baseline(
        s.monthly_nim,
        months_ahead=HORIZON_MONTHS_AHEAD,
        current_loans_m=s.current_loans_m,
        current_deposits_m=s.current_deposits_m,
        current_loan_rate_pct=s.current_loan_rate_pct,
        current_deposit_rate_pct=s.current_deposit_rate_pct,
        loan_rate_30d_bps=s.loan_rate_30d_bps,
        deposit_rate_30d_bps=s.deposit_rate_30d_bps,
        deposit_growth_30d_pct=s.total_deposit_30d_change_pct,
    )

    s.horizon_metrics = horizon_metrics
    s.horizon_year_end_nim = safe_float(
        horizon_metrics.get("year_end_nim_pct"), s.cert_current_nim
    )
    s.horizon_change_bps = safe_float(
        horizon_metrics.get("current_to_year_end_bps"), 0.0
    )
    s.horizon_first_month_bps = safe_float(
        horizon_metrics.get("first_month_nim_change_bps"), 0.0
    )
    s.horizon_full_year_nii_m = safe_float(
        horizon_metrics.get("full_year_nii_m"), s.ytd_nii
    )
    s.horizon_remaining_nii_m = safe_float(
        horizon_metrics.get("forecast_nii_remaining_m"), 0.0
    )
    s.horizon_asset_growth_pct = safe_float(
        horizon_metrics.get("trailing_asset_growth_pct"), 0.0
    )
    s.horizon_deposit_growth_pct = safe_float(
        horizon_metrics.get("deposit_growth_run_rate_pct"), 0.0
    )
    s.horizon_method_text = str(horizon_metrics.get("baseline_method", ""))

    _build_narrative(s)

    return s


def ytd_metrics_through(history, cutoff_date):
    """
    Year-to-date ROE proxy and cost/income as they stood at a past month-end.

    Recomputing the YTD aggregates at the cutoff is what makes the headline
    deltas honest: comparing a YTD figure against a single prior month would
    mix two different bases.
    """
    cutoff_date = pd.to_datetime(cutoff_date)
    local = history[
        (history["date"].dt.year == cutoff_date.year)
        & (history["date"] <= cutoff_date)
    ]

    if local.empty:
        return None, None

    months = int(local["date"].dt.month.nunique())
    avg_cet1 = local["cet1_capital_m"].mean()
    net_profit = local["net_profit_m"].sum()
    operating_income = local["operating_income_m"].sum()
    operating_costs = local["operating_costs_m"].sum()

    roe = (
        None
        if not avg_cet1 or months <= 0
        else net_profit * (12.0 / months) / avg_cet1 * 100.0
    )
    cost_income = (
        None if not operating_income else operating_costs / operating_income * 100.0
    )

    return roe, cost_income


def _build_narrative(s):
    """Attach the change / why / impact / next copy the HUD panels render."""
    escape = html.escape

    # --- Margin -------------------------------------------------
    s.nim_signal_primary = f"NIM {s.cert_current_nim:.2f}% / {s.nim_mom_bps:+.1f} bps MoM"
    s.nim_signal_secondary = (
        f"Monthly NII €{s.cert_current_monthly_nii:,.0f}m · "
        f"pricing spread {s.spread_30d_bps:+.1f} bps over 30D"
    )
    spread_direction = (
        "widened"
        if s.spread_30d_bps > 0
        else "narrowed"
        if s.spread_30d_bps < 0
        else "was unchanged"
    )
    s.nim_why = (
        f"Loan-versus-deposit pricing spread {spread_direction} by "
        f"{abs(s.spread_30d_bps):.1f} bps over 30D."
    )
    s.nim_impact = (
        f"Latest monthly NII is €{s.cert_current_monthly_nii:,.0f}m "
        f"({s.monthly_nii_change_m:+,.0f}m vs prior month)."
    )
    s.nim_next = (
        "Inspect country and business-line pricing/pass-through drivers in "
        "Morning Brief or Copilot."
    )

    # --- Funding ------------------------------------------------
    if s.deposit_leader is not None and s.deposit_laggard is not None:
        s.deposit_signal_primary = (
            f"{s.total_deposit_30d_change_pct:+.2f}% / "
            f"€{s.total_deposit_30d_change_m / 1000:+.2f}bn over 30D"
        )
        s.deposit_signal_secondary = (
            f"{escape(str(s.deposit_leader['country']))} leads "
            f"{safe_float(s.deposit_leader['deposit_change_30d_pct']):+.1f}% · "
            f"{escape(str(s.deposit_laggard['country']))} lowest "
            f"{safe_float(s.deposit_laggard['deposit_change_30d_pct']):+.1f}%"
        )
        s.deposit_why = (
            f"Growth is uneven: {escape(str(s.deposit_leader['country']))} leads "
            f"while {escape(str(s.deposit_laggard['country']))} is slowest."
        )
    else:
        s.deposit_signal_primary = "Deposit movement unavailable"
        s.deposit_signal_secondary = "No latest country deposit observation"
        s.deposit_why = "No country-level deposit observation is available."

    s.deposit_impact = (
        f"Funding base changed by €{s.total_deposit_30d_change_m / 1000:+.2f}bn over 30D."
    )
    s.deposit_next = (
        "Review slower-growth markets and business lines before changing deposit pricing."
    )

    # --- Credit -------------------------------------------------
    if s.credit_hotspot is not None:
        delta_text = (
            "30D comparison unavailable"
            if s.credit_hotspot_stage2_delta_pp is None
            else f"{s.credit_hotspot_stage2_delta_pp:+.2f}pp vs 30D"
        )
        s.credit_signal_primary = (
            f"{escape(str(s.credit_hotspot['country']))} / "
            f"{escape(str(s.credit_hotspot['business_line']))} Stage 2 "
            f"{safe_float(s.credit_hotspot['weighted_stage_2_share_pct']):.1f}%"
        )
        s.credit_signal_secondary = (
            f"{delta_text} · {s.current_credit_watch_count} current watch(es)"
        )
        s.credit_impact = (
            f"Stage 2 is "
            f"{safe_float(s.credit_hotspot['weighted_stage_2_share_pct']):.1f}%"
        )
    else:
        s.credit_signal_primary = "Credit movement unavailable"
        s.credit_signal_secondary = "No latest credit observation"
        s.credit_impact = "Credit impact unavailable"

    s.credit_why = (
        "Stage 2 concentration is highest in the identified country/business line; "
        "the data does not establish the underlying cause."
    )
    s.credit_next = (
        "Investigate migration drivers and provisioning exposure before taking action."
    )

    # --- External news ------------------------------------------
    if s.top_news is not None:
        s.news_signal_primary = escape(clip_ui_text(s.top_news["headline"], 58))
        s.news_signal_secondary = (
            f"{escape(str(s.top_news['source']))} · potential metric: "
            f"{escape(str(s.top_news['primary_affected_metric']))}"
        )
        s.news_why = escape(
            clip_ui_text(s.top_news.get("bank_impact_summary", ""), 120)
        )
        s.news_impact = escape(str(s.top_news["primary_affected_metric"]))
        s.news_next = escape(clip_ui_text(s.top_news.get("suggested_action", ""), 105))
    else:
        s.news_signal_primary = "External intelligence unavailable"
        s.news_signal_secondary = "No recent public-source item in the window"
        s.news_why = "No current external-development context available."
        s.news_impact = "—"
        s.news_next = "Review the external-intelligence feed when new items arrive."

    # Margin, funding and credit: the three movements the brief opens on.
    s.executive_change_count = 3
