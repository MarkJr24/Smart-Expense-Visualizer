import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def charts_view(data):
    # Custom CSS for beautiful charts
    st.markdown("""
    <style>
    .charts-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .chart-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    /* Section title pill bars */
    .section-bar {
        background: linear-gradient(180deg, #6366f1 0%, #8b5cf6 100%);
        color: #ffffff;
        padding: 14px 18px;
        border-radius: 16px;
        font-weight: 800;
        font-size: 18px;
        box-shadow: 0 8px 18px rgba(99,102,241,0.18);
        display: block;
        width: 100%;
    }
    
    .metric-highlight {
        background: linear-gradient(45deg, #ff6b6b, #feca57);
        color: white !important;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0 20px 0;
        font-weight: bold;
        font-size: 1.2em;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("## 📊 Beautiful Charts & Analytics")
    
    # Check if data is empty
    if data.empty:
        st.info("📊 No expense data available yet. Add some expenses to see charts!")
        return
    
    # Check if required columns exist
    if 'Category' not in data.columns or 'Amount' not in data.columns:
        st.warning("⚠️ Data format issue. Please ensure your data has 'Category' and 'Amount' columns.")
        return
    
    try:
        # Convert Date column to datetime if it exists
        if 'Date' in data.columns:
            data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
            data = data.dropna(subset=['Date'])
        
        # Calculate key metrics
        total_spending = data['Amount'].sum()
        category_totals = data.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        top_category = category_totals.index[0] if not category_totals.empty else "N/A"
        top_category_amount = category_totals.iloc[0] if not category_totals.empty else 0
        
        # Beautiful metrics display
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-highlight">
                💰 Total Spent<br>₹{total_spending:,.0f}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-highlight">
                🏆 Top Category<br>{top_category}
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-highlight">
                📈 Top Amount<br>₹{top_category_amount:,.0f}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
        
        # 1. Beautiful Pie Chart for Category Distribution
        if not category_totals.empty:
            st.markdown('<div class="section-bar">🥧 Category Distribution</div>', unsafe_allow_html=True)
            
            # Create beautiful pie chart
            colors = px.colors.qualitative.Set3
            fig_pie = px.pie(
                values=category_totals.values, 
                names=category_totals.index,
                title="Spending by Category",
                color_discrete_sequence=colors
            )
            
            fig_pie.update_traces(
                textposition='inside', 
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Amount: ₹%{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
            )
            
            fig_pie.update_layout(
                title_font_size=20,
                title_x=0.5,
                font=dict(size=14),
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.01
                )
            )
            
            st.plotly_chart(fig_pie, width='stretch')
        
        # 2. Beautiful Bar Chart for Category Spending
        if not category_totals.empty:
            st.markdown('<div class="section-bar">📊 Category Spending Comparison</div>', unsafe_allow_html=True)
            
            # Create horizontal bar chart for better readability
            fig_bar = px.bar(
                x=category_totals.values,
                y=category_totals.index,
                orientation='h',
                title="Spending by Category",
                color=category_totals.values,
                color_continuous_scale='Viridis'
            )
            
            fig_bar.update_traces(
                hovertemplate='<b>%{y}</b><br>Amount: ₹%{x:,.0f}<extra></extra>',
                marker=dict(line=dict(width=1, color='white'))
            )
            
            fig_bar.update_layout(
                title_font_size=20,
                title_x=0.5,
                xaxis_title="Amount (₹)",
                yaxis_title="Category",
                font=dict(size=14),
                height=400
            )
            
            st.plotly_chart(fig_bar, width='stretch')
        
        # 3. Beautiful Line Chart for Daily Spending Trend
        if 'Date' in data.columns and not data.empty:
            daily_totals = data.groupby(data['Date'].dt.date)['Amount'].sum().reset_index()
            daily_totals.columns = ['Date', 'Amount']
            
            if not daily_totals.empty:
                st.markdown('<div class="section-bar">📈 Daily Spending Trend</div>', unsafe_allow_html=True)
                
                # Create beautiful line chart with area fill
                fig_line = go.Figure()
                
                fig_line.add_trace(go.Scatter(
                    x=daily_totals['Date'],
                    y=daily_totals['Amount'],
                    mode='lines+markers',
                    name='Daily Spending',
                    line=dict(width=3, color='#667eea'),
                    marker=dict(size=8, color='#ff6b6b'),
                    fill='tonexty',
                    fillcolor='rgba(102, 126, 234, 0.1)'
                ))
                
                fig_line.update_layout(
                    title="Daily Spending Trend",
                    title_font_size=20,
                    title_x=0.5,
                    xaxis_title="Date",
                    yaxis_title="Amount (₹)",
                    font=dict(size=14),
                    hovermode='x unified',
                    height=400
                )
                
                fig_line.update_traces(
                    hovertemplate='<b>%{x}</b><br>Amount: ₹%{y:,.0f}<extra></extra>'
                )
                
                st.plotly_chart(fig_line, width='stretch')
        
        # 4. Monthly Spending Analysis
        if 'Date' in data.columns and not data.empty:
            data['Month'] = data['Date'].dt.to_period('M')
            monthly_totals = data.groupby('Month')['Amount'].sum()
            
            if not monthly_totals.empty:
                st.markdown('<div class="section-bar">📅 Monthly Spending Analysis</div>', unsafe_allow_html=True)
                
                # Create beautiful monthly bar chart
                monthly_df = monthly_totals.reset_index()
                monthly_df['Month'] = monthly_df['Month'].astype(str)
                
                fig_monthly = px.bar(
                    monthly_df,
                    x='Month',
                    y='Amount',
                    title="Monthly Spending",
                    color='Amount',
                    color_continuous_scale='Blues'
                )
                
                fig_monthly.update_traces(
                    hovertemplate='<b>%{x}</b><br>Amount: ₹%{y:,.0f}<extra></extra>',
                    marker=dict(line=dict(width=1, color='white'))
                )
                
                fig_monthly.update_layout(
                    title_font_size=20,
                    title_x=0.5,
                    xaxis_title="Month",
                    yaxis_title="Amount (₹)",
                    font=dict(size=14),
                    height=400
                )
                
                st.plotly_chart(fig_monthly, width='stretch')
        
        # 5. Spending Statistics Table
        if not category_totals.empty:
            st.markdown('<div class="section-bar">📋 Detailed Category Statistics</div>', unsafe_allow_html=True)
            
            # Create statistics dataframe
            stats_data = []
            for category, amount in category_totals.items():
                percentage = (amount / total_spending) * 100
                stats_data.append({
                    'Category': category,
                    'Amount': f"₹{amount:,.0f}",
                    'Percentage': f"{percentage:.1f}%",
                    'Count': len(data[data['Category'] == category])
                })
            
            stats_df = pd.DataFrame(stats_data)
            
            # Display with custom styling
            st.dataframe(
                stats_df,
                width='stretch',
                hide_index=True,
                column_config={
                    "Category": st.column_config.TextColumn("Category", width="medium"),
                    "Amount": st.column_config.TextColumn("Amount", width="medium"),
                    "Percentage": st.column_config.TextColumn("Percentage", width="medium"),
                    "Count": st.column_config.NumberColumn("Transactions", width="small")
                }
            )
            
    except Exception as e:
        st.error(f"Error generating charts: {str(e)}")
        st.info("Please check your data format and try again.")
