import streamlit as st

def detect_recurring_expenses(data):
    st.subheader("🔁 Recurring Expenses Detector")

    recurring = data.groupby(['Category', 'Amount']).filter(lambda x: len(x) > 2)
    if not recurring.empty:
        st.info("🔄 Recurring expenses detected:")
        st.dataframe(recurring)
    else:
        st.success("No major recurring expenses found.")
