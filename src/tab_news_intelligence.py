import pandas as pd
import plotly.express as px
import streamlit as st

from src.extended_data_loader import load_news_geo_impact, load_news_signals


def render_news_intelligence_tab():
    st.subheader("News Intelligence")
    st.caption(
        "Curated public news and releases (ECB, Eurostat, EBA, European "
        "Commission, national statistics offices, and peer-bank press "
        "releases), each linked to a synthetic bank-impact classification."
    )

    news = load_news_signals()
    geo = load_news_geo_impact()

    if news.empty:
        st.info(
            "No news_signals.csv found. Run "
            "`python -m src.generators.generate_all_data` to generate it."
        )
        return

    news = news.sort_values("published_date", ascending=False)

    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        categories = ["All"] + sorted(news["category"].dropna().unique().tolist())
        selected_category = st.selectbox("Category", categories, key="news_category_filter")
    with filter_col2:
        impact_levels = ["All", "HIGH", "MEDIUM", "LOW"]
        selected_impact = st.selectbox("Potential impact level", impact_levels, key="news_impact_filter")
    with filter_col3:
        min_relevance = st.slider("Minimum relevance score", 0, 100, 50, key="news_relevance_filter")

    filtered = news.copy()
    if selected_category != "All":
        filtered = filtered[filtered["category"] == selected_category]
    if selected_impact != "All":
        filtered = filtered[filtered["potential_impact_level"] == selected_impact]
    filtered = filtered[filtered["relevance_score"] >= min_relevance]

    st.caption(f"Showing {len(filtered)} of {len(news)} news items.")

    top_col1, top_col2, top_col3, top_col4 = st.columns(4)
    top_col1.metric("Total items", len(news))
    top_col2.metric("High impact", int((news["potential_impact_level"] == "HIGH").sum()))
    top_col3.metric("Available scenarios", int((news["scenario_status"] == "AVAILABLE").sum()))
    top_col4.metric("Avg. confidence", f"{news['confidence_score'].mean():.0%}")

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.markdown("**Items by category**")
        category_counts = (
            news.groupby("category").size().reset_index(name="count").sort_values("count", ascending=True)
        )
        fig_cat = px.bar(category_counts, x="count", y="category", orientation="h",
                          labels={"count": "Number of items", "category": ""})
        fig_cat.update_layout(height=340, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_cat, use_container_width=True)

    with chart_col2:
        st.markdown("**Relevance vs. confidence**")
        fig_scatter = px.scatter(
            news, x="relevance_score", y="confidence_score", color="potential_impact_level",
            hover_data=["headline", "source"],
            color_discrete_map={"HIGH": "#d62728", "MEDIUM": "#ff7f0e", "LOW": "#2ca02c"},
            labels={"relevance_score": "Relevance score", "confidence_score": "Confidence"},
        )
        fig_scatter.update_layout(height=340, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_scatter, use_container_width=True)

    if not geo.empty:
        st.markdown("**Geographic exposure heat (latest 90 days)**")
        recent_cutoff = news["published_date"].max() - pd.Timedelta(days=90)
        recent_news_ids = news.loc[news["published_date"] >= recent_cutoff, "news_id"]
        geo_recent = geo[geo["news_id"].isin(recent_news_ids)]
        if not geo_recent.empty:
            geo_summary = (
                geo_recent.groupby("country", as_index=False)
                .agg(avg_geo_impact_score=("geo_impact_score", "mean"), items=("news_id", "nunique"))
                .sort_values("avg_geo_impact_score", ascending=False)
            )
            fig_geo = px.bar(geo_summary, x="country", y="avg_geo_impact_score", hover_data=["items"],
                              labels={"avg_geo_impact_score": "Avg. geo impact score", "country": ""})
            fig_geo.update_layout(height=300, margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig_geo, use_container_width=True)

    st.markdown("### Items")
    for row in filtered.itertuples():
        icon = {"HIGH": "\U0001F534", "MEDIUM": "\U0001F7E0", "LOW": "\U0001F7E2"}.get(row.potential_impact_level, "\u26aa")
        with st.expander(f"{icon} {row.published_date.strftime('%d %b %Y')} - {row.headline}"):
            st.markdown(f"**Source:** [{row.source}]({row.source_url}) | **Category:** {row.category} | **Geography:** {row.geographic_scope}")
            st.write(row.summary)
            st.markdown(f"**Bank impact:** {row.bank_impact_summary}")
            st.markdown(f"**Suggested action:** {row.suggested_action}")
            m1, m2, m3 = st.columns(3)
            m1.metric("Relevance", f"{row.relevance_score}/100")
            m2.metric("Confidence", f"{row.confidence_score:.0%}")
            m3.metric("Direction", row.impact_direction)
            if row.linked_scenario:
                st.info(f"Linked scenario: **{row.linked_scenario}** ({row.scenario_status})")

    st.caption(
        "Classifications are synthetic prototype labels layered on real public sources. "
        "They are not statements made by the cited organisations."
    )
