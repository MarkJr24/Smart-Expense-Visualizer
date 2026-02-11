import re
from typing import List, Dict, Optional


def extract_currency_and_amount(text: str) -> Optional[Dict[str, any]]:
    """Extract currency and amount from receipt text.
    
    Supports multiple currencies: USD ($), INR (₹), EUR (€), SAR (﷼), AED, etc.
    
    Args:
        text: OCR extracted text from receipt
        
    Returns:
        Dictionary with 'amount' and 'currency' keys, or None if not found
    """
    # Currency patterns with their symbols/codes
    currency_patterns = [
        # Symbol-based patterns
        (r'[$]\s*(\d+(?:,\d{3})*(?:\.\d{2})?)', 'USD', '$'),
        (r'[₹]\s*(\d+(?:,\d{3})*(?:\.\d{2})?)', 'INR', '₹'),
        (r'[€]\s*(\d+(?:,\d{3})*(?:\.\d{2})?)', 'EUR', '€'),
        (r'[﷼]\s*(\d+(?:,\d{3})*(?:\.\d{2})?)', 'SAR', '﷼'),
        
        # Code-based patterns (USD, INR, EUR, SAR, AED, etc.)
        (r'(?:USD|US\$)\s*(\d+(?:,\d{3})*(?:\.\d{2})?)', 'USD', '$'),
        (r'(?:INR|Rs\.?|₹)\s*(\d+(?:,\d{3})*(?:\.\d{2})?)', 'INR', '₹'),
        (r'(?:EUR|€)\s*(\d+(?:,\d{3})*(?:\.\d{2})?)', 'EUR', '€'),
        (r'(?:SAR|﷼)\s*(\d+(?:,\d{3})*(?:\.\d{2})?)', 'SAR', 'SAR'),
        (r'(?:AED|Dhs?\.?)\s*(\d+(?:,\d{3})*(?:\.\d{2})?)', 'AED', 'AED'),
        
        # Reverse patterns (amount before currency)
        (r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*[$]', 'USD', '$'),
        (r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*[₹]', 'INR', '₹'),
        (r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*[€]', 'EUR', '€'),
        (r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:USD|INR|EUR|SAR|AED)', 'MULTI', ''),
    ]
    
    # Keywords that indicate total amount
    total_keywords = [
        'total', 'grand total', 'net total', 'amount payable', 
        'total amount', 'bill total', 'sum', 'balance due',
        'amount due', 'final amount', 'net amount'
    ]
    
    lines = text.split('\n')
    best_match = None
    highest_amount = 0
    
    for line in lines:
        line_lower = line.lower()
        
        # Check if line contains total keywords
        is_total_line = any(keyword in line_lower for keyword in total_keywords)
        
        for pattern, currency_code, symbol in currency_patterns:
            matches = re.findall(pattern, line, re.IGNORECASE)
            
            for match in matches:
                # Remove commas and convert to float
                amount_str = match.replace(',', '')
                try:
                    amount = float(amount_str)
                    
                    # Prioritize total lines and higher amounts
                    priority = amount * (10 if is_total_line else 1)
                    
                    if priority > highest_amount:
                        highest_amount = priority
                        best_match = {
                            'amount': amount,
                            'currency': currency_code,
                            'symbol': symbol,
                            'line': line.strip()
                        }
                except ValueError:
                    continue
    
    return best_match


def extract_expenses_from_text(text: str) -> List[Dict[str, any]]:
    """Extract expense information from OCR text.
    
    Args:
        text: OCR extracted text from receipt
        
    Returns:
        List of expense dictionaries with Amount, Category, and Note
    """
    expenses = []
    
    # Try to extract currency and amount
    currency_info = extract_currency_and_amount(text)
    
    if currency_info:
        # Create a single expense entry with the detected total
        expense = {
            "Amount": currency_info['amount'],
            "Category": "Other",  # Default category
            "Note": f"Extracted from receipt: {currency_info['line'][:50]}",
            "Currency": currency_info['currency'],
            "Symbol": currency_info['symbol']
        }
        expenses.append(expense)
    else:
        # Fallback: try basic number extraction
        lines = text.split('\n')
        for line in lines:
            # Look for any number that could be an amount
            match = re.search(r'(\d+(?:,\d{3})*(?:\.\d{2})?)', line)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = float(amount_str)
                    if amount > 0:  # Only positive amounts
                        expenses.append({
                            "Amount": amount,
                            "Category": "Other",
                            "Note": line.strip()[:50]
                        })
                        break  # Take first valid amount found
                except ValueError:
                    continue
    
    return expenses
