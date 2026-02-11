import pandas as pd
import os
from pathlib import Path
import streamlit as st

# Import portable configuration
try:
    from portable_config import DATA_DIR, REPORTS_DIR, BASE_DIR
    PORTABLE_MODE = True
except ImportError:
    PORTABLE_MODE = False


def _resolve_shared_data_path() -> str:
    """Resolve a single shared expenses CSV path for the entire project.

    Priority:
    1) ENV var EXPENSES_CSV_PATH
    2) Portable mode data directory
    3) The nearest ancestor directory containing data/expenses.csv
    4) Create data/expenses.csv in the project directory containing this file
    """
    # 1) Environment variable override
    env_path = os.getenv("EXPENSES_CSV_PATH")
    if env_path:
        path = Path(env_path).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        return str(path)

    # 2) Portable mode - use portable data directory
    if PORTABLE_MODE:
        portable_path = DATA_DIR / "expenses.csv"
        portable_path.parent.mkdir(parents=True, exist_ok=True)
        return str(portable_path)

    # 3) Walk up from this file and current working dir to find an existing data/expenses.csv
    search_roots = []
    this_dir = Path(__file__).resolve().parent
    search_roots.append(this_dir)
    search_roots.extend(this_dir.parents)
    search_roots.append(Path.cwd())

    for root in search_roots:
        candidate = (root / "data" / "expenses.csv").resolve()
        if candidate.exists():
            return str(candidate)

    # 4) Fallback: create under the topmost project dir that contains this file
    project_root = this_dir
    if len(this_dir.parents) > 0:
        project_root = this_dir.parents[0]
    fallback = (project_root / "data" / "expenses.csv").resolve()
    fallback.parent.mkdir(parents=True, exist_ok=True)
    return str(fallback)


DATA_PATH = _resolve_shared_data_path()


def load_data():
    """Load expense data from multiple sources and merge them."""
    all_data = []
    
    # 1. Load from main data/expenses.csv (if exists)
    if os.path.exists(DATA_PATH):
        try:
            main_data = pd.read_csv(DATA_PATH)
            if not main_data.empty:
                all_data.append(main_data)
        except Exception as e:
            st.warning(f"Could not load main data: {e}")
    
    # 2. Load from reports/expenses_summary.csv (if exists)
    reports_path = Path(__file__).parent.parent / "reports" / "expenses_summary.csv"
    if reports_path.exists():
        try:
            reports_data = pd.read_csv(reports_path)
            if not reports_data.empty:
                # Add Note column if it doesn't exist
                if 'Note' not in reports_data.columns:
                    reports_data['Note'] = ''
                all_data.append(reports_data)
        except Exception as e:
            st.warning(f"Could not load reports data: {e}")
    
    # 3. Load from data/expenses.csv (if exists and different from DATA_PATH)
    data_expenses_path = Path(__file__).parent.parent / "data" / "expenses.csv"
    if data_expenses_path.exists() and str(data_expenses_path) != DATA_PATH:
        try:
            data_expenses = pd.read_csv(data_expenses_path)
            if not data_expenses.empty:
                all_data.append(data_expenses)
        except Exception as e:
            st.warning(f"Could not load data/expenses.csv: {e}")
    
    # Merge all data
    if all_data:
        combined_data = pd.concat(all_data, ignore_index=True)
        # Remove duplicates based on Date, Category, Amount
        combined_data = combined_data.drop_duplicates(subset=['Date', 'Category', 'Amount'], keep='first')
        # Sort by date
        combined_data['Date'] = pd.to_datetime(combined_data['Date'], errors='coerce')
        combined_data = combined_data.sort_values('Date').reset_index(drop=True)
        return combined_data
    else:
        return pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])


def save_expense(date, category, amount, note):
    new = pd.DataFrame([
        {
            "Date": date,
            "Category": category,
            "Amount": amount,
            "Note": note,
        }
    ])
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        df = pd.concat([df, new], ignore_index=True)
    else:
        df = new
    Path(DATA_PATH).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_PATH, index=False)


def get_data_path() -> str:
    """Return the resolved shared CSV path used across the app."""
    return DATA_PATH


def update_expense_row(row_index: int, date, category, amount, note) -> bool:
    """Update a specific row by index. Returns True on success."""
    try:
        if os.path.exists(DATA_PATH):
            df = pd.read_csv(DATA_PATH)
        else:
            return False
        if row_index < 0 or row_index >= len(df):
            return False
        df.at[row_index, "Date"] = str(date)
        df.at[row_index, "Category"] = category
        df.at[row_index, "Amount"] = float(amount)
        df.at[row_index, "Note"] = note
        Path(DATA_PATH).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(DATA_PATH, index=False)
        return True
    except Exception:
        return False



def delete_expense_row(row_index: int) -> bool:
    """Delete a specific row by index. Returns True on success."""
    try:
        if os.path.exists(DATA_PATH):
            df = pd.read_csv(DATA_PATH)
        else:
            return False
        if row_index < 0 or row_index >= len(df):
            return False
        df = df.drop(index=row_index).reset_index(drop=True)
        Path(DATA_PATH).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(DATA_PATH, index=False)
        return True
    except Exception:
        return False
