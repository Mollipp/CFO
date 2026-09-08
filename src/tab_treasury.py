import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.extended_data_loader import (
    load_treasury_hedge_options, load_treasury_portfolio, load_treasury_scenario_impacts,
)


def render_treasury_tab():
    st.subheader("Treasury Portfolio & Hedging")
    st.caption(
        "Synthetic EUR banking-book securities portfolio with duration, "
        "convexity and DV01, illustrative market-risk scenarios and "
        "simplified interest-rate swap hedge options."
    )

    portfolio = load_treasury_portfolio()
    scenarios = load_treasury_scenario_impacts()
    hedges = load_treasury_hedge_options()

    if portfolio.empty:
        st.info("No treasury_portfolio.csv found. Run `python -m src.generators.generate_all_data`.")
        return

    total_mv = portfolio["market_value_m"].sum()
    total_dv01 = portfolio["dv01_m_per_bp"].sum()
    total_unrealised = portfolio["unrealized_pnl_m"].sum()
    avg_duration = (portfolio["modified_duration"] * portfolio["market_value_m"]).sum() / total_mv

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Portfolio market value", f"\u20ac{total_mv:,.0f}m")
    k2.metric("Portfolio DV01", f"\u20ac{total_dv01:,.2f}m / bp")
    k3.metric("Weighted avg. duration", f"{avg_duration:.2f} years")
    k4.metric("Unrealised P&L", f"\u20ac{total_unrealised:+,.0f}m")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Market value by asset class**")
        by_class = portfolio.groupby("asset_class", as_index=False)["market_value_m"].sum().sort_values("market_value_m", ascending=False)
        fig_class = px.pie(by_class, names="asset_class", values="market_value_m", hole=0.45)
        fig_class.update_layout(height=320, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_class, use_container_width=True)

    with c2:
        st.markdown("**DV01 by maturity bucket**")
        bucket_order = ["0-2Y", "2-5Y", "5-10Y", "10Y+"]
        by_bucket = portfolio.groupby("maturity_bucket", as_index=False)["dv01_m_per_bp"].sum()
        by_bucket["maturity_bucket"] = pd.Categorical(by_bucket["maturity_bucket"], categories=bucket_order, ordered=True)
        by_bucket = by_bucket.sort_values("maturity_bucket")
        fig_bucket = px.bar(by_bucket, x="maturity_bucket", y="dv01_m_per_bp",
                             labels={"dv01_m_per_bp": "DV01 (\u20acm / bp)", "maturity_bucket": ""})
        fig_bucket.update_layout(height=320, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_bucket, use_container_width=True)

    st.divider()
    st.subheader("Market-risk scenarios")
    if not scenarios.empty:
        scenario_summary = (
            scenarios.groupby("scenario_name", as_index=False)
            .agg(economic_value_impact_m=("economic_value_impact_m", "sum"),
                 estimated_oci_impact_m=("estimated_oci_impact_m", "sum"))
            .sort_values("economic_value_impact_m")
        )
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Economic value impact", x=scenario_summary["scenario_name"],
                              y=scenario_summary["economic_value_impact_m"], marker_color="#1f77b4"))
        fig.add_trace(go.Bar(name="Estimated OCI impact", x=scenario_summary["scenario_name"],
                              y=scenario_summary["estimated_oci_impact_m"], marker_color="#ff7f0e"))
        fig.update_layout(barmode="group", height=380, yaxis_title="EUR millions", margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            scenario_summary.rename(columns={
                "scenario_name": "Scenario",
                "economic_value_impact_m": "Economic value impact (\u20acm)",
                "estimated_oci_impact_m": "Estimated OCI impact (\u20acm)",
            }).style.format({"Economic value impact (\u20acm)": "{:+,.1f}", "Estimated OCI impact (\u20acm)": "{:+,.1f}"}),
            hide_index=True, use_container_width=True,
        )

    st.divider()
    st.subheader("Hedge options")
    if not hedges.empty:
        st.dataframe(
            hedges[["hedge_name", "hedge_notional_m", "dv01_reduction_pct",
                    "rates_plus_50bp_pnl_before_m", "rates_plus_50bp_pnl_after_m",
                    "estimated_annual_carry_m"]].rename(columns={
                "hedge_name": "Hedge", "hedge_notional_m": "Notional (\u20acm)",
                "dv01_reduction_pct": "DV01 reduction (%)",
                "rates_plus_50bp_pnl_before_m": "+50bp before (\u20acm)",
                "rates_plus_50bp_pnl_after_m": "+50bp after (\u20acm)",
                "estimated_annual_carry_m": "Est. annual carry (\u20acm)",
            }),
            hide_index=True, use_container_width=True,
        )

    st.divider()
    st.subheader("Portfolio holdings")
    st.dataframe(
        portfolio[["issuer", "issuer_country", "asset_class", "rating",
                   "accounting_classification", "maturity_bucket",
                   "market_value_m", "yield_pct", "modified_duration", "dv01_m_per_bp"]]
        .rename(columns={
            "issuer": "Issuer", "issuer_country": "Country", "asset_class": "Asset class",
            "rating": "Rating", "accounting_classification": "Accounting",
            "maturity_bucket": "Maturity", "market_value_m": "Market value (\u20acm)",
            "yield_pct": "Yield (%)", "modified_duration": "Mod. duration", "dv01_m_per_bp": "DV01 (\u20acm/bp)",
        }).sort_values("Market value (\u20acm)", ascending=False),
        hide_index=True, use_container_width=True, height=360,
    )
