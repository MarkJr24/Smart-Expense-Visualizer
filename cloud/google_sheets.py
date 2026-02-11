import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_gsheet_connection(json_key_path, sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_key_path, scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    return sheet

def append_expense_to_sheet(sheet, expense):
    sheet.append_row([expense['Date'], expense['Category'], expense['Amount'], expense['Note']])
