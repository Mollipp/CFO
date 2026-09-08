import pandas as pd
import plotly.express as px
import streamlit as st

from src.extended_data_loader import load_peer_benchmarks, load_peer_financials, load_peer_positioning


def render_peer_benchmarking_tab(latest_bank_metrics):
    st.subheader("Peer Benchmarking")
    st.caption(
        "Our synthetic bank compared against eight real European peer banks using FY2025 "
        "public disclosures. Treat as directional only, not a regulatory-grade comparison."
    )

    peers = load_peer_financials()
    positioning = load_peer_positioning()
    benchmarks = load_peer_benchmarks()

    if peers.empty:
        st.info("No peer_financials.csv found. Run `python -m src.generators.generate_all_data`.")
        return

    our_cet1 = latest_bank_metrics.get("cet1_ratio_pct")
    our_cost_income = latest_bank_metrics.get("cost_to_income_pct")

    if not benchmarks.empty:
        cols = st.columns(4)
        for i, (metric, label) in enumerate([
            ("cet1_ratio_pct", "CET1 ratio"), ("cost_income_ratio_pct", "Cost/income"),
            ("reported_return_pct", "Reported return"), ("lcr_pct", "LCR"),
        ]):
            row = benchmarks[benchmarks["metric"] == metric]
            if not row.empty:
                median_val = row.iloc[0]["peer_median"]
                cols[i].metric(f"Peer median - {label}",
                               f"{median_val:.1f}%" if metric != "lcr_pct" else f"{median_val:.0f}%")

    if our_cet1 is not None or our_cost_income is not None:
        st.markdown("**Our bank vs. peer median**")
        c1, c2 = st.columns(2)
        if our_cet1 is not None:
            row = benchmarks[benchmarks["metric"] == "cet1_ratio_pct"]
            median = float(row.iloc[0]["peer_median"]) if not row.empty else None
            delta = (our_cet1 - median) if median is not None else None
            c1.metric("Our CET1 ratio", f"{our_cet1:.2f}%",
                       f"{delta:+.2f} pp vs. peer median" if delta is not None else None)
        if our_cost_income is not None:
            row = benchmarks[benchmarks["metric"] == "cost_income_ratio_pct"]
            median = float(row.iloc[0]["peer_median"]) if not row.empty else None
            delta = (median - our_cost_income) if median is not None else None
            c2.metric("Our cost-to-income", f"{our_cost_income:.1f}%",
                       f"{delta:+.1f} pp better than peer median" if delta is not None else None)

    st.divider()
    if not positioning.empty:
        st.markdown("**Profitability vs. capital positioning**")
        plot_df = positioning.copy()
        if our_cet1 is not None and our_cost_income is not None:
            our_row = pd.DataFrame([{"bank_name": "Our Bank (synthetic)", "reported_return_pct": None,
                                      "cet1_ratio_pct": our_cet1, "positioning_quadrant": "Our Bank"}])
            plot_df = pd.concat([plot_df, our_row], ignore_index=True)

        fig = px.scatter(plot_df, x="cet1_ratio_pct", y="reported_return_pct", text="bank_name",
                          color="positioning_quadrant",
                          labels={"cet1_ratio_pct": "CET1 ratio (%)", "reported_return_pct": "Reported return (%)"})
        fig.update_traces(textposition="top center", marker=dict(size=12))
        fig.update_layout(height=420, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Peer disclosures")
    display = peers[["bank_name", "home_market", "period", "reported_return_pct", "return_metric_type",
                      "cet1_ratio_pct", "cost_income_ratio_pct", "cost_of_risk_bps", "lcr_pct"]].rename(columns={
        "bank_name": "Bank", "home_market": "Market", "period": "Period",
        "reported_return_pct": "Return (%)", "return_metric_type": "Metric",
        "cet1_ratio_pct": "CET1 (%)", "cost_income_ratio_pct": "Cost/income (%)",
        "cost_of_risk_bps": "Cost of risk (bps)", "lcr_pct": "LCR (%)",
    })
    st.dataframe(display, hide_index=True, use_container_width=True)

    with st.expander("Sources and notes"):
        for row in peers.itertuples():
            st.markdown(f"**{row.bank_name}** - [{row.source_name}]({row.source_url})  \n{row.notes}")

    st.caption("Peer figures are public FY2025 disclosures. Our bank's figures are entirely synthetic.")
