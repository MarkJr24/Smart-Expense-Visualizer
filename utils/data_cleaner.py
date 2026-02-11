import pandas as pd

def clean_data(df):
    df = df.dropna(subset=['Date', 'Category', 'Amount'])
    df['Date'] = pd.to_datetime(df['Date'])
    df['Category'] = df['Category'].str.strip().str.title()
    df['Amount'] = df['Amount'].astype(float)
    return df
