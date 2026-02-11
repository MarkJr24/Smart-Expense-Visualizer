import streamlit as st
import pandas as pd
from utils.helpers import save_expense, load_data, update_expense_row, delete_expense_row
from ocr.bill_scanner import scan_bill_file
from ocr.extractor_utils import extract_expenses_from_text

def add_expense():
    st.subheader("➕ Add / Edit / Remove Expense")

    with st.form("add_form"):
        date = st.date_input("Date")
        category = st.selectbox("Category", ["Food", "Travel", "Bills", "Shopping", "Other"])
        amount = st.number_input("Amount", min_value=0.0, step=1.0, format="%.2f")
        note = st.text_input("Note")
        submit = st.form_submit_button("Add Expense")

        if submit:
            save_expense(date, category, amount, note)
            st.success("Expense added successfully!")

    st.markdown("---")
    st.subheader("🧾 Scan Receipt (OCR)")

    uploaded = st.file_uploader("Upload a receipt image (PNG/JPG)", type=["png", "jpg", "jpeg"])
    if uploaded is not None:
        if st.button("Scan & Extract"):
            with st.spinner("Scanning receipt..."):
                try:
                    text = scan_bill_file(uploaded)
                    st.text_area("Extracted Text", text, height=150)
                    items = extract_expenses_from_text(text)
                    if not items:
                        st.warning("Couldn't auto-detect amounts/categories. Edit manually below.")
                    for idx, item in enumerate(items or []):
                        st.write(f"Detected item {idx+1}:")
                        with st.form(f"ocr_item_{idx}"):
                            o_date = st.date_input("Date", key=f"ocr_date_{idx}")
                            o_category = st.text_input("Category", value=item.get("Category", "Other"), key=f"ocr_cat_{idx}")
                            o_amount = st.number_input("Amount", min_value=0.0, format="%.2f", value=float(item.get("Amount", 0.0)), key=f"ocr_amt_{idx}")
                            o_note = st.text_input("Note", value=item.get("Note", ""), key=f"ocr_note_{idx}")
                            ok = st.form_submit_button("Save this item")
                            if ok:
                                save_expense(o_date, o_category, o_amount, o_note)
                                st.success("Saved from OCR.")
                except Exception as e:
                    st.error(f"OCR failed: {e}")

    st.markdown("---")
    st.subheader("✏️ Edit or 🗑 Remove Expense")

    df = load_data()
    if df is None or df.empty:
        st.info("No expenses yet to edit or remove.")
        return

    # Show a table and select a row by index
    st.dataframe(df)
    row_index = st.number_input(
        "Select row index to edit/remove",
        min_value=0,
        max_value=len(df) - 1,
        step=1,
        value=0,
        format="%d",
    )

    # Prefill with selected row
    sel = df.iloc[int(row_index)]
    with st.form("edit_form"):
        e_date = st.text_input("Date", value=str(sel.get("Date", "")))
        e_category = st.text_input("Category", value=str(sel.get("Category", "")))
        e_amount = st.number_input(
            "Amount", min_value=0.0, step=1.0, format="%.2f", value=float(sel.get("Amount", 0.0))
        )
        e_note = st.text_input("Note", value=str(sel.get("Note", "")))
        col1, col2 = st.columns(2)
        with col1:
            do_update = st.form_submit_button("Save Changes")
        with col2:
            do_delete = st.form_submit_button("Delete Row")

        if do_update:
            ok = update_expense_row(int(row_index), e_date, e_category, e_amount, e_note)
            if ok:
                st.success("Updated successfully.")
            else:
                st.error("Failed to update.")

        if do_delete:
            ok = delete_expense_row(int(row_index))
            if ok:
                st.success("Deleted successfully.")
            else:
                st.error("Failed to delete.")
