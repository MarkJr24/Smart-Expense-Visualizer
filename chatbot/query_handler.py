import os
import json
from typing import Optional, Dict, Any


def _load_context() -> Dict[str, Any]:
    """Load minimal expense context to ground LLM responses.

    Falls back to an empty dataset if loading fails.
    """
    try:
        from utils.helpers import load_data
        df = load_data()
        if df is None or df.empty:
            return {"total_spent": 0.0, "top_categories": {}, "rows_preview": []}

        total_spent = float(df["Amount"].fillna(0).sum())
        top_categories = (
            df.groupby("Category")["Amount"].sum().sort_values(ascending=False).head(5).to_dict()
        )
        rows_preview = df.head(10).to_dict(orient="records")
        return {
            "total_spent": total_spent,
            "top_categories": top_categories,
            "rows_preview": rows_preview,
        }
    except Exception:
        return {"total_spent": 0.0, "top_categories": {}, "rows_preview": []}


def _get_openai_key() -> Optional[str]:
    """Resolve OpenAI API key from env or Streamlit secrets, if available."""
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key
    try:
        import streamlit as st  # type: ignore

        return st.secrets.get("OPENAI_API_KEY")  # type: ignore[attr-defined]
    except Exception:
        return None


def _llm_answer(query: str, context: Dict[str, Any]) -> str:
    """Query the OpenAI Chat Completions API with expense context."""
    api_key = _get_openai_key()
    if not api_key:
        return (
            "ChatGPT integration is not configured. Set OPENAI_API_KEY in your environment "
            "or .streamlit/secrets.toml to enable AI responses."
        )

    try:
        # Lazy import to avoid dependency issues if the user hasn't installed openai yet
        from openai import OpenAI  # type: ignore

        client = OpenAI(api_key=api_key)
        system_prompt = (
            "You are a helpful expense assistant embedded in a Streamlit app. "
            "Use the provided JSON context of the user's expenses for computations. "
            "Be concise and numeric when appropriate. Currency is INR (₹)."
        )
        context_str = json.dumps(context, ensure_ascii=False)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Context: {context_str}\n\nQuestion: {query}",
                },
            ],
            temperature=0.2,
            max_tokens=300,
        )
        return resp.choices[0].message.content.strip()  # type: ignore[index]
    except ImportError:
        return (
            "The 'openai' package is not installed. Add 'openai' to requirements and run pip install."
        )
    except Exception as e:
        return f"AI response error: {str(e)}"


def test_ai_connectivity() -> str:
    """Lightweight health check for AI configuration and connectivity."""
    api_key = _get_openai_key()
    if not api_key:
        return "AI disabled: OPENAI_API_KEY not set."
    try:
        from openai import OpenAI  # type: ignore

        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a health-check bot."},
                {"role": "user", "content": "Reply with 'pong'."},
            ],
            temperature=0.0,
            max_tokens=5,
        )
        content = resp.choices[0].message.content.strip().lower()  # type: ignore[index]
        if "pong" in content:
            return "AI OK: connectivity verified."
        return f"AI reachable but unexpected reply: {content}"
    except ImportError:
        return "AI error: 'openai' package not installed."
    except Exception as e:
        return f"AI error: {str(e)}"


