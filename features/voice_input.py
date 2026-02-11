import streamlit as st
import speech_recognition as sr
import sqlite3
import re

# ✅ Create the table if not exists
def create_table():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount INTEGER,
            category TEXT,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ✅ Insert parsed data to database
def insert_to_db(amount, category, date):
    try:
        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expenses (amount, category, date) VALUES (?, ?, ?)",
                       (amount, category, date))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

# ✅ Extract data from spoken input
def extract_expense_data(text):
    amount_match = re.search(r'\d+', text)
    category_match = re.search(r'for (\w+)', text)
    date_match = re.search(r'on (\w+ \d+)', text)

    amount = int(amount_match.group()) if amount_match else None
    category = category_match.group(1) if category_match else "Unknown"
    date = date_match.group(1) if date_match else "Today"

    return amount, category, date

# ✅ Voice input + processing
def voice_to_text_input():
    st.subheader("🎤 Voice Input (Real)")
    create_table()

    if st.button("Start Listening"):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Listening... Please speak now.")
            audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio)
            st.success(f"Recognized: {text}")

            # ➤ Parse the expense data
            amount, category, date = extract_expense_data(text)
            st.write("Parsed ➤", f"₹{amount}", category, date)

            # ➤ Save to database
            if amount is not None:
                if insert_to_db(amount, category, date):
                    st.success("✅ Expense saved to database!")
                else:
                    st.error("❌ Failed to save.")
            else:
                st.warning("⚠️ No amount detected.")

        except sr.UnknownValueError:
            st.error("Could not understand audio.")
        except sr.RequestError:
            st.error("Could not reach speech recognition service.")
