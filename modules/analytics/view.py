"""
Analytics UI Module for ARGUS AI Platform.
Features Time-Series Forecasting, ABC Analysis, Pareto 80/20 Rule, and RFM Customer Segmentation.
"""
import streamlit as st
import pandas as pd
import numpy as np
from modules.base_module import BaseModule
from services.analytics_service import AnalyticsService
from services.visualization_service import VisualizationService
from core.session import SessionManager
from core.exceptions import handle_errors


class AnalyticsModule(BaseModule):
    @property
    def module_id(self) -> str:
        return "analytics_engine"

    @property
    def name(self) -> str:
        return "Analytics & Forecasting"

    @property
    def icon(self) -> str:
        return "📊"

    @property
    def category(self) -> str:
        return "Analytics"

    @property
    def order(self) -> int:
        return 60

    @handle_errors(show_traceback=True)
    def render(self) -> None:
        st.title("📊 Advanced Analytics & Predictive Engine")

        df = SessionManager.get_active_df()
        if df is None:
            st.warning("⚠️ No active dataset loaded. Please ingest a dataset first using the File Loader or Database Connectors.")
            return

        st.markdown(f"Working on Active Dataset: **{SessionManager.get(SessionManager.DATASET_METADATA, {}).get('name', 'Dataset')}** ({len(df)} rows)")

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Descriptive Summary",
            "Predictive Forecasting",
            "ABC Classification",
            "Pareto 80/20 Analysis",
            "RFM Customer Segmentation"
        ])

        # 1. Descriptive Summary
        with tab1:
            st.subheader("Descriptive & Diagnostic Statistics")
            summary = AnalyticsService.run_descriptive_summary(df)
            if isinstance(summary, dict) and "message" not in summary:
                st.dataframe(pd.DataFrame(summary).T, use_container_width=True)
            else:
                st.info("No numeric columns available for statistical summary.")

        # 2. Time-Series Forecasting
        with tab2:
            st.subheader("Predictive Time-Series Forecasting")
            cols = list(df.columns)
            date_col = st.selectbox("Select Date / Time Column", options=cols, key="fc_date")
            val_col = st.selectbox("Select Metric Column to Forecast", options=df.select_dtypes(include=[np.number]).columns, key="fc_val")
            periods = st.slider("Forecast Periods (Months / Days)", min_value=1, max_value=24, value=6)

            if st.button("🚀 Run Predictive Forecast Model", type="primary"):
                res = AnalyticsService.run_time_series_forecast(df, date_col=date_col, value_col=val_col, periods=periods)
                st.success(f"Forecast model executed! Model R² Score: {res['model_r2']}, Trend Slope: {res['trend_slope']}")

                df_hist = pd.DataFrame(res["historical"])
                df_fc = pd.DataFrame(res["forecast"])

                # Combined Plotly line chart
                fig = VisualizationService.create_line_chart(df_hist, x_col="date", y_col="actual", title=f"Historical vs Forecasted {val_col}")
                # Add forecast line
                import plotly.graph_objects as go
                fig.add_trace(go.Scatter(x=df_fc["date"], y=df_fc["forecast"], mode="lines+markers", name="Forecasted", line=dict(color="#f59e0b", dash="dash")))
                fig.add_trace(go.Scatter(x=df_fc["date"], y=df_fc["upper_bound"], mode="lines", name="Upper Bound", line=dict(color="rgba(245, 158, 11, 0.3)")))
                fig.add_trace(go.Scatter(x=df_fc["date"], y=df_fc["lower_bound"], mode="lines", name="Lower Bound", fill="tonexty", line=dict(color="rgba(245, 158, 11, 0.3)")))

                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df_fc, use_container_width=True)

        # 3. ABC Analysis
        with tab3:
            st.subheader("ABC Inventory / Revenue Classification")
            item_col = st.selectbox("Select Item / Product Column", options=cols, key="abc_item")
            rev_col = st.selectbox("Select Revenue / Value Column", options=df.select_dtypes(include=[np.number]).columns, key="abc_val")

            if st.button("📊 Run ABC Classification", type="primary"):
                abc_res = AnalyticsService.run_abc_analysis(df, item_col=item_col, value_col=rev_col)
                st.success(f"Total Revenue Analyzed: ${abc_res['total_value']:,}")

                col_s1, col_s2 = st.columns([1, 2])
                with col_s1:
                    st.json(abc_res["summary"])
                with col_s2:
                    df_abc = pd.DataFrame(abc_res["data"])
                    fig_abc = VisualizationService.create_pie_donut_chart(df_abc, names_col="abc_category", values_col=rev_col, title="ABC Category Revenue Breakdown")
                    st.plotly_chart(fig_abc, use_container_width=True)

                st.dataframe(df_abc.head(30), use_container_width=True)

        # 4. Pareto 80/20 Analysis
        with tab4:
            st.subheader("Pareto 80/20 Rule Analysis")
            cat_col = st.selectbox("Select Category Column", options=cols, key="par_cat")
            num_col = st.selectbox("Select Impact Metric Column", options=df.select_dtypes(include=[np.number]).columns, key="par_val")

            if st.button("📉 Generate Pareto Curve", type="primary"):
                pareto_res = AnalyticsService.run_pareto_analysis(df, category_col=cat_col, value_col=num_col)
                st.info(f"💡 Top {pareto_res['top_80_count']} out of {pareto_res['total_categories']} categories drive 80% of total output.")

                df_par = pd.DataFrame(pareto_res["data"])
                fig_par = VisualizationService.create_bar_chart(df_par, x_col=cat_col, y_col=num_col, title=f"Pareto Distribution - {cat_col}")
                st.plotly_chart(fig_par, use_container_width=True)

        # 5. RFM Customer Segmentation
        with tab5:
            st.subheader("RFM Customer Segmentation (K-Means)")
            cust_col = st.selectbox("Select Customer ID Column", options=cols, key="rfm_cust")
            date_col_rfm = st.selectbox("Select Transaction Date Column", options=cols, key="rfm_date")
            amt_col = st.selectbox("Select Purchase Amount Column", options=df.select_dtypes(include=[np.number]).columns, key="rfm_amt")
            n_clusters = st.slider("Number of Customer Clusters", min_value=2, max_value=6, value=4)

            if st.button("🎯 Execute RFM Segmentation Model", type="primary"):
                rfm_res = AnalyticsService.run_rfm_segmentation(df, customer_id_col=cust_col, date_col=date_col_rfm, amount_col=amt_col, clusters=n_clusters)
                st.success("Customer Segmentation Model Completed!")

                st.subheader("Cluster Profile Summary")
                st.dataframe(pd.DataFrame(rfm_res["cluster_summary"]), use_container_width=True)
                st.dataframe(pd.DataFrame(rfm_res["rfm_data"]).head(30), use_container_width=True)
