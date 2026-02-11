# Google Cloud Vision OCR Setup Guide

## Quick Start

The app now uses Google Cloud Vision API for receipt scanning instead of local Tesseract OCR.

### Step 1: Get API Credentials

**Option A: API Key (Easiest)**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Cloud Vision API:
   - Go to "APIs & Services" → "Library"
   - Search for "Cloud Vision API"
   - Click "Enable"
4. Create API Key:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy the generated API key

**Option B: Service Account (More Secure)**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a service account
3. Download the JSON key file
4. Save it securely in your project directory

### Step 2: Configure Credentials

**Using API Key:**
1. Create a file named `.env` in the app directory
2. Add this line:
   ```
   GOOGLE_CLOUD_VISION_API_KEY=your_actual_api_key_here
   ```
3. Save the file

**Using Service Account:**
1. Create a file named `.env` in the app directory
2. Add this line:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=path/to/your-service-account-key.json
   ```
3. Save the file

### Step 3: Install Dependencies

Run this command in your terminal:
```bash
pip install google-cloud-vision python-dotenv
```

Or if using the virtual environment:
```bash
.\myenv\Scripts\pip.exe install google-cloud-vision python-dotenv
```

### Step 4: Restart Application

Restart the Streamlit app for changes to take effect.

## Free Tier Limits

Google Cloud Vision API free tier includes:
- **1,000 requests per month** for free
- After that: $1.50 per 1,000 requests

This is more than enough for personal expense tracking!

## Testing

1. Go to "Add/Edit Expenses" tab
2. Upload a receipt image (PNG, JPG, or JPEG)
3. Click "Scan & Extract"
4. The app will extract text using Google Cloud Vision
5. Amount and currency will be auto-detected

## Troubleshooting

**"OCR not configured" error:**
- Make sure `.env` file exists in the app directory
- Verify API key is correct
- Restart the application

**"OCR quota exceeded" error:**
- You've used your free 1,000 requests this month
- Wait until next month or upgrade to paid tier

**"Authentication failed" error:**
- Check your API key is valid
- Ensure Cloud Vision API is enabled in your project
- Verify credentials file path is correct (if using service account)

## Security Note

⚠️ **Never commit your `.env` file to version control!**

The `.env` file contains sensitive credentials. Make sure it's listed in `.gitignore`.
