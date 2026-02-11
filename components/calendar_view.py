import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

def calendar_view(data):
    # Custom CSS for beautiful styling
    st.markdown("""
    <style>
    .calendar-container {
        background: #0f172a;
        padding: 18px;
        border-radius: 14px;
        margin: 10px 0;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 10px 28px rgba(0,0,0,0.35);
    }
    
    .expense-card {
        background: rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 12px;
        margin: 8px 0;
        border: 1px solid rgba(255,255,255,0.08);
        transition: box-shadow 0.2s ease, transform 0.1s ease;
    }
    
    .expense-card:hover {
        box-shadow: 0 8px 20px rgba(0,0,0,0.06);
    }
    
    .day-header {
        background: rgba(255,255,255,0.9);
        color: #000000 !important;
        padding: 12px 16px;
        border-radius: 10px;
        margin: 10px 0;
        font-weight: 700;
        font-size: 1.05em;
        border: 1px solid #e5e7eb;
    }
    
    .day-header * {
        color: #000000 !important;
        text-shadow: none !important;
    }
    
    .day-header div,
    .day-header span {
        color: #000000 !important;
        text-shadow: none !important;
    }
    
    .amount-high {
        color: #000000;
        font-weight: 800;
        font-size: 1.05em;
    }
    
    .amount-medium {
        color: #000000;
        font-weight: 800;
        font-size: 1.05em;
    }
    
    .amount-low {
        color: #000000;
        font-weight: 800;
        font-size: 1.05em;
    }
    
    .category-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 0.8em;
        font-weight: 700;
        margin: 2px;
        color: #ffffff;
    }
    
    .metric-card {
        background: rgba(255,255,255,0.06);
        padding: 16px;
        border-radius: 12px;
        color: #e5e7eb !important;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .metric-value {
        font-size: 1.8em;
        font-weight: 800;
        margin: 8px 0;
        color: #ffffff !important;
    }
    
    .metric-label {
        font-size: 0.9em;
        opacity: .9;
        color: #d1d5db !important;
        font-weight: 700;
    }
    
    /* Force metric text to dark */
    .metric-card div,
    .metric-card span,
    .metric-card label {
        color: #e5e7eb !important;
        text-shadow: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("## 📅 Calendar View")
    
    # Check if data is empty
    if data.empty:
        st.info("📊 No expense data available yet. Add some expenses to see the calendar view!")
        return
    
    # Check if required columns exist
    if 'Date' not in data.columns or 'Category' not in data.columns or 'Amount' not in data.columns:
        st.warning("⚠️ Data format issue. Please ensure your data has 'Date', 'Category', and 'Amount' columns.")
        return
    
    try:
        # Convert Date column to datetime
        data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
        
        # Remove rows with invalid dates
        data = data.dropna(subset=['Date'])
        
        if data.empty:
            st.warning("⚠️ No valid date data found. Please check your date format.")
            return
        
        # Calculate statistics
        total_expenses = data['Amount'].sum()
        total_days = len(data['Date'].dt.date.unique())
        avg_daily = total_expenses / total_days if total_days > 0 else 0
        max_daily = data.groupby(data['Date'].dt.date)['Amount'].sum().max()
        min_daily = data.groupby(data['Date'].dt.date)['Amount'].sum().min()
        
        # Beautiful metrics display
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">₹{total_expenses:,.0f}</div>
                <div class="metric-label">Total Expenses</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_days}</div>
                <div class="metric-label">Active Days</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">₹{avg_daily:,.0f}</div>
                <div class="metric-label">Daily Average</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">₹{max_daily:,.0f}</div>
                <div class="metric-label">Highest Day</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Create a beautiful daily spending trend chart
        daily_totals = data.groupby(data['Date'].dt.date)['Amount'].sum().reset_index()
        daily_totals.columns = ['Date', 'Amount']
        
        fig = px.line(daily_totals, x='Date', y='Amount', 
                     title="Daily Spending Trend",
                     color_discrete_sequence=['#FFFFFF'])
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#FFFFFF'),
            title_font_size=20,
            title_x=0.5
        )
        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=8, color='#ff6b6b')
        )
        st.plotly_chart(fig, width='stretch')
        
        # Group by date and display with beautiful cards
        st.markdown("## 📊 Daily Breakdown")
        
        # Sort dates in descending order (most recent first)
        for date in sorted(data['Date'].unique(), reverse=True):
            day_data = data[data['Date'] == date]
            day_total = day_data['Amount'].sum()
            
            # Determine amount styling based on spending level
            if day_total > avg_daily * 1.5:
                amount_class = "amount-high"
                day_icon = "🔥"
            elif day_total > avg_daily:
                amount_class = "amount-medium"
                day_icon = "📈"
            else:
                amount_class = "amount-low"
                day_icon = "💰"
            
            # Create beautiful day header
            st.markdown(f"""
            <div class="day-header">
                {day_icon} {date.strftime('%A, %d %B %Y')} - <span class="{amount_class}">₹{day_total:,.2f}</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Display expenses in a 4-column grid of compact tiles
            category_colors = {
                'Food': '#ef4444',
                'Travel': '#3b82f6',
                'Shopping': '#8b5cf6',
                'Entertainment': '#f59e0b',
                'Utilities': '#10b981',
                'Health': '#f97316',
                'Education': '#22c55e',
                'Other': '#6b7280'
            }

            cols = st.columns(4)
            for i, (_, expense) in enumerate(day_data.iterrows()):
                with cols[i % 4]:
                    category = expense['Category']
                    amount = expense['Amount']
                    note = expense.get('Note', '')
                    color = category_colors.get(category, '#6b7280')

                    st.markdown(f"""
                    <div class=\"expense-card\" style=\"min-height:84px;\">\
                        <div style=\"display:flex;justify-content:space-between;align-items:center;gap:8px;\">\
                            <div>\
                                <span class=\"category-badge\" style=\"background-color:{color};\">{category}</span>\
                            </div>\
                            <div style=\"font-weight:800;color:{color};\">₹{amount:,.2f}</div>\
                        </div>\
                        <div style=\"margin-top:6px;color:#e5e7eb;font-size:12px;opacity:.9;\">{note if note else 'No note'}\
                        </div>\
                    </div>
                    """, unsafe_allow_html=True)
            
            # Show category breakdown if multiple expenses
            if len(day_data) > 1:
                category_breakdown = day_data.groupby('Category')['Amount'].sum().sort_values(ascending=False)
                
                st.markdown("**📊 Category Breakdown:**")
                cols = st.columns(min(len(category_breakdown), 4))
                
                for i, (category, amount) in enumerate(category_breakdown.items()):
                    with cols[i % 4]:
                        color = category_colors.get(category, '#95a5a6')
                        st.markdown(f"""
                        <div style="text-align: center; padding: 10px; background: {color}20; border-radius: 8px; margin: 5px;">
                            <div style="font-weight: bold; color: {color};">{category}</div>
                            <div style="font-size: 1.1em; font-weight: bold;">₹{amount:,.0f}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error displaying calendar view: {str(e)}")
        st.info("Please check your data format and try again.")
