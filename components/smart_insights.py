import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

def insights_view(data):
    # Custom CSS for beautiful insights
    st.markdown("""
    <style>
    .insights-container {
        background: #0f172a;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 8px 32px rgba(0,0,0,0.25);
    }
    
    .insight-card {
        background: rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        border-left: 4px solid #6366f1;
        color: #e5e7eb !important;
    }
    
    .insight-highlight {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: #ffffff !important;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
        font-weight: bold;
        font-size: 1.3em;
        box-shadow: 0 8px 20px rgba(0,0,0,0.25);
        border: 1px solid rgba(255, 255, 255, 0.15);
        min-height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .insight-item {
        background: rgba(255,255,255,0.06);
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #22c55e;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        color: #e5e7eb !important;
    }
    
    .warning-item {
        background: rgba(245,158,11,0.15);
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #f59e0b;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        color: #e5e7eb !important;
    }
    
    .success-item {
        background: rgba(16,185,129,0.15);
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #10b981;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        color: #e5e7eb !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("## 🧠 Smart Insights & Analytics")
    
    # Check if data is empty
    if data.empty:
        st.info("📊 No expense data available yet. Add some expenses to see insights!")
        return
    
    # Check if required columns exist
    if 'Date' not in data.columns or 'Amount' not in data.columns or 'Category' not in data.columns:
        st.warning("⚠️ Data format issue. Please ensure your data has 'Date', 'Amount', and 'Category' columns.")
        return
    
    try:
        # Convert Date column to datetime
        data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
        data = data.dropna(subset=['Date'])
        
        if data.empty:
            st.warning("⚠️ No valid date data found. Please check your date format.")
            return
        
        # Calculate comprehensive insights
        total_expenses = data['Amount'].sum()
        total_transactions = len(data)
        avg_expense = data['Amount'].mean()
        median_expense = data['Amount'].median()
        
        # Daily analysis
        daily_totals = data.groupby(data['Date'].dt.date)['Amount'].sum()
        max_daily = daily_totals.max()
        min_daily = daily_totals.min()
        avg_daily = daily_totals.mean()
        top_day = daily_totals.idxmax()
        lowest_day = daily_totals.idxmin()
        
        # Category analysis
        category_totals = data.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        top_category = category_totals.index[0]
        top_category_amount = category_totals.iloc[0]
        category_percentage = (top_category_amount / total_expenses) * 100
        
        # Spending patterns
        data['DayOfWeek'] = data['Date'].dt.day_name()
        data['Month'] = data['Date'].dt.month_name()
        data['WeekOfYear'] = data['Date'].dt.isocalendar().week
        
        # Day of week analysis
        dow_spending = data.groupby('DayOfWeek')['Amount'].sum().reindex([
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
        ])
        highest_dow = dow_spending.idxmax()
        highest_dow_amount = dow_spending.max()
        
        # Monthly analysis
        monthly_totals = data.groupby('Month')['Amount'].sum()
        highest_month = monthly_totals.idxmax() if not monthly_totals.empty else "N/A"
        highest_month_amount = monthly_totals.max() if not monthly_totals.empty else 0
        
        # Spending trends
        recent_7_days = data[data['Date'] >= (data['Date'].max() - timedelta(days=7))]
        recent_spending = recent_7_days['Amount'].sum()
        previous_7_days = data[(data['Date'] >= (data['Date'].max() - timedelta(days=14))) & 
                              (data['Date'] < (data['Date'].max() - timedelta(days=7)))]
        previous_spending = previous_7_days['Amount'].sum()
        
        spending_change = ((recent_spending - previous_spending) / previous_spending * 100) if previous_spending > 0 else 0
        
        # Key Metrics Display
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="insight-highlight">
                💰 Total Spent<br>₹{total_expenses:,.0f}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="insight-highlight">
                📊 Transactions<br>{total_transactions}
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="insight-highlight">
                📈 Avg per Transaction<br>₹{avg_expense:,.0f}
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="insight-highlight">
                📅 Active Days<br>{len(daily_totals)}
            </div>
            """, unsafe_allow_html=True)
        
        # Top Insights
        st.markdown("### 🔥 Top Insights")
        
        # Most expensive day
        st.markdown(f"""
        <div class="insight-item">
            <strong>💸 Most Expensive Day:</strong> {top_day.strftime('%A, %B %d, %Y')}<br>
            <strong>Amount:</strong> ₹{max_daily:,.2f} | <strong>Average Daily:</strong> ₹{avg_daily:,.2f}
        </div>
        """, unsafe_allow_html=True)
        
        # Top spending category
        st.markdown(f"""
        <div class="insight-item">
            <strong>🏷️ Top Spending Category:</strong> {top_category}<br>
            <strong>Amount:</strong> ₹{top_category_amount:,.2f} | <strong>Percentage:</strong> {category_percentage:.1f}% of total spending
        </div>
        """, unsafe_allow_html=True)
        
        # Highest spending day of week
        st.markdown(f"""
        <div class="insight-item">
            <strong>📅 Highest Spending Day:</strong> {highest_dow}<br>
            <strong>Amount:</strong> ₹{highest_dow_amount:,.2f}
        </div>
        """, unsafe_allow_html=True)
        

        
        # Spending Patterns Analysis
        st.markdown("### 📊 Spending Patterns")
        
        # Day of week spending chart
        if not dow_spending.empty:
            fig_dow = px.bar(
                x=dow_spending.index,
                y=dow_spending.values,
                title="Spending by Day of Week",
                color=dow_spending.values,
                color_continuous_scale='Viridis'
            )
            fig_dow.update_layout(
                title_font_size=16,
                xaxis_title="Day of Week",
                yaxis_title="Amount (₹)",
                height=300
            )
            st.plotly_chart(fig_dow, width='stretch')
        
        # Budget Analysis
        st.markdown("### 💡 Smart Recommendations")
        
        # Spending trend analysis
        if spending_change > 10:
            st.markdown(f"""
            <div class="warning-item">
                <strong>⚠️ Spending Alert:</strong> Your spending increased by {spending_change:.1f}% in the last 7 days compared to the previous week.
                <br><strong>Recent 7 days:</strong> ₹{recent_spending:,.2f} | <strong>Previous 7 days:</strong> ₹{previous_spending:,.2f}
            </div>
            """, unsafe_allow_html=True)
        elif spending_change < -10:
            st.markdown(f"""
            <div class="success-item">
                <strong>✅ Great Job!</strong> Your spending decreased by {abs(spending_change):.1f}% in the last 7 days compared to the previous week.
                <br><strong>Recent 7 days:</strong> ₹{recent_spending:,.2f} | <strong>Previous 7 days:</strong> ₹{previous_spending:,.2f}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="insight-item">
                <strong>📊 Stable Spending:</strong> Your spending is relatively stable with a {spending_change:+.1f}% change in the last 7 days.
                <br><strong>Recent 7 days:</strong> ₹{recent_spending:,.2f} | <strong>Previous 7 days:</strong> ₹{previous_spending:,.2f}
            </div>
            """, unsafe_allow_html=True)
        
        # Category recommendations
        if category_percentage > 40:
            st.markdown(f"""
            <div class="warning-item">
                <strong>🎯 Category Focus:</strong> {top_category} represents {category_percentage:.1f}% of your total spending. 
                Consider reviewing expenses in this category for potential savings.
            </div>
            """, unsafe_allow_html=True)
        
        # Daily spending recommendations
        if max_daily > avg_daily * 2:
            st.markdown(f"""
            <div class="insight-item">
                <strong>📈 High Spending Day:</strong> Your highest spending day ({top_day.strftime('%A')}) was {max_daily/avg_daily:.1f}x higher than average.
                Consider planning major purchases on lower spending days.
            </div>
            """, unsafe_allow_html=True)
        

        
        # Detailed Statistics
        st.markdown("### 📋 Detailed Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**💰 Amount Statistics:**")
            st.markdown(f"- **Total Expenses:** ₹{total_expenses:,.2f}")
            st.markdown(f"- **Average per Transaction:** ₹{avg_expense:,.2f}")
            st.markdown(f"- **Median Transaction:** ₹{median_expense:,.2f}")
            st.markdown(f"- **Highest Single Day:** ₹{max_daily:,.2f}")
            st.markdown(f"- **Lowest Single Day:** ₹{min_daily:,.2f}")
        
        with col2:
            st.markdown("**📅 Time Statistics:**")
            st.markdown(f"- **Total Transactions:** {total_transactions}")
            st.markdown(f"- **Active Days:** {len(daily_totals)}")
            st.markdown(f"- **Average Daily:** ₹{avg_daily:,.2f}")
            st.markdown(f"- **Highest Day:** {top_day.strftime('%B %d')}")
            st.markdown(f"- **Lowest Day:** {lowest_day.strftime('%B %d')}")
        

        
    except Exception as e:
        st.error(f"Error generating insights: {str(e)}")
        st.info("Please check your data format and try again.")
