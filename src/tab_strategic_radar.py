import plotly.express as px
import streamlit as st

from src.extended_data_loader import load_strategic_capability_map, load_strategic_radar


def render_strategic_radar_tab():
    st.subheader("Strategic & M&A Radar")
    st.caption(
        "Illustrative strategic-partnership and acquisition radar. Company facts are drawn "
        "from public disclosures. All scores are synthetic management-assessment inputs, "
        "not recommendations or valuations from the cited companies."
    )

    radar = load_strategic_radar()
    capability_map = load_strategic_capability_map()

    if radar.empty:
        st.info("No strategic_radar.csv found. Run `python -m src.generators.generate_all_data`.")
        return

    status_filter = st.multiselect("Radar status", options=["PRIORITY", "WATCH", "SELECTIVE"],
                                     default=["PRIORITY", "WATCH", "SELECTIVE"], key="radar_status_filter")
    filtered_radar = radar[radar["radar_status"].isin(status_filter)]

    k1, k2, k3 = st.columns(3)
    k1.metric("Priority opportunities", int((radar["radar_status"] == "PRIORITY").sum()))
    k2.metric("Watch list", int((radar["radar_status"] == "WATCH").sum()))
    k3.metric("Selective", int((radar["radar_status"] == "SELECTIVE").sum()))

    st.markdown("**Opportunity scoring: fit vs. affordability**")
    fig = px.scatter(filtered_radar, x="affordability_score", y="strategic_fit_score",
                      size="overall_opportunity_score", color="radar_status", text="company_name",
                      hover_data=["capability_domain", "preferred_route"],
                      color_discrete_map={"PRIORITY": "#2ca02c", "WATCH": "#ff7f0e", "SELECTIVE": "#7f7f7f"},
                      labels={"affordability_score": "Affordability score", "strategic_fit_score": "Strategic fit score"})
    fig.update_traces(textposition="top center")
    fig.update_layout(height=460, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Opportunities")
    for row in filtered_radar.sort_values("opportunity_rank").itertuples():
        badge = {"PRIORITY": "\U0001F7E2", "WATCH": "\U0001F7E0", "SELECTIVE": "\u26aa"}.get(row.radar_status, "")
        with st.expander(f"{badge} #{row.opportunity_rank} {row.company_name} - {row.capability_domain} "
                          f"(score: {row.overall_opportunity_score:.1f})"):
            st.markdown(f"**HQ:** {row.headquarters_country} | **Ownership:** {row.ownership_status} | "
                        f"**Route:** {row.preferred_route}")
            st.write(row.business_model_summary)
            st.markdown(f"**Public scale:** {row.public_scale_metric} ([source]({row.public_source_url}))")
            st.markdown(f"**Strategic gap addressed:** {row.strategic_gap_addressed}")
            st.markdown(f"**Rationale:** {row.strategic_rationale}")
            st.markdown(f"**Key risk:** {row.key_risk}")
            s = st.columns(4)
            s[0].metric("Strategic fit", row.strategic_fit_score)
            s[1].metric("Financial attractiveness", row.financial_attractiveness_score)
            s[2].metric("Integration feasibility", row.integration_feasibility_score)
            s[3].metric("Affordability", row.affordability_score)

    st.divider()
    st.subheader("Capability gap map")
    if not capability_map.empty:
        fig_gap = px.bar(capability_map.sort_values("capability_gap", ascending=True),
                          x="capability_gap", y="capability", orientation="h", color="priority",
                          color_discrete_map={"HIGH": "#d62728", "MEDIUM": "#ff7f0e"},
                          labels={"capability_gap": "Gap (target - current)", "capability": ""})
        fig_gap.update_layout(height=380, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_gap, use_container_width=True)

        st.dataframe(
            capability_map[["capability", "current_score", "target_score", "capability_gap",
                             "priority", "linked_companies", "strategic_objective"]].rename(columns={
                "capability": "Capability", "current_score": "Current", "target_score": "Target",
                "capability_gap": "Gap", "priority": "Priority",
                "linked_companies": "Linked companies", "strategic_objective": "Objective",
            }),
            hide_index=True, use_container_width=True,
        )

    st.caption("All scores are synthetic management-assessment inputs for this hackathon prototype.")
