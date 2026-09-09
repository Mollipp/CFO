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

# Basel III floors the executive KPI cards measure their headroom against.
REGULATORY_CET1_REQUIREMENT_PCT = 10.5
REGULATORY_LCR_REQUIREMENT_PCT = 100.0


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

    # The ratios above are a certified month-end close, but the cockpit also
    # runs on the daily signal table, which carries on past that close into the
    # open month. The header shows both so a reading is never mistaken for the
    # other: the live date is where the deposit, rate and credit signals end.
    daily = views.cfo_daily_bank()
    s.live_date_ts = (
        pd.to_datetime(daily["date"].max())
        if daily is not None and not daily.empty
        else s.reporting_date_ts
    )
    s.live_date = s.live_date_ts.strftime("%d %B %Y")
    s.close_date = s.reporting_date_ts.strftime("%d %b %Y")

    s.cet1_ratio = safe_float(current_position["cet1_ratio_pct"])
    s.total_capital_ratio = safe_float(current_position["total_capital_ratio_pct"])
    s.lcr_ratio = safe_float(current_position["lcr_pct"])
    s.loan_to_deposit_ratio = safe_float(current_position["loan_to_deposit_pct"])
    s.ytd_roe_proxy = safe_float(current_position["annualised_ytd_roe_proxy_pct"])
    s.ytd_cost_income = safe_float(current_position["ytd_cost_income_ratio_pct"])
    s.ytd_nii = safe_float(current_position["ytd_nii_m"])
    s.ytd_operating_income = safe_float(current_position["ytd_operating_income_m"])
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
    s.cert_nim_months = int(monthly_nim["month"].nunique())
    s.nim_mom_bps = (s.cert_current_nim - s.previous_cert_nim) * 100.0

    # The cockpit now reads into the open month, so the newest row can hold a
    # handful of days against a full prior month. NIM already annualises on
    # days observed, but NII is a sum: comparing it raw would read a part-month
    # as a collapse in income. Both sides are lifted to a full-month run rate.
    def _nii_run_rate(row):
        days_observed = safe_float(row["days_observed"])
        if days_observed <= 0:
            return 0.0
        month_start = pd.to_datetime(row["month"])
        days_in_month = month_start.days_in_month
        return safe_float(row["monthly_nii_m"]) * days_in_month / days_observed

    s.cert_current_month_days = int(safe_float(latest_nim_row["days_observed"]))
    s.cert_current_month_is_partial = (
        s.cert_current_month_days
        < pd.to_datetime(latest_nim_row["month"]).days_in_month
    )
    s.cert_current_monthly_nii = _nii_run_rate(latest_nim_row)
    s.monthly_nii_change_m = s.cert_current_monthly_nii - _nii_run_rate(previous_nim_row)
    s.nii_basis_label = (
        f"run rate, {s.cert_current_month_days} days observed"
        if s.cert_current_month_is_partial
        else "full month"
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
    _build_kpi_explainers(s)
    _build_domain_grid(s)

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


def _direction(value, up="rose", down="fell", flat="was unchanged"):
    return up if value > 0 else down if value < 0 else flat


def _build_kpi_explainers(s):
    """
    The why / impact / next reading behind each executive KPI.

    The four headline ratios are the cockpit's entry point, and a ratio on its
    own does not tell a CFO whether to act. Each card carries the same three
    lines the decision lenses use: what moved the number, what it means in
    money or headroom, and the one thing worth doing about it.
    """
    escape = html.escape

    cet1_buffer_pp = s.cet1_ratio - REGULATORY_CET1_REQUIREMENT_PCT
    lcr_buffer_pp = s.lcr_ratio - REGULATORY_LCR_REQUIREMENT_PCT
    annualisation = (
        f"{s.months_observed} month{'s' if s.months_observed != 1 else ''} observed, "
        f"annualised"
    )

    s.kpi_cards = [
        {
            "code": "CAP / 01",
            "label": "CET1 RATIO",
            "value": f"{s.cet1_ratio:.1f}%",
            "delta_pp": s.cet1_mom_pp,
            "context": (
                f"{s.cet1_peer_gap_pp:+.1f}pp vs peer median · "
                f"€{s.cet1_capital / 1000:.1f}bn CET1"
            ),
            "module": "brief",
            "why": (
                f"CET1 capital of €{s.cet1_capital / 1000:.2f}bn {_direction(s.cet1_mom_pp)} "
                f"against €{s.latest_history['rwa_m'] / 1000:.1f}bn of risk-weighted assets, "
                f"moving the ratio {s.cet1_mom_pp:+.2f}pp since {s.previous_month_label}."
            ),
            "impact": (
                f"{cet1_buffer_pp:+.1f}pp of headroom over the "
                f"{REGULATORY_CET1_REQUIREMENT_PCT:.1f}% requirement, worth roughly "
                f"€{abs(cet1_buffer_pp) / 100 * s.latest_history['rwa_m'] / 1000:.1f}bn of "
                f"distributable capital, and {s.cet1_peer_gap_pp:+.1f}pp against the "
                f"{s.peer_count}-bank peer median."
            ),
            "next": (
                "Test the buffer against the stressed capital paths in What-If before "
                "committing to distribution or RWA growth."
            ),
        },
        {
            "code": "LIQ / 02",
            "label": "LIQUIDITY COVERAGE",
            "value": f"{s.lcr_ratio:.1f}%",
            "delta_pp": s.lcr_mom_pp,
            "context": (
                f"HQLA €{s.hqla / 1000:.1f}bn · "
                f"L/D {s.loan_to_deposit_ratio:.1f}%"
            ),
            "module": "treasury",
            "why": (
                f"€{s.hqla / 1000:.1f}bn of high-quality liquid assets against 30-day net "
                f"outflows, while the deposit base moved "
                f"€{s.total_deposit_30d_change_m / 1000:+.2f}bn over the last 30 days."
            ),
            "impact": (
                f"{lcr_buffer_pp:+.1f}pp over the "
                f"{REGULATORY_LCR_REQUIREMENT_PCT:.0f}% minimum. Loan-to-deposit at "
                f"{s.loan_to_deposit_ratio:.1f}% sets how much further lending the "
                f"current funding base can carry."
            ),
            "next": (
                "Check the funding and hedge position in Treasury, and the slowest "
                "deposit markets in Morning Brief."
            ),
        },
        {
            "code": "RET / 03",
            "label": "ANNUALISED YTD ROE PROXY",
            "value": f"{s.ytd_roe_proxy:.1f}%",
            "delta_pp": s.ytd_roe_delta_pp,
            "context": (
                f"{s.roe_peer_gap_pp:+.1f}pp vs peer median · directional comparison"
            ),
            "module": "peers",
            "why": (
                f"Year-to-date net profit over average CET1 capital "
                f"({annualisation}). Net interest margin is "
                f"{s.cert_current_nim:.2f}% and {s.nim_mom_bps:+.1f} bps month on month, "
                f"which is the largest single driver."
            ),
            "impact": (
                f"{abs(s.roe_peer_gap_pp):.1f}pp "
                f"{'above' if s.roe_peer_gap_pp >= 0 else 'below'} the peer median. "
                f"A proxy on CET1 "
                f"rather than reported equity, so it is directional: use it to rank "
                f"movement, not to state a reported return."
            ),
            "next": (
                "Compare the return and its drivers against the peer set in Peer "
                "Benchmarking before setting a target."
            ),
        },
        {
            "code": "EFF / 04",
            "label": "YTD COST / INCOME",
            "value": f"{s.ytd_cost_income:.1f}%",
            "delta_pp": s.ytd_ci_delta_pp,
            "context": (
                f"{s.efficiency_peer_advantage_pp:+.1f}pp efficiency advantage vs peer median"
            ),
            "module": "peers",
            "lower_is_better": True,
            "why": (
                f"Year-to-date operating costs over operating income across "
                f"{annualisation.split(',')[0]}. The ratio {_direction(s.ytd_ci_delta_pp)} "
                f"{abs(s.ytd_ci_delta_pp):.1f}pp since {s.previous_month_label}; a rising "
                f"ratio means costs are outpacing income."
            ),
            "impact": (
                f"{abs(s.efficiency_peer_advantage_pp):.1f}pp "
                f"{'better' if s.efficiency_peer_advantage_pp >= 0 else 'worse'} than the "
                f"peer median. One point of cost/income is roughly "
                f"€{s.ytd_operating_income / max(s.months_observed, 1) * 12 / 100:,.0f}m of "
                f"annualised operating income at the current run rate."
            ),
            "next": (
                "Hold the efficiency gap against the peer quadrant before approving "
                "new cost commitments."
            ),
        },
    ]

    for card in s.kpi_cards:
        for field in ("why", "impact", "next"):
            card[field] = escape(card[field])


def _build_narrative(s):
    """Attach the change / why / impact / next copy the HUD panels render."""
    escape = html.escape

    # --- Margin -------------------------------------------------
    s.nim_signal_primary = f"NIM {s.cert_current_nim:.2f}% / {s.nim_mom_bps:+.1f} bps MoM"
    s.nim_signal_secondary = (
        f"Monthly NII €{s.cert_current_monthly_nii:,.0f}m ({s.nii_basis_label}) · "
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
        f"Monthly NII run rate is €{s.cert_current_monthly_nii:,.0f}m "
        f"({s.monthly_nii_change_m:+,.0f}m vs prior month, {s.nii_basis_label})."
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


# ------------------------------------------------------------------
# Domain grid — the executive readout behind Morning Brief
# ------------------------------------------------------------------

def _pct_change(now, before):
    """Percentage movement, or None when there is no comparable base."""
    now = safe_float(now)
    before = safe_float(before)
    if not before:
        return None
    return (now - before) / abs(before) * 100.0


def _movement(value, unit="pp", lower_is_better=False):
    """Arrow, magnitude and the tone class a KPI tile renders."""
    arrow = "↑" if value > 0 else "↓" if value < 0 else "→"
    magnitude = abs(value)
    precision = 2 if 0 < magnitude < 0.1 else 1
    improving = (value < 0) if lower_is_better else (value > 0)
    tone = "is-flat" if value == 0 else "is-up" if improving else "is-down"
    return f"{arrow} {magnitude:,.{precision}f}{unit}", tone


def _tile(code, label, value, delta_text, tone, why, impact, next_copy, topic):
    return {
        "code": code,
        "label": label,
        "value": value,
        "delta": delta_text,
        "tone": tone,
        "why": why,
        "impact": impact,
        "next": next_copy,
        "topic": topic,
    }


def _loan_book_30d():
    """
    Loan book now and 30 days ago, bank-wide and by business line.

    The daily signal table is the only source that carries the loan book past
    the certified month-end close, so the 30-day comparison is taken there and
    on the same basis on both sides of the window.
    """
    detail = views.cfo_daily_business_country()
    if detail is None or detail.empty:
        return None

    latest_date = detail["date"].max()
    prior_date = latest_date - pd.Timedelta(days=CREDIT_LOOKBACK_DAYS)
    if prior_date not in set(detail["date"]):
        return None

    def _by_line(on_date):
        return detail[detail["date"] == on_date].groupby(
            "business_line", as_index=False
        )["interest_earning_assets_m"].sum()

    now, before = _by_line(latest_date), _by_line(prior_date)
    merged = now.merge(before, on="business_line", suffixes=("_now", "_before"))
    if merged.empty:
        return None

    merged["change_m"] = (
        merged["interest_earning_assets_m_now"]
        - merged["interest_earning_assets_m_before"]
    )
    merged["change_pct"] = (
        100.0
        * merged["change_m"]
        / merged["interest_earning_assets_m_before"].replace(0, pd.NA)
    ).astype(float)
    merged = merged.sort_values("change_pct", ascending=False)

    total_now = float(merged["interest_earning_assets_m_now"].sum())
    total_before = float(merged["interest_earning_assets_m_before"].sum())

    return {
        "total_now_m": total_now,
        "total_before_m": total_before,
        "change_m": total_now - total_before,
        "change_pct": _pct_change(total_now, total_before) or 0.0,
        "leader": merged.iloc[0],
        "laggard": merged.iloc[-1],
    }


def _earnings_tiles(s):
    """Domain 01 — what the bank earned and what it cost to earn it."""
    annual_nii_m = s.cert_current_monthly_nii * 12.0
    annual_nii_change_m = s.monthly_nii_change_m * 12.0
    nii_delta, nii_tone = _movement(s.monthly_nii_change_m, "m")
    ci_delta, ci_tone = _movement(s.ytd_ci_delta_pp, "pp", lower_is_better=True)
    nim_delta, nim_tone = _movement(s.nim_mom_bps, "bps")

    monthly_income = s.ytd_operating_income / max(s.months_observed, 1)
    one_point_of_ci_m = monthly_income * 12.0 / 100.0
    ytd_costs_m = s.ytd_operating_income * s.ytd_cost_income / 100.0

    return [
        _tile(
            "ERN / 01",
            "Net interest margin",
            f"{s.cert_current_nim:.2f}%",
            f"{nim_delta} vs {s.previous_month_label}",
            nim_tone,
            s.nim_why,
            s.nim_impact,
            s.nim_next,
            "nim",
        ),
        _tile(
            "ERN / 02",
            "Net interest income",
            f"€{s.cert_current_monthly_nii:,.0f}m",
            f"{nii_delta} vs {s.previous_month_label}",
            nii_tone,
            (
                f"Monthly net interest income on a {s.nii_basis_label} basis: "
                f"average earning assets of "
                f"€{s.cert_current_monthly_nii * 1200.0 / max(s.cert_current_nim, 0.01) / 1000:,.1f}bn "
                f"carried at a {s.cert_current_nim:.2f}% margin. The observed "
                f"loan-versus-deposit pricing spread moved "
                f"{s.spread_30d_bps:+.1f} bps over 30 days."
            ),
            (
                f"€{annual_nii_m / 1000:,.2f}bn of annualised net interest income at "
                f"the current run rate. The month-on-month move is worth "
                f"€{annual_nii_change_m:+,.0f}m a year if it holds."
            ),
            (
                "Trace the margin into country and business-line pricing before "
                "reading the run rate as a forecast."
            ),
            "nim",
        ),
        _tile(
            "ERN / 03",
            "Cost / income ratio",
            f"{s.ytd_cost_income:.1f}%",
            f"{ci_delta} vs prior YTD",
            ci_tone,
            (
                f"Year-to-date operating costs of €{ytd_costs_m:,.0f}m "
                f"against €{s.ytd_operating_income:,.0f}m of operating income over "
                f"{s.months_observed} month{'s' if s.months_observed != 1 else ''}. "
                f"The ratio {_direction(s.ytd_ci_delta_pp)} "
                f"{abs(s.ytd_ci_delta_pp):.2f}pp since {s.previous_month_label}."
            ),
            (
                f"One point of cost/income is roughly €{one_point_of_ci_m:,.0f}m of "
                f"annualised operating income at the current run rate, and the ratio "
                f"sits {abs(s.efficiency_peer_advantage_pp):.1f}pp "
                f"{'better' if s.efficiency_peer_advantage_pp >= 0 else 'worse'} than the "
                f"{s.peer_count}-bank peer median."
            ),
            (
                "Hold the efficiency gap against the peer quadrant before approving "
                "new cost commitments."
            ),
            "efficiency",
        ),
    ]


def _balance_sheet_tiles(s):
    """Domain 02 — the funding base, the loan book and the gap between them."""
    deposit_total_m = (
        float(s.deposit_country["deposit_balance_m"].sum())
        if s.deposit_country is not None and not s.deposit_country.empty
        else s.current_deposits_m
    )
    deposit_delta, deposit_tone = _movement(s.total_deposit_30d_change_pct, "%")

    ltd_prior = safe_float(
        s.previous_history["loan_to_deposit_pct"], s.loan_to_deposit_ratio
    )
    ltd_delta_pp = s.loan_to_deposit_ratio - ltd_prior
    ltd_delta, ltd_tone = _movement(ltd_delta_pp, "pp", lower_is_better=True)
    funding_headroom_m = deposit_total_m - s.current_loans_m

    loans = _loan_book_30d()

    if loans is None:
        loan_tile = _tile(
            "BAL / 02",
            "Loan book",
            f"€{s.current_loans_m / 1000:,.1f}bn",
            f"{_movement(safe_float(s.latest_history['loan_growth_mom_pct']), '%')[0]} MoM",
            _movement(safe_float(s.latest_history["loan_growth_mom_pct"]), "%")[1],
            (
                "The daily signal table does not reach 30 days back, so the loan "
                "book is read at the certified month-end close."
            ),
            (
                f"€{s.current_loans_m / 1000:,.1f}bn of loans against "
                f"€{s.current_deposits_m / 1000:,.1f}bn of deposits at the close."
            ),
            "Open the funding view once the daily window is long enough to compare.",
            "balance_sheet",
        )
    else:
        loan_delta, loan_tone = _movement(loans["change_pct"], "%")
        leader, laggard = loans["leader"], loans["laggard"]
        loan_tile = _tile(
            "BAL / 02",
            "Loan book",
            f"€{loans['total_now_m'] / 1000:,.1f}bn",
            f"{loan_delta} over 30D",
            loan_tone,
            (
                f"Growth is uneven across the book: {leader['business_line']} leads at "
                f"{leader['change_pct']:+.2f}% while {laggard['business_line']} is "
                f"slowest at {laggard['change_pct']:+.2f}% over 30 days."
            ),
            (
                f"The loan book moved €{loans['change_m'] / 1000:+,.2f}bn over 30 days. "
                f"At the current {safe_float(s.latest_history['rwa_m']) / max(safe_float(s.latest_history['total_assets_m']), 1) * 100:.1f}% "
                f"RWA density that lending consumes roughly "
                f"€{abs(loans['change_m']) * safe_float(s.latest_history['rwa_m']) / max(safe_float(s.latest_history['total_assets_m']), 1) / 1000:,.2f}bn "
                f"of risk-weighted assets."
            ),
            (
                "Check whether the fastest-growing segment is priced for the capital "
                "it consumes before extending the book further."
            ),
            "balance_sheet",
        )

    return [
        _tile(
            "BAL / 01",
            "Deposit base",
            f"€{deposit_total_m / 1000:,.1f}bn",
            f"{deposit_delta} over 30D",
            deposit_tone,
            s.deposit_why,
            s.deposit_impact,
            s.deposit_next,
            "deposits",
        ),
        loan_tile,
        _tile(
            "BAL / 03",
            "Loan-to-deposit ratio",
            f"{s.loan_to_deposit_ratio:.1f}%",
            f"{ltd_delta} vs {s.previous_month_label}",
            ltd_tone,
            (
                f"€{s.current_loans_m / 1000:,.1f}bn of loans against "
                f"€{deposit_total_m / 1000:,.1f}bn of deposits. The ratio "
                f"{_direction(ltd_delta_pp)} {abs(ltd_delta_pp):.2f}pp since "
                f"{s.previous_month_label}."
            ),
            (
                f"€{funding_headroom_m / 1000:,.1f}bn of deposits sit above the loan "
                f"book, which is what the current funding base can carry before "
                f"lending has to be funded in the market."
                if funding_headroom_m >= 0
                else f"The loan book runs €{abs(funding_headroom_m) / 1000:,.1f}bn ahead "
                f"of deposits, so that share of lending is funded in the market."
            ),
            (
                "Review the funding and hedge position in Treasury before committing "
                "the remaining deposit headroom to new lending."
            ),
            "balance_sheet",
        ),
    ]


def _capital_tiles(s):
    """Domain 03 — capital and liquidity, read against their requirements."""
    cet1_card, lcr_card = s.kpi_cards[0], s.kpi_cards[1]

    cet1_delta, cet1_tone = _movement(s.cet1_mom_pp, "pp")
    lcr_delta, lcr_tone = _movement(s.lcr_mom_pp, "pp")

    total_capital_prior = safe_float(
        s.previous_history["total_capital_ratio_pct"], s.total_capital_ratio
    )
    tc_delta_pp = s.total_capital_ratio - total_capital_prior
    tc_delta, tc_tone = _movement(tc_delta_pp, "pp")

    own_funds_m = (
        safe_float(s.latest_history["cet1_capital_m"])
        + safe_float(s.latest_history["at1_capital_m"])
        + safe_float(s.latest_history["tier2_capital_m"])
    )
    rwa_m = safe_float(s.latest_history["rwa_m"])

    return [
        _tile(
            "CAP / 01",
            "CET1 ratio",
            f"{s.cet1_ratio:.2f}%",
            f"{cet1_delta} vs {s.previous_month_label}",
            cet1_tone,
            cet1_card["why"],
            cet1_card["impact"],
            cet1_card["next"],
            "capital",
        ),
        _tile(
            "LIQ / 02",
            "Liquidity coverage ratio",
            f"{s.lcr_ratio:.1f}%",
            f"{lcr_delta} vs {s.previous_month_label}",
            lcr_tone,
            lcr_card["why"],
            lcr_card["impact"],
            lcr_card["next"],
            "liquidity",
        ),
        _tile(
            "CAP / 03",
            "Total capital ratio",
            f"{s.total_capital_ratio:.2f}%",
            f"{tc_delta} vs {s.previous_month_label}",
            tc_tone,
            (
                f"€{own_funds_m / 1000:,.2f}bn of total own funds — CET1, AT1 and "
                f"Tier 2 — against €{rwa_m / 1000:,.1f}bn of risk-weighted assets. "
                f"The AT1 and Tier 2 layers add "
                f"{s.total_capital_ratio - s.cet1_ratio:.2f}pp above the CET1 ratio."
            ),
            (
                f"€{(own_funds_m - safe_float(s.latest_history['cet1_capital_m'])) / 1000:,.2f}bn "
                f"of the stack is non-CET1 capital, which absorbs loss after CET1 and "
                f"is the cheaper layer to refill if risk-weighted assets grow."
            ),
            (
                "Test the total-capital path alongside CET1 in What-If before pricing "
                "new issuance."
            ),
            "capital",
        ),
    ]


def _risk_tiles(s):
    """Domain 04 — the exposure the balance sheet carries and what it is covered by."""
    latest, previous = s.latest_history, s.previous_history

    provisions_m = safe_float(latest["provisions_m"])
    provisions_prior_m = safe_float(previous["provisions_m"])
    gca_m = safe_float(latest["gross_carrying_amount_m"])
    gca_prior_m = safe_float(previous["gross_carrying_amount_m"])
    ead_m = safe_float(latest["ead_m"])
    ead_prior_m = safe_float(previous["ead_m"])
    rwa_m = safe_float(latest["rwa_m"])
    rwa_prior_m = safe_float(previous["rwa_m"])
    total_assets_m = safe_float(latest["total_assets_m"])
    cet1_capital_m = safe_float(latest["cet1_capital_m"])

    coverage_pct = provisions_m / gca_m * 100.0 if gca_m else 0.0
    coverage_prior_pct = (
        provisions_prior_m / gca_prior_m * 100.0 if gca_prior_m else coverage_pct
    )
    rwa_density_pct = rwa_m / total_assets_m * 100.0 if total_assets_m else 0.0
    ead_uplift_pct = (ead_m / gca_m - 1.0) * 100.0 if gca_m else 0.0
    stage_2_exposure_m = gca_m * s.stage_2_share_pct / 100.0
    stage_3_exposure_m = gca_m * s.stage_3_share_pct / 100.0

    # A pure RWA move, holding CET1 capital still: this is the capital cost of
    # the quarter's balance-sheet growth, separated from capital generation.
    cet1_from_rwa_pp = (
        (cet1_capital_m / rwa_m - cet1_capital_m / rwa_prior_m) * 100.0
        if rwa_m and rwa_prior_m
        else 0.0
    )

    prov_delta, _ = _movement(_pct_change(provisions_m, provisions_prior_m) or 0.0, "%")
    # The allowance on its own is neither good nor bad; what it is worth is the
    # cover it gives the book, so the tile takes its tone from coverage.
    _, prov_tone = _movement(coverage_pct - coverage_prior_pct, "pp")
    ead_delta, ead_tone = _movement(
        _pct_change(ead_m, ead_prior_m) or 0.0, "%", lower_is_better=True
    )
    gca_delta, gca_tone = _movement(_pct_change(gca_m, gca_prior_m) or 0.0, "%")
    rwa_delta, rwa_tone = _movement(
        _pct_change(rwa_m, rwa_prior_m) or 0.0, "%", lower_is_better=True
    )

    return [
        _tile(
            "RAQ / 01",
            "Provisions",
            f"€{provisions_m / 1000:,.2f}bn",
            f"{prov_delta} vs {s.previous_month_label}",
            prov_tone,
            (
                f"€{provisions_m / 1000:,.2f}bn of loan-loss allowance against "
                f"€{gca_m / 1000:,.1f}bn of gross carrying amount — a coverage ratio "
                f"of {coverage_pct:.2f}%, {coverage_pct - coverage_prior_pct:+.2f}pp "
                f"versus {s.previous_month_label}. The month's provision charge was "
                f"€{safe_float(latest['provision_charge_m']):,.0f}m."
            ),
            (
                f"Stage 3 exposure is €{stage_3_exposure_m / 1000:,.2f}bn at "
                f"{s.stage_3_share_pct:.2f}% of the book, so the allowance stands at "
                f"{provisions_m / stage_3_exposure_m * 100.0:.0f}% of it."
                if stage_3_exposure_m
                else f"Coverage stands at {coverage_pct:.2f}% of gross carrying amount."
            ),
            (
                "Check whether coverage is falling because exposure improved or "
                "because the charge was released, before reading it as good news."
            ),
            "credit",
        ),
        _tile(
            "RAQ / 02",
            "Exposure at default",
            f"€{ead_m / 1000:,.1f}bn",
            f"{ead_delta} vs {s.previous_month_label}",
            ead_tone,
            (
                f"€{ead_m / 1000:,.1f}bn of exposure at default against "
                f"€{gca_m / 1000:,.1f}bn drawn, so undrawn commitments and credit "
                f"conversion add {ead_uplift_pct:+.1f}% on top of the drawn book."
            ),
            (
                f"Risk weights apply to EAD, not to the drawn balance: at the current "
                f"{rwa_m / ead_m * 100.0:.1f}% average weight, "
                f"€{(ead_m - ead_prior_m) / 1000:+,.2f}bn of EAD movement is worth "
                f"€{(ead_m - ead_prior_m) * rwa_m / ead_m / 1000:+,.2f}bn of RWA."
                if ead_m
                else "No comparable exposure base is available."
            ),
            (
                "Review committed-but-undrawn lines alongside the drawn book before "
                "sizing new limits."
            ),
            "credit",
        ),
        _tile(
            "RAQ / 03",
            "Gross carrying amount",
            f"€{gca_m / 1000:,.1f}bn",
            f"{gca_delta} vs {s.previous_month_label}",
            gca_tone,
            (
                f"€{gca_m / 1000:,.1f}bn of gross loans before allowance. "
                f"Stage 1 holds {safe_float(latest['stage_1_share_pct']):.1f}%, "
                f"Stage 2 {s.stage_2_share_pct:.2f}% and Stage 3 "
                f"{s.stage_3_share_pct:.2f}% of the book."
            ),
            (
                f"€{stage_2_exposure_m / 1000:,.1f}bn sits in Stage 2 under heightened "
                f"monitoring — the population that would carry a lifetime expected-loss "
                f"charge if it migrated to Stage 3."
            ),
            (
                "Open the credit lens for the country and business line carrying the "
                "highest Stage 2 concentration."
            ),
            "credit",
        ),
        _tile(
            "RAQ / 04",
            "Risk-weighted assets",
            f"€{rwa_m / 1000:,.1f}bn",
            f"{rwa_delta} vs {s.previous_month_label}",
            rwa_tone,
            (
                f"€{rwa_m / 1000:,.1f}bn of risk-weighted assets on "
                f"€{total_assets_m / 1000:,.1f}bn of total assets — an RWA density of "
                f"{rwa_density_pct:.1f}%. RWA moved "
                f"€{(rwa_m - rwa_prior_m) / 1000:+,.2f}bn since "
                f"{s.previous_month_label}."
            ),
            (
                f"Holding CET1 capital still, that RWA movement alone is worth "
                f"{cet1_from_rwa_pp:+.2f}pp of CET1 ratio; the ratio actually moved "
                f"{s.cet1_mom_pp:+.2f}pp, so capital generation accounts for the "
                f"remaining {s.cet1_mom_pp - cet1_from_rwa_pp:+.2f}pp."
            ),
            (
                "Stress the RWA path in What-If before committing the CET1 buffer to "
                "growth or distribution."
            ),
            "capital",
        ),
    ]


def _build_domain_grid(s):
    """
    The four supervisory domains the executive view opens on.

    Every tile carries the same reading the decision lenses use — the number,
    what moved it, what it is worth, and the one thing to do next — so the grid
    replaces a ratio wall with something a CFO can act on.
    """
    escape = html.escape

    s.domain_grid = [
        {
            "code": "Domain 01 / ERN",
            "name": "Earnings",
            "metrics": "NII · NIM · cost / income",
            "tiles": _earnings_tiles(s),
        },
        {
            "code": "Domain 02 / BAL",
            "name": "Balance sheet",
            "metrics": "Deposits · loans · funding mix",
            "tiles": _balance_sheet_tiles(s),
        },
        {
            "code": "Domain 03 / CAP-LIQ",
            "name": "Capital & Liquidity",
            "metrics": "CET1 · LCR · total capital",
            "tiles": _capital_tiles(s),
        },
        {
            "code": "Domain 04 / RISK",
            "name": "Risk & Asset Quality",
            "metrics": "Provisions · EAD · GCA · RWA",
            "tiles": _risk_tiles(s),
        },
    ]

    # Some copy is reused from the narrative and KPI builders, which escape as
    # they go. Unescaping first makes the pass idempotent, so a reused string is
    # never double-escaped into visible entities.
    for domain in s.domain_grid:
        for field in ("code", "name", "metrics"):
            domain[field] = escape(domain[field])

        for index, tile in enumerate(domain["tiles"], start=1):
            for field in ("code", "label", "value", "delta"):
                tile[field] = escape(tile[field])

            tile["index"] = index
            for field in ("why", "impact", "next"):
                tile[field] = html.unescape(tile[field])
            tile["why_short"] = escape(clip_ui_text(tile["why"], 150))
            for field in ("why", "impact", "next"):
                tile[field] = escape(tile[field])