def _rule_based_answer(query: str) -> str:
    """Fallback that reads from data/expenses.csv via utils.helpers.load_data."""
    try:
        from utils.helpers import load_data

        df = load_data()
        if df is None or df.empty:
            return "No expense data available yet. Add some expenses first."

        # Normalize columns in case of inconsistent casing
        amount_series = df.get("Amount")
        category_series = df.get("Category")
        date_series = df.get("Date")
        if amount_series is None:
            return "Couldn't find the 'Amount' column in your data."

        low = query.lower()

        # Total spend
        if "total spent" in low or "how much did i spend" in low or "total spend" in low:
            total = float(amount_series.fillna(0).sum())
            return f"You've spent a total of ₹{total:.2f}."

        # Show last N expenses
        import re
        n_match = re.search(r"last\s+(\d+)\s+expenses", low)
        if n_match:
            n = int(n_match.group(1))
            n = max(1, min(n, 50))
            preview_cols = [c for c in ["Date", "Category", "Amount", "Note"] if c in df.columns]
            out = df.tail(n)[preview_cols]
            return out.to_string(index=False)

        if "show last 5 expenses" in low:
            preview_cols = [c for c in ["Date", "Category", "Amount", "Note"] if c in df.columns]
            out = df.tail(5)[preview_cols]
            return out.to_string(index=False)

        # Largest / Smallest expense
        if "largest expense" in low:
            idx = amount_series.astype(float).fillna(0).idxmax()
            row = df.iloc[idx]
            cat = str(row.get("Category", ""))
            date = str(row.get("Date", ""))
            amt = float(row.get("Amount", 0))
            note = str(row.get("Note", "")).strip()
            note_part = f" Note: {note}." if note else ""
            return f"Largest expense: ₹{amt:.2f} on {date} ({cat}).{note_part}"

        if "smallest expense" in low:
            idx = amount_series.astype(float).fillna(0).idxmin()
            row = df.iloc[idx]
            cat = str(row.get("Category", ""))
            date = str(row.get("Date", ""))
            amt = float(row.get("Amount", 0))
            note = str(row.get("Note", "")).strip()
            note_part = f" Note: {note}." if note else ""
            return f"Smallest expense: ₹{amt:.2f} on {date} ({cat}).{note_part}"

        # Average daily spend
        if "average daily spend" in low and date_series is not None:
            import pandas as pd
            dt = pd.to_datetime(date_series, errors="coerce")
            tmp = df.copy()
            tmp["_dt"] = dt
            tmp = tmp.dropna(subset=["_dt"])  # keep valid dates only
            if tmp.empty:
                return "Dates are not parseable to compute daily average."
            daily = tmp.groupby(tmp["_dt"].dt.date)["Amount"].sum()
            if daily.empty:
                return "No daily data available."
            return f"Average daily spend: ₹{float(daily.mean()):.2f}."

        # Category-specific (simple heuristic: look for the word 'on X' or known category words)
        if category_series is not None:
            # Example: "food", "transport", etc.
            known_cats = set(str(c).lower() for c in category_series.dropna().unique())
            matched_cat = None
            for cat in known_cats:
                if cat in low:
                    matched_cat = cat
                    break
            if matched_cat:
                total = float(
                    df[category_series.str.lower() == matched_cat]["Amount"].fillna(0).sum()
                )
                return f"You spent ₹{total:.2f} on {matched_cat}."

        # Compare X vs Y categories: e.g., "compare food vs travel"
        import re as _re
        cmp = _re.search(r"compare\s+([a-zA-Z\s]+)\s+vs\s+([a-zA-Z\s]+)", low)
        if cmp and category_series is not None:
            a = cmp.group(1).strip()
            b = cmp.group(2).strip()
            def _sum_cat(name: str) -> float:
                mask = category_series.astype(str).str.lower().str.contains(name.lower())
                return float(df.loc[mask, "Amount"].fillna(0).sum())
            av = _sum_cat(a)
            bv = _sum_cat(b)
            winner = a if av >= bv else b
            return f"{a.title()}: ₹{av:.2f} vs {b.title()}: ₹{bv:.2f} → Higher: {winner.title()}."

        # Month or date range queries
        if date_series is not None:
            import pandas as pd
            dt = pd.to_datetime(date_series, errors="coerce")
            tmp = df.copy()
            tmp["_dt"] = dt
            tmp = tmp.dropna(subset=["_dt"])  # keep valid dates only

            # monthly total for <Month Year>
            m = _re.search(r"monthly\s+total\s+for\s+([a-zA-Z]+)\s+(\d{4})", low)
            if m and not tmp.empty:
                month_name = m.group(1)
                year = int(m.group(2))
                try:
                    month_num = pd.to_datetime(f"01 {month_name} {year}", dayfirst=True).month
                    sel = (tmp["_dt"].dt.year == year) & (tmp["_dt"].dt.month == month_num)
                    total = float(tmp.loc[sel, "Amount"].fillna(0).sum())
                    return f"Total for {month_name.title()} {year}: ₹{total:.2f}."
                except Exception:
                    pass

            # spend in <Month Year>
            m2 = _re.search(r"spend\s+in\s+([a-zA-Z]+)\s+(\d{4})", low)
            if m2 and not tmp.empty:
                month_name = m2.group(1)
                year = int(m2.group(2))
                try:
                    month_num = pd.to_datetime(f"01 {month_name} {year}", dayfirst=True).month
                    sel = (tmp["_dt"].dt.year == year) & (tmp["_dt"].dt.month == month_num)
                    total = float(tmp.loc[sel, "Amount"].fillna(0).sum())
                    return f"Spend in {month_name.title()} {year}: ₹{total:.2f}."
                except Exception:
                    pass

            # expenses between YYYY-MM-DD and YYYY-MM-DD
            r = _re.search(r"expenses\s+between\s+(\d{4}-\d{2}-\d{2})\s+and\s+(\d{4}-\d{2}-\d{2})", low)
            if r and not tmp.empty:
                try:
                    start = pd.to_datetime(r.group(1))
                    end = pd.to_datetime(r.group(2))
                    sel = (tmp["_dt"] >= start) & (tmp["_dt"] <= end)
                    total = float(tmp.loc[sel, "Amount"].fillna(0).sum())
                    return f"Total between {start.date()} and {end.date()}: ₹{total:.2f}."
                except Exception:
                    pass

        # Summarize last N expenses
        if "summarize last" in low and "expenses" in low:
            n_match2 = re.search(r"summarize\s+last\s+(\d+)\s+expenses", low)
            n = int(n_match2.group(1)) if n_match2 else 10
            n = max(1, min(n, 50))
            preview_cols = [c for c in ["Date", "Category", "Amount", "Note"] if c in df.columns]
            out = df.tail(n)[preview_cols]
            total = float(out.get("Amount", []).fillna(0).sum()) if "Amount" in out.columns else 0.0
            return f"Last {n} expenses (total ₹{total:.2f}):\n" + out.to_string(index=False)

        # Top category
        if ("top" in low and "category" in low) or ("highest" in low and "category" in low):
            if category_series is None:
                return "Couldn't find the 'Category' column in your data."
            grouped = (
                df.groupby(category_series.str.title())["Amount"].sum().sort_values(ascending=False)
            )
            if grouped.empty:
                return "No categorized expenses found."
            top_cat = grouped.index[0]
            top_val = float(grouped.iloc[0])
            return f"Top category: {top_cat} with ₹{top_val:.2f}."

        return (
            "Sorry, I didn’t understand that. Try asking things like 'total spent', "
            "'food expenses', or 'top category'."
        )
    except Exception as e:
        return f"Error processing query: {str(e)}"


def handle_query(user_input: str) -> str:
    """Handle a user query using ChatGPT if configured, else fallback.

    The function auto-loads expense context for the LLM to improve answers.
    """
    query = (user_input or "").strip()
    if not query:
        return "Please enter a question."

    context = _load_context()
    ai_answer = _llm_answer(query, context)

    # If AI isn't configured/available, fall back to the rule-based responder
    if ai_answer.startswith("ChatGPT integration is not configured") or ai_answer.startswith(
        "The 'openai' package is not installed"
    ) or ai_answer.startswith("AI response error"):
        return _rule_based_answer(query)

    return ai_answer