import streamlit as st

def check_budget_alerts(data):
    st.subheader("🚨 Budget Alerts")

    # Check if data is empty
    if data.empty:
        st.info("📊 No expense data available yet. Add some expenses to see budget alerts!")
        return
    
    # Check if required columns exist
    if 'Category' not in data.columns or 'Amount' not in data.columns:
        st.warning("⚠️ Data format issue. Please ensure your data has 'Category' and 'Amount' columns.")
        return

    try:
        alerts = []
        category_sums = data.groupby('Category')['Amount'].sum()

        BUDGET_LIMITS = {
            "Food": 1000,
            "Travel": 500,
            "Bills": 1500,
            "Shopping": 800,
            "Other": 300
        }
        
        for category, limit in BUDGET_LIMITS.items():
            if category in category_sums and category_sums[category] > limit:
                alerts.append(f"⚠️ {category} exceeded the limit of ₹{limit} (Spent: ₹{category_sums[category]:.2f})")

        if alerts:
            for alert in alerts:
                st.warning(alert)
        else:
            st.success("All categories are within budget ✅")
            
    except Exception as e:
        st.error(f"Error checking budget alerts: {str(e)}")
        st.info("Please check your data format and try again.")
