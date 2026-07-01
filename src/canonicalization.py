import re
import dateparser

def canonicalize_date(date_str: str) -> str:
    """
    Standardises date strings into YYYY-MM-DD format using dateparser.
    """
    if not date_str or not date_str.strip():
        return ""
    
    # Strip any brackets or surrounding noise
    date_clean = re.sub(r"[\[\]()]", "", date_str).strip()
    
    try:
        # dateparser is highly flexible for different text/numeric dates
        parsed = dateparser.parse(date_clean, settings={
            'PREFER_DAY_OF_MONTH': 'first',
            'REQUIRE_PARTS': ['year', 'month'],
            'DATE_ORDER': 'DMY'
        })
        if parsed:
            return parsed.strftime("%Y-%m-%d")
    except Exception:
        pass
        
    return date_clean

def canonicalize_amount(amount_str: str) -> float:
    """
    Cleans and converts money string values to float.
    """
    if not amount_str:
        return 0.0
        
    # Remove commas, spaces, currency symbols
    cleaned = amount_str.replace(",", "").replace(" ", "")
    # Remove any non-numeric and non-decimal chars
    cleaned = re.sub(r"[^\d.]", "", cleaned)
    
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

def detect_currency(raw_line: str) -> str:
    """
    Detects the currency symbol or text and returns the ISO standard code (default: INR).
    """
    upper_line = raw_line.upper()
    if "$" in upper_line or "USD" in upper_line:
        return "USD"
    elif "€" in upper_line or "EUR" in upper_line:
        return "EUR"
    elif "£" in upper_line or "GBP" in upper_line:
        return "GBP"
    return "INR"  # Default for Indian invoices

def canonicalize_vendor(vendor_str: str) -> tuple:
    """
    Standardises vendor name to uppercase, and generates a canonical vendor ID key.
    Returns: (standardized_name, canonical_vendor_id)
    """
    if not vendor_str:
        return "", "VENDOR_UNKNOWN"
        
    # Standardise spelling to uppercase and strip spaces
    vendor_clean = re.sub(r"\s+", " ", vendor_str).strip().upper()
    
    # Generate ID: Remove corporate legal suffixes (PVT, LTD, LLP, INC, etc.)
    id_name = re.sub(r"\b(?:PVT|LTD|PRIVATE|LIMITED|LLP|INC|CORP|CO|AND|&)\b", "", vendor_clean)
    # Remove special characters
    id_name = re.sub(r"[^A-Z0-9\s]", "", id_name)
    # Format with underscores
    tokens = id_name.split()
    vendor_id = f"VENDOR_{'_'.join(tokens)}" if tokens else "VENDOR_UNKNOWN"
    
    return vendor_clean, vendor_id

def canonicalize_gstin(gstin_str: str) -> str:
    """
    Cleans and standardises GSTIN.
    """
    if not gstin_str:
        return ""
    # Strip spaces, hyphens, colons, convert to upper
    cleaned = re.sub(r"[\s\-:]", "", gstin_str).upper()
    return cleaned
