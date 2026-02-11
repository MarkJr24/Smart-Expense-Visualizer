import matplotlib.pyplot as plt
import pandas as pd
from utils.helpers import load_data

def draw_category_chart():
    # Use centralized loader that already handles multiple sources and paths
    df = load_data()

    if df is None or df.empty:
        return None

    # Ensure required columns
    if "Amount" not in df.columns or "Category" not in df.columns:
        return None

    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df = df.dropna(subset=["Amount", "Category"])  # ensure clean data

    if df.empty:
        return None

    category_sum = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)

    if category_sum.empty:
        return None

    fig, ax = plt.subplots()
    category_sum.plot(kind="bar", ax=ax, color="skyblue")
    ax.set_title("Expenses by Category")
    ax.set_ylabel("Amount (₹)")
    ax.set_xlabel("Category")
    fig.tight_layout()
    return fig