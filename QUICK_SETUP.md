# Quick Setup Guide - Get Your API Key Now

## Step 1: Sign in to Google Cloud Console

I've opened https://console.cloud.google.com/ for you in the browser.

**Action needed:** Sign in with your Google account.

---

## Step 2: Create or Select a Project

After signing in:

1. Click the project dropdown at the top (next to "Google Cloud")
2. Click "**NEW PROJECT**"
3. Enter a project name (e.g., "Expense Tracker")
4. Click "**CREATE**"
5. Wait for the project to be created (takes ~30 seconds)

---

## Step 3: Enable Cloud Vision API

1. In the search bar at the top, type: **Cloud Vision API**
2. Click on "**Cloud Vision API**" in the results
3. Click the blue "**ENABLE**" button
4. Wait for it to enable (~10 seconds)

---

## Step 4: Create API Key

1. Click the hamburger menu (☰) in the top-left
2. Go to: **APIs & Services** → **Credentials**
3. Click "**+ CREATE CREDENTIALS**" at the top
4. Select "**API Key**"
5. A popup will show your new API key
6. Click "**COPY**" to copy the key

---

## Step 5: Add API Key to .env File

1. Open the file: `c:\Users\dell\OneDrive\Desktop\smart_expense_visualizer output\.env`
2. Find the line: `GOOGLE_CLOUD_VISION_API_KEY=`
3. Paste your API key after the `=` sign
4. Save the file

**Example:**
```
GOOGLE_CLOUD_VISION_API_KEY=AIzaSyDXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

---

## Step 6: Restart the App

Stop the current Streamlit app (Ctrl+C in terminal) and restart it:

```bash
.\myenv\Scripts\python.exe -m streamlit run app.py
```

---

## Step 7: Test Receipt Scanning

1. Go to "**Add/Edit Expenses**" tab
2. Upload a receipt image
3. Click "**Scan & Extract**"
4. Watch the magic happen! ✨

---

## Troubleshooting

**"OCR not configured" error:**
- Make sure you saved the `.env` file
- Verify the API key has no extra spaces
- Restart the app

**"Authentication failed" error:**
- Check that Cloud Vision API is enabled
- Verify the API key is correct
- Try creating a new API key

---

## Free Tier

You get **1,000 free OCR requests per month** - more than enough for personal use!

---

## Security Note

⚠️ **Keep your API key private!** Don't share it or commit it to version control.
