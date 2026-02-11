"""
Cloud-based OCR implementation using Google Cloud Vision API.
Reliable receipt scanning without local Tesseract installation.
"""
import os
import io
from PIL import Image
from typing import Union

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


def _get_vision_client():
    """Get Google Cloud Vision client.
    
    Returns:
        Vision API client
        
    Raises:
        Exception: If API credentials not configured
    """
    try:
        from google.cloud import vision
        
        # Check for API key or service account
        api_key = os.getenv('GOOGLE_CLOUD_VISION_API_KEY')
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        if not api_key and not credentials_path:
            raise Exception(
                "⚠️ OCR not configured.\n\n"
                "To enable receipt scanning:\n"
                "1. Get a free Google Cloud Vision API key from:\n"
                "   https://console.cloud.google.com/apis/credentials\n"
                "2. Create a .env file in the app directory\n"
                "3. Add: GOOGLE_CLOUD_VISION_API_KEY=your_key_here\n"
                "4. Restart the application\n\n"
                "For now, please enter expense details manually."
            )
        
        # Create client
        if api_key:
            # Using API key
            client = vision.ImageAnnotatorClient(
                client_options={"api_key": api_key}
            )
        else:
            # Using service account credentials
            client = vision.ImageAnnotatorClient()
        
        return client
        
    except ImportError:
        raise Exception(
            "⚠️ OCR library not installed.\n\n"
            "Run: pip install google-cloud-vision python-dotenv\n"
            "Then restart the application."
        )


def scan_bill_file(file_obj) -> str:
    """Scan receipt using Google Cloud Vision API.
    
    Args:
        file_obj: Uploaded file from Streamlit
        
    Returns:
        Extracted text from receipt
        
    Raises:
        Exception: User-friendly error if scanning fails
    """
    # Validate image
    try:
        img = Image.open(file_obj)
        
        # Convert to bytes for API
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=img.format or 'PNG')
        img_bytes = img_byte_arr.getvalue()
        
    except Exception:
        raise Exception(
            "❌ Invalid image file.\n\n"
            "Please upload a valid PNG, JPG, or JPEG image."
        )
    
    # Get Vision API client
    try:
        client = _get_vision_client()
    except Exception as e:
        # Re-raise configuration errors
        raise
    
    # Perform OCR
    try:
        from google.cloud import vision
        
        # Create image object
        image = vision.Image(content=img_bytes)
        
        # Perform text detection
        response = client.text_detection(image=image)
        
        # Check for errors
        if response.error.message:
            raise Exception(
                f"❌ OCR API error.\n\n"
                f"Error: {response.error.message}\n\n"
                "Please try again or enter details manually."
            )
        
        # Extract text
        texts = response.text_annotations
        
        if not texts:
            raise Exception(
                "⚠️ No text detected in image.\n\n"
                "Please ensure:\n"
                "• Image is clear and in focus\n"
                "• Receipt text is readable\n"
                "• Image has good lighting\n\n"
                "Or enter expense details manually."
            )
        
        # First annotation contains full text
        full_text = texts[0].description
        
        return full_text
        
    except Exception as e:
        error_str = str(e)
        
        # Re-raise our custom errors
        if any(x in error_str for x in ['⚠️', '❌', 'not configured', 'not installed']):
            raise
        
        # Handle API errors
        if 'quota' in error_str.lower():
            raise Exception(
                "⚠️ OCR quota exceeded.\n\n"
                "Free tier limit reached. Please enter details manually."
            )
        elif 'billing' in error_str.lower():
            raise Exception(
                "⚠️ Billing not enabled.\n\n"
                "Google Cloud Vision API requires billing to be enabled on the project.\n"
                "Even for the free tier, a billing account must be linked.\n\n"
                "Please enable billing at: https://console.cloud.google.com/billing"
            )
        elif 'authentication' in error_str.lower() or 'credentials' in error_str.lower():
            raise Exception(
                "❌ OCR authentication failed.\n\n"
                "Please check your API credentials and try again."
            )
        
        # Generic error
        raise Exception(
            "❌ Receipt scanning failed.\n\n"
            f"Error: {error_str}\n"
            "Please try again or enter expense details manually."
        )


def scan_bill(image_path: Union[str, os.PathLike]) -> str:
    """Scan receipt from file path.
    
    Args:
        image_path: Path to image file
        
    Returns:
        Extracted text from receipt
    """
    with open(image_path, 'rb') as f:
        return scan_bill_file(f)
