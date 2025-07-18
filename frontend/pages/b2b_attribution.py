"""
B2B Marketing Attribution Dashboard

Advanced B2B attribution analysis with lead scoring, account-based attribution,
pipeline velocity tracking, and sales-marketing alignment insights.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
import numpy as np

from frontend.utils.api_client import APIClient
from frontend.utils.visualization import create_attribution_chart, format_currency


class B2BAttributionDashboard:
    """B2B Marketing Attribution Dashboard with advanced analytics."""
    
    def __init__(self):
        self.api_client = APIClient()
        
    def render(self):
        """Render the B2B attribution dashboard."""
        st.set_page_config(
            page_title="B2B Marketing Attribution",
            page_icon="🎯",
            layout="wide"
        )
        
        st.title("🎯 B2B Marketing Attribution Engine")
        st.markdown("""
        **Comprehensive B2B attribution analysis designed for complex sales cycles and account-based marketing.**
        
        This platform analyzes attribution across multiple dimensions:
        - **Time-Weighted Attribution**: Accounts for long B2B sales cycles (3-18 months)
        - **Lead Quality Impact**: Weights touchpoints by lead scoring and demographic fit
        - **Account-Based Attribution**: Considers buying committees and deal complexity
        - **Stage Progression**: Tracks touchpoint influence on funnel advancement
        - **Pipeline Velocity**: Measures impact on sales cycle acceleration
        """)
        
        # Sidebar for controls
        self._render_sidebar()
        
        # Main dashboard tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎯 Attribution Analysis", 
            "📊 Channel Performance", 
            "🤝 Sales-Marketing Alignment",
            "🔄 Pipeline Velocity",
            "⚙️ Model Configuration"
        ])
        
        with tab1:
            self._render_attribution_analysis()
        
        with tab2:
            self._render_channel_performance()
        
        with tab3:
            self._render_sales_marketing_alignment()
        
        with tab4:
            self._render_pipeline_velocity()
        
        with tab5:
            self._render_model_configuration()
    
    def _render_sidebar(self):
        """Render sidebar controls."""
        st.sidebar.header("Analysis Parameters")
        
        # Date range selection
        st.sidebar.subheader("Date Range")
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            st.session_state.date_from = st.date_input(
                "From",
                value=date.today() - timedelta(days=90),
                key="b2b_date_from"
            )
        
        with col2:
            st.session_state.date_to = st.date_input(
                "To",
                value=date.today(),
                key="b2b_date_to"
            )
        
        # Account selection
        st.sidebar.subheader("Account Filtering")
        account_filter = st.sidebar.selectbox(
            "Account Type",
            ["All Accounts", "Enterprise", "Mid-Market", "SMB"],
            key="account_filter"
        )
        
        # Custom account IDs
        custom_accounts = st.sidebar.text_area(
            "Specific Account IDs (one per line)",
            placeholder="account_123\naccount_456",
            key="custom_accounts"
        )
        
        if custom_accounts:
            st.session_state.account_ids = [acc.strip() for acc in custom_accounts.split('\n') if acc.strip()]
        else:
            st.session_state.account_ids = None
        
        # Attribution weights customization
        st.sidebar.subheader("Attribution Weights")
        with st.sidebar.expander("Customize Weights"):
            time_weight = st.slider("Time Decay", 0.0, 1.0, 0.25, 0.05, key="time_weight")
            quality_weight = st.slider("Lead Quality", 0.0, 1.0, 0.25, 0.05, key="quality_weight")
            account_weight = st.slider("Account-Based", 0.0, 1.0, 0.25, 0.05, key="account_weight")
            stage_weight = st.slider("Stage Progression", 0.0, 1.0, 0.15, 0.05, key="stage_weight")
            velocity_weight = st.slider("Pipeline Velocity", 0.0, 1.0, 0.10, 0.05, key="velocity_weight")
            
            # Normalize weights
            total_weight = time_weight + quality_weight + account_weight + stage_weight + velocity_weight
            if total_weight > 0:
                st.session_state.attribution_weights = {
                    'time': time_weight / total_weight,
                    'quality': quality_weight / total_weight,
                    'account': account_weight / total_weight,
                    'stage': stage_weight / total_weight,
                    'velocity': velocity_weight / total_weight
                }
            else:
                st.session_state.attribution_weights = None
    
    def _render_attribution_analysis(self):
        """Render the main attribution analysis."""
        st.header("B2B Attribution Analysis")
        
        # Calculate attribution button
        if st.button("🚀 Calculate B2B Attribution", type="primary"):
            self._calculate_attribution()
        
        # Display results if available
        if hasattr(st.session_state, 'b2b_attribution_results'):
            self._display_attribution_results()
    
    def _calculate_attribution(self):
        """Calculate B2B attribution using the API."""
        try:
            with st.spinner("Calculating B2B attribution... This may take a moment for complex analyses."):
                
                # Prepare request payload
                payload = {
                    "account_ids": st.session_state.get('account_ids'),
                    "date_from": st.session_state.date_from.isoformat(),
                    "date_to": st.session_state.date_to.isoformat(),
                    "attribution_weights": st.session_state.get('attribution_weights')
                }
                
                # Make API call
                response = self.api_client.post("/attribution/b2b/calculate", json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.b2b_attribution_results = result['data']
                    st.success("✅ B2B attribution calculated successfully!")
                else:
                    st.error(f"❌ Error calculating attribution: {response.text}")
                    
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    def _display_attribution_results(self):
        """Display comprehensive attribution results."""
        results = st.session_state.b2b_attribution_results
        
        # Overview metrics
        st.subheader("Attribution Overview")
        
        metadata = results.get('metadata', {})
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Leads Analyzed", metadata.get('leads_analyzed', 0))
        with col2:
            st.metric("Opportunities Analyzed", metadata.get('opportunities_analyzed', 0))
        with col3:
            st.metric("Touchpoints Analyzed", metadata.get('touchpoints_analyzed', 0))
        with col4:
            summary = results.get('attribution_summary', {})
            total_value = summary.get('total_attribution_value', 0)
            st.metric("Total Attribution Value", format_currency(total_value))
        
        # Attribution breakdown by model
        st.subheader("Attribution Model Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Attribution by model type
            model_data = {
                'Time-Weighted': len(results.get('time_weighted_attribution', {})),
                'Quality-Weighted': len(results.get('quality_weighted_attribution', {})),
                'Account-Based': len(results.get('account_based_attribution', {})),
                'Stage Progression': len(results.get('stage_progression_attribution', {})),
                'Pipeline Velocity': len(results.get('pipeline_velocity_attribution', {}))
            }
            
            fig = px.bar(
                x=list(model_data.keys()),
                y=list(model_data.values()),
                title="Touchpoints by Attribution Model",
                labels={'x': 'Attribution Model', 'y': 'Number of Touchpoints'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top touchpoints from combined model
            combined_attribution = results.get('combined_b2b_attribution', {})
            if combined_attribution:
                top_touchpoints = sorted(
                    combined_attribution.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
                
                df_top = pd.DataFrame(top_touchpoints, columns=['Touchpoint ID', 'Attribution Value'])
                df_top['Attribution Value'] = df_top['Attribution Value'].apply(format_currency)
                
                st.subheader("Top Contributing Touchpoints")
                st.dataframe(df_top, use_container_width=True)
        
        # Detailed attribution breakdown
        with st.expander("📊 Detailed Attribution Breakdown"):
            attribution_tabs = st.tabs([
                "Combined Model", "Time-Weighted", "Quality-Weighted", 
                "Account-Based", "Stage Progression", "Pipeline Velocity"
            ])
            
            attribution_models = [
                ('combined_b2b_attribution', "Combined B2B Model"),
                ('time_weighted_attribution', "Time-Weighted Attribution"),
                ('quality_weighted_attribution', "Quality-Weighted Attribution"),
                ('account_based_attribution', "Account-Based Attribution"),
                ('stage_progression_attribution', "Stage Progression Attribution"),
                ('pipeline_velocity_attribution', "Pipeline Velocity Attribution")
            ]
            
            for i, (model_key, model_name) in enumerate(attribution_models):
                with attribution_tabs[i]:
                    model_data = results.get(model_key, {})
                    if model_data:
                        df_model = pd.DataFrame([
                            {'Touchpoint ID': tp_id, 'Attribution Value': value}
                            for tp_id, value in model_data.items()
                        ])
                        df_model = df_model.sort_values('Attribution Value', ascending=False)
                        
                        # Create visualization
                        fig = px.bar(
                            df_model.head(20),
                            x='Attribution Value',
                            y='Touchpoint ID',
                            orientation='h',
                            title=f"{model_name} - Top 20 Touchpoints"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Show data table
                        st.dataframe(df_model, use_container_width=True)
                    else:
                        st.info(f"No data available for {model_name}")
    
    def _render_channel_performance(self):
        """Render channel performance analysis."""
        st.header("Channel Performance Insights")
        
        if st.button("📊 Analyze Channel Performance", type="primary"):
            self._get_channel_insights()
        
        if hasattr(st.session_state, 'channel_insights'):
            self._display_channel_insights()
    
    def _get_channel_insights(self):
        """Get channel performance insights from API."""
        try:
            with st.spinner("Analyzing channel performance..."):
                payload = {
                    "account_ids": st.session_state.get('account_ids'),
                    "date_from": st.session_state.date_from.isoformat(),
                    "date_to": st.session_state.date_to.isoformat()
                }
                
                response = self.api_client.post("/attribution/b2b/channel-insights", json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.channel_insights = result['data']
                    st.success("✅ Channel insights generated successfully!")
                else:
                    st.error(f"❌ Error generating insights: {response.text}")
                    
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    def _display_channel_insights(self):
        """Display channel performance insights."""
        insights = st.session_state.channel_insights
        
        channels = insights.get('channels', {})
        insights_list = insights.get('insights', [])
        summary = insights.get('summary', {})
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Channels", summary.get('total_channels', 0))
        with col2:
            best_channel = summary.get('best_performing_channel', 'N/A')
            st.metric("Best Performing Channel", best_channel)
        with col3:
            analysis_period = summary.get('analysis_period', 'Unknown')
            st.metric("Analysis Period", analysis_period)
        
        # Channel performance table
        if channels:
            st.subheader("Channel Performance Metrics")
            
            df_channels = pd.DataFrame.from_dict(channels, orient='index')
            df_channels = df_channels.round(2)
            df_channels = df_channels.sort_values('roi', ascending=False)
            
            # Format currency columns
            currency_cols = ['total_attribution', 'total_cost']
            for col in currency_cols:
                if col in df_channels.columns:
                    df_channels[f'{col}_formatted'] = df_channels[col].apply(format_currency)
            
            st.dataframe(df_channels, use_container_width=True)
            
            # ROI visualization
            col1, col2 = st.columns(2)
            
            with col1:
                fig_roi = px.bar(
                    df_channels.reset_index(),
                    x='index',
                    y='roi',
                    title="ROI by Channel",
                    labels={'index': 'Channel', 'roi': 'ROI'}
                )
                st.plotly_chart(fig_roi, use_container_width=True)
            
            with col2:
                fig_cost = px.scatter(
                    df_channels.reset_index(),
                    x='total_cost',
                    y='total_attribution',
                    size='touchpoint_count',
                    color='roi',
                    hover_name='index',
                    title="Cost vs Attribution by Channel",
                    labels={
                        'total_cost': 'Total Cost',
                        'total_attribution': 'Total Attribution',
                        'index': 'Channel'
                    }
                )
                st.plotly_chart(fig_cost, use_container_width=True)
        
        # Actionable insights
        if insights_list:
            st.subheader("🎯 Actionable Insights")
            for i, insight in enumerate(insights_list, 1):
                st.markdown(f"**{i}.** {insight}")
    
    def _render_sales_marketing_alignment(self):
        """Render sales-marketing alignment analysis."""
        st.header("Sales-Marketing Alignment Report")
        
        if st.button("🤝 Generate Alignment Report", type="primary"):
            self._get_alignment_report()
        
        if hasattr(st.session_state, 'alignment_report'):
            self._display_alignment_report()
    
    def _get_alignment_report(self):
        """Get sales-marketing alignment report from API."""
        try:
            with st.spinner("Generating alignment report..."):
                payload = {
                    "account_ids": st.session_state.get('account_ids'),
                    "date_from": st.session_state.date_from.isoformat(),
                    "date_to": st.session_state.date_to.isoformat()
                }
                
                response = self.api_client.post("/attribution/b2b/alignment-report", json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.alignment_report = result['data']
                    st.success("✅ Alignment report generated successfully!")
                else:
                    st.error(f"❌ Error generating report: {response.text}")
                    
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    def _display_alignment_report(self):
        """Display sales-marketing alignment report."""
        report = st.session_state.alignment_report
        
        # Alignment score and grade
        col1, col2, col3 = st.columns(3)
        
        with col1:
            score = report.get('alignment_score', 0)
            st.metric("Alignment Score", f"{score:.1f}/100")
        
        with col2:
            grade = report.get('grade', 'F')
            st.metric("Alignment Grade", grade)
        
        with col3:
            total_attr = (
                report.get('sales_attribution', 0) + 
                report.get('marketing_attribution', 0) + 
                report.get('joint_attribution', 0)
            )
            st.metric("Total Attribution", format_currency(total_attr))
        
        # Attribution split visualization
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart of attribution split
            labels = ['Sales', 'Marketing', 'Joint']
            values = [
                report.get('sales_percentage', 0),
                report.get('marketing_percentage', 0),
                report.get('joint_percentage', 0)
            ]
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                title="Attribution Split by Team"
            )])
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Attribution amounts
            attr_data = {
                'Team': ['Sales', 'Marketing', 'Joint'],
                'Attribution': [
                    report.get('sales_attribution', 0),
                    report.get('marketing_attribution', 0),
                    report.get('joint_attribution', 0)
                ],
                'Percentage': [
                    report.get('sales_percentage', 0),
                    report.get('marketing_percentage', 0),
                    report.get('joint_percentage', 0)
                ]
            }
            
            df_attr = pd.DataFrame(attr_data)
            df_attr['Attribution'] = df_attr['Attribution'].apply(format_currency)
            df_attr['Percentage'] = df_attr['Percentage'].round(1)
            
            st.subheader("Attribution Breakdown")
            st.dataframe(df_attr, use_container_width=True)
        
        # Recommendations
        recommendations = report.get('recommendations', [])
        if recommendations:
            st.subheader("📋 Alignment Recommendations")
            for i, recommendation in enumerate(recommendations, 1):
                st.markdown(f"**{i}.** {recommendation}")
        
        # Alignment score interpretation
        with st.expander("📖 Understanding Your Alignment Score"):
            st.markdown("""
            **Alignment Score Interpretation:**
            - **90-100 (A+)**: Excellent alignment - sales and marketing work seamlessly together
            - **80-89 (A)**: Very good alignment with minor optimization opportunities
            - **70-79 (B)**: Good alignment but room for improvement in collaboration
            - **60-69 (C)**: Moderate alignment - consider joint planning and activities
            - **50-59 (D)**: Poor alignment - urgent need for better coordination
            - **0-49 (F)**: Very poor alignment - fundamental process and communication issues
            
            **Ideal Balance:** ~40% Marketing, ~40% Sales, ~20% Joint touchpoints
            """)
    
    def _render_pipeline_velocity(self):
        """Render pipeline velocity analysis."""
        st.header("Pipeline Velocity Analysis")
        
        st.info("📊 Pipeline velocity metrics help understand how touchpoints impact deal acceleration and sales cycle optimization.")
        
        # This would be expanded with actual velocity data
        st.markdown("""
        **Coming Soon: Enhanced Pipeline Velocity Analytics**
        
        This section will include:
        - Sales cycle acceleration analysis
        - Touchpoint impact on deal velocity
        - Stage progression timing
        - Velocity benchmarks by deal size
        - Predictive cycle length modeling
        """)
    
    def _render_model_configuration(self):
        """Render model configuration and information."""
        st.header("B2B Attribution Model Configuration")
        
        # Get model information
        if st.button("📋 Load Model Information"):
            self._get_model_info()
        
        if hasattr(st.session_state, 'model_info'):
            self._display_model_info()
        
        # Touchpoint types
        if st.button("🏷️ Load Touchpoint Types"):
            self._get_touchpoint_types()
        
        if hasattr(st.session_state, 'touchpoint_types'):
            self._display_touchpoint_types()
    
    def _get_model_info(self):
        """Get B2B model information from API."""
        try:
            response = self.api_client.get("/attribution/b2b/model-info")
            
            if response.status_code == 200:
                result = response.json()
                st.session_state.model_info = result['data']
                st.success("✅ Model information loaded!")
            else:
                st.error(f"❌ Error loading model info: {response.text}")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    def _display_model_info(self):
        """Display B2B model information."""
        info = st.session_state.model_info
        
        st.subheader(f"🎯 {info.get('model_name', 'Unknown Model')}")
        st.markdown(f"**Version:** {info.get('version', 'Unknown')}")
        st.markdown(f"**Description:** {info.get('description', 'No description available')}")
        
        # Attribution factors
        factors = info.get('attribution_factors', {})
        if factors:
            st.subheader("Attribution Factors")
            
            df_factors = pd.DataFrame([
                {
                    'Factor': factor.replace('_', ' ').title(),
                    'Weight': data.get('weight', 0),
                    'Description': data.get('description', '')
                }
                for factor, data in factors.items()
            ])
            
            st.dataframe(df_factors, use_container_width=True)
        
        # B2B features
        features = info.get('b2b_features', [])
        if features:
            st.subheader("B2B-Specific Features")
            for feature in features:
                st.markdown(f"• {feature}")
        
        # Data requirements
        requirements = info.get('data_requirements', {})
        if requirements:
            st.subheader("Data Requirements")
            
            for category, fields in requirements.items():
                with st.expander(f"{category.title()} Data"):
                    for field in fields:
                        st.markdown(f"• `{field}`")
    
    def _get_touchpoint_types(self):
        """Get touchpoint types from API."""
        try:
            response = self.api_client.get("/attribution/b2b/touchpoint-types")
            
            if response.status_code == 200:
                result = response.json()
                st.session_state.touchpoint_types = result['data']
                st.success("✅ Touchpoint types loaded!")
            else:
                st.error(f"❌ Error loading touchpoint types: {response.text}")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    def _display_touchpoint_types(self):
        """Display touchpoint types and weights."""
        data = st.session_state.touchpoint_types
        
        touchpoint_types = data.get('touchpoint_types', {})
        
        if touchpoint_types:
            st.subheader("B2B Touchpoint Types & Weights")
            
            df_touchpoints = pd.DataFrame([
                {
                    'Touchpoint Type': tp_type.replace('_', ' ').title(),
                    'Attribution Weight': info.get('weight', 1.0),
                    'Category': info.get('category', 'Other'),
                    'Description': info.get('description', '')
                }
                for tp_type, info in touchpoint_types.items()
            ])
            
            df_touchpoints = df_touchpoints.sort_values('Attribution Weight', ascending=False)
            st.dataframe(df_touchpoints, use_container_width=True)
            
            # Visualization of weights by category
            fig = px.bar(
                df_touchpoints,
                x='Touchpoint Type',
                y='Attribution Weight',
                color='Category',
                title="Attribution Weights by Touchpoint Type"
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Lead quality multipliers
        quality_multipliers = data.get('lead_quality_multipliers', {})
        if quality_multipliers:
            st.subheader("Lead Quality Multipliers")
            
            df_quality = pd.DataFrame([
                {'Quality Tier': tier, 'Multiplier': multiplier}
                for tier, multiplier in quality_multipliers.items()
            ])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.dataframe(df_quality, use_container_width=True)
            
            with col2:
                fig_quality = px.bar(
                    df_quality,
                    x='Quality Tier',
                    y='Multiplier',
                    title="Lead Quality Multipliers"
                )
                st.plotly_chart(fig_quality, use_container_width=True)


def main():
    """Main function to run the B2B Attribution Dashboard."""
    dashboard = B2BAttributionDashboard()
    dashboard.render()


if __name__ == "__main__":
    main()