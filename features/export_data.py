import streamlit as st
import pandas as pd
from io import BytesIO

def export_data(data):
    st.markdown("""
    <style>
    .code-pill { background: rgba(17,24,39,0.9); color: #a7f3d0; padding: 2px 8px; border-radius: 8px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }
    .export-container { background:#0f172a; padding:16px; border-radius:12px; border:1px solid rgba(255,255,255,0.08); }
    </style>
    """, unsafe_allow_html=True)

    st.subheader("📤 Export Data")

    # PDF export
    if st.button("Download PDF", use_container_width=True):
        try:
            from fpdf import FPDF
            
            # Create PDF
            pdf = FPDF(orientation='L', unit='mm', format='A4')
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Smart Expense Visualizer - Export Report', ln=1, align='C')
            pdf.ln(5)
            
            # Add summary
            if not data.empty and 'Amount' in data.columns:
                total = float(data['Amount'].sum())
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 8, f'Total Expenses: Rs. {total:,.2f}', ln=1)
                pdf.cell(0, 8, f'Total Transactions: {len(data)}', ln=1)
                pdf.ln(5)
            
            # Table header
            pdf.set_font('Arial', 'B', 10)
            pdf.set_fill_color(99, 102, 241)
            pdf.set_text_color(255, 255, 255)
            
            cols = list(data.columns)
            col_width = 270 / len(cols)  # Distribute width evenly
            
            for col in cols:
                pdf.cell(col_width, 8, str(col), border=1, align='C', fill=True)
            pdf.ln()
            
            # Table rows
            pdf.set_font('Arial', '', 9)
            pdf.set_text_color(0, 0, 0)
            
            for idx, row in data.iterrows():
                for col in cols:
                    val = row[col]
                    if col.lower() == 'amount' and isinstance(val, (int, float)):
                        text = f'Rs. {val:,.2f}'
                    else:
                        text = str(val)[:30]  # Limit text length
                    pdf.cell(col_width, 7, text, border=1, align='C')
                pdf.ln()
                
                # Avoid too many rows
                if idx >= 100:
                    pdf.cell(0, 7, '... (showing first 100 rows)', ln=1)
                    break
            
            # Generate PDF
            pdf_output = pdf.output(dest='S').encode('latin-1')
            
            st.download_button(
                label="📥 Click here to download PDF",
                data=pdf_output,
                file_name="expenses_export.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            st.success("✅ PDF generated successfully! Click the button above to download.")
            
        except ImportError:
            st.error("❌ PDF export requires 'fpdf' library. Install it using: pip install fpdf")
        except Exception as e:
            st.error(f"❌ Error generating PDF: {str(e)}")

    csv = data.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "expenses.csv", "text/csv", use_container_width=True)

    # Excel export using xlsxwriter if available
    try:
        import xlsxwriter  # noqa: F401
        buffer_xlsx = BytesIO()
        with pd.ExcelWriter(buffer_xlsx, engine="xlsxwriter") as writer:
            data.to_excel(writer, index=False, sheet_name="Expenses")
            workbook  = writer.book
            worksheet = writer.sheets["Expenses"]
            money_fmt = workbook.add_format({"num_format": "₹#,##0.00"})
            # Apply money format to any column named Amount
            for idx, col in enumerate(data.columns):
                col_width = max(12, min(40, int(data[col].astype(str).str.len().max() if not data.empty else 12) + 2))
                worksheet.set_column(idx, idx, col_width, money_fmt if col.lower() == "amount".lower() else None)
        st.download_button(
            label="Download Excel (.xlsx)",
            data=buffer_xlsx.getvalue(),
            file_name="expenses.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    except Exception:
        st.caption("Install xlsxwriter to enable Excel export.")



    # Settings UI removed per revert request