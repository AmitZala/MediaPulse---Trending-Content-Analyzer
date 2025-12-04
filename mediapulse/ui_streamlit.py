# mediapulse/ui_streamlit.py (updated)
import streamlit as st
from mediapulse.fetcher import DataFetcher
from mediapulse.processor import DataProcessor
from mediapulse.analytics import AnalyticsSummary
from mediapulse.charts import ChartRenderer
import pandas as pd

st.set_page_config(page_title="MediaPulse", page_icon="🚀", layout="wide")
st.title("MediaPulse — Trending Content Analyzer (Enhanced)")

fetcher = DataFetcher()
processor = DataProcessor()
analytics = AnalyticsSummary()
charts = ChartRenderer()

raw = fetcher.fetch()
cleaned = processor.clean(raw)

# Sidebar selectors
st.sidebar.header("Filters")
keywords = sorted(cleaned['keyword'].str.lower().unique().tolist())
selected_keywords = st.sidebar.multiselect("Keywords (empty = all)", options=keywords, default=keywords[:3])
platforms = sorted(cleaned['platform'].str.lower().unique().tolist())
selected_platforms = st.sidebar.multiselect("Platforms", options=platforms, default=platforms)
content_types = sorted(cleaned['content_type'].str.lower().unique().tolist())
selected_content_types = st.sidebar.multiselect("Content types", options=content_types, default=content_types)
regions = sorted(cleaned['region'].str.lower().unique().tolist())
selected_regions = st.sidebar.multiselect("Regions", options=regions, default=regions[:5])

freq = st.sidebar.selectbox("Aggregation", options=['D','W','M'], index=0, format_func=lambda x: {'D':'Daily','W':'Weekly','M':'Monthly'}[x])
engagement_weighted = st.sidebar.checkbox("Use engagement-weighted metric", value=False)
ma_window = st.sidebar.slider("Moving average window", 1, 14, 3)

if st.sidebar.button("Analyze"):
    # apply filters
    kws = selected_keywords if selected_keywords else None
    plats = selected_platforms if selected_platforms else None
    cts = selected_content_types if selected_content_types else None
    regs = selected_regions if selected_regions else None

    filtered = processor.filter_multi(cleaned, keywords=kws, platforms=plats, content_types=cts, regions=regs)
    if filtered.empty:
        st.warning("No data for selected filters.")
    else:
        agg = processor.aggregate(filtered, freq=freq, by_cols=['platform','content_type','region'], engagement_weighted=engagement_weighted)
        st.subheader("Aggregate sample")
        st.dataframe(agg.head(50))

        # show stacked area across platforms (for overall)
        st.subheader("Volume by Platform (stacked)")
        try:
            area_fig = charts.plotly_stacked_area(agg.groupby(['datetime','platform'], as_index=False)['count'].sum())
            st.plotly_chart(area_fig, use_container_width=True)
        except Exception as e:
            st.error(f"Area chart failed: {e}")

        # engagement distribution by platform
        st.subheader("Engagement distribution")
        try:
            box_fig = charts.plotly_box_engagement(filtered, by='platform')
            st.plotly_chart(box_fig, use_container_width=True)
        except Exception as e:
            st.error(f"Box plot failed: {e}")

        # top-by-region heatmap (bar fallback)
        st.subheader("Engagement by Region")
        try:
            region_fig = charts.plotly_region_heatmap(agg)
            st.plotly_chart(region_fig, use_container_width=True)
        except Exception as e:
            st.error(f"Region chart failed: {e}")

        # spike detection & table
        st.subheader("Detected spikes")
        spikes = analytics.spike_detection(agg)
        if not spikes.empty:
            st.dataframe(spikes)
        else:
            st.write("No spikes detected with current parameters.")

        # per-keyword time-series with platform breakdown (first chosen keyword)
        if selected_keywords:
            chosen = selected_keywords[0]
            st.subheader(f"Time series for '{chosen}' (platform breakdown)")
            kw_agg = agg[agg['keyword'].str.lower() == chosen.lower()]
            if kw_agg.empty:
                st.write("No data for this keyword after aggregation.")
            else:
                try:
                    fig_ts = charts.plotly_time_series(kw_agg, chosen, moving_avg=analytics.moving_average(kw_agg, ma_window).tolist(), color_col='platform')
                    st.plotly_chart(fig_ts, use_container_width=True)
                except Exception as e:
                    st.error(f"TS plot failed: {e}")

        # top content types in selected regions (first region)
        if selected_regions:
            r = selected_regions[0]
            st.subheader(f"Top content types in region: {r}")
            top_ct = analytics.region_top_content(filtered, r)
            if not top_ct.empty:
                st.table(top_ct)
            else:
                st.write("No content-type data for this region.")

        # export aggregated file
        st.download_button("Download aggregated CSV", data=agg.to_csv(index=False), file_name="mediapulse_agg.csv")

