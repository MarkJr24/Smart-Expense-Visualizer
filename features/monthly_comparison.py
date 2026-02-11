import streamlit as st
import pandas as pd
import altair as alt

def show_monthly_comparison(data):
    st.subheader("📆 Monthly Comparison")

    # Check if data is empty
    if data.empty:
        st.info("📊 No expense data available yet. Add some expenses to see monthly comparison!")
        return
    
    # Check if required columns exist
    if 'Date' not in data.columns or 'Amount' not in data.columns:
        st.warning("⚠️ Data format issue. Please ensure your data has 'Date' and 'Amount' columns.")
        return

    try:
        # Use real timestamps for month aggregation to avoid Period -> epoch issues
        safe = data.copy()
        safe['Date'] = pd.to_datetime(safe['Date'], errors='coerce')
        safe = safe.dropna(subset=['Date'])

        if safe.empty:
            st.warning("⚠️ No valid date data found. Please check your date format.")
            return

        # Resample to month start and sum amounts
        monthly = (
            safe.set_index('Date')
                .resample('MS')['Amount']
                .sum()
                .sort_index()
        )

        if monthly.empty:
            st.info("No monthly data available for comparison.")
            return

        # Simple line chart for monthly totals
        st.line_chart(monthly)
        
    except Exception as e:
        st.error(f"Error generating monthly comparison: {str(e)}")
        st.info("Please check your data format and try again.")
