import re

def extract_gstin(line: str) -> str:
    """
    Extracts an Indian GSTIN (15 characters) from a text line.
    Format: 2 digits + 5 letters + 4 digits + 1 letter + 1 digit/letter + Z + 1 digit/letter
    """
    # Regex pattern for standard Indian GSTIN
    pattern = r"[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]"
    match = re.search(pattern, line, re.IGNORECASE)
    if match:
        return match.group(0).upper()
    return ""

def extract_date(line: str) -> str:
    """
    Extracts date strings from a text line supporting multiple formats:
    - DD/MM/YYYY, DD-MM-YYYY, YYYY/MM/DD, YYYY-MM-DD
    - DD Month YYYY, Month DD, YYYY, etc.
    """
    # 1. Numeric patterns: YYYY-MM-DD, DD/MM/YYYY, DD-MM-YY, etc.
    numeric_pattern = r"\b\d{1,4}[/\-.]\d{1,2}[/\-.]\d{2,4}\b"
    match = re.search(numeric_pattern, line)
    if match:
        return match.group(0)
        
    # 2. Textual patterns: e.g., "12 June 2026", "June 12, 2026", "12-Jun-2026"
    months_pattern = (
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    )
    
    # DD Month YYYY or DD-Month-YYYY
    text_pattern_1 = rf"\b\d{{1,2}}[\s\-]*{months_pattern}[\s\-]*\d{{2,4}}\b"
    match = re.search(text_pattern_1, line, re.IGNORECASE)
    if match:
        return match.group(0)
        
    # Month DD, YYYY
    text_pattern_2 = rf"\b{months_pattern}\s+\d{{1,2}},?\s+\d{{2,4}}\b"
    match = re.search(text_pattern_2, line, re.IGNORECASE)
    if match:
        return match.group(0)
        
    return ""

def extract_amount(line: str) -> str:
    """
    Extracts monetary numeric values from a line.
    Finds the numeric sequence that represents the amount (handles commas and decimals).
    """
    # Clean standard noise words from line to isolate numeric amount
    clean_line = re.sub(r"(?:total|grand|net|tax|amount|payable|rs|inr|gst|cgst|sgst|igst|value|due|after|balance)[:\s\-\u20b9]*", "", line, flags=re.IGNORECASE)
    
    # Match numbers with potential commas and decimal points (e.g. 45,600.00 or 132334)
    # Look for the last or largest numeric pattern which is typically the amount
    matches = re.findall(r"\b\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?\b|\b\d+(?:\.\d{1,2})?\b", clean_line)
    
    if matches:
        # Filter out very short numeric values that are likely not amounts (like single digits) unless it's the only match
        valid_amounts = [m for m in matches if len(m.replace('.', '').replace(',', '')) > 2]
        if valid_amounts:
            return valid_amounts[-1]  # Usually the last one is the final sum
        return matches[-1]
        
    return ""

def extract_invoice_id(line: str) -> str:
    """
    Extracts an alphanumeric invoice number from a line.
    """
    # Pattern to extract ID after keywords
    pattern_keyword = r"(?:inv(?:oice)?|bill|document|ref(?:erence)?|doc|no|number|code)(?:\s*(?:no|number|id|code))?[:\-\s]+([A-Z0-9\-/]+)"
    match = re.search(pattern_keyword, line, re.IGNORECASE)
    if match:
        # Clean any trailing punctuation
        val = match.group(1).strip()
        if val:
            return val
            
    # Fallback: extract the largest alphanumeric token that looks like an ID
    # Avoid picking up pure words or short numbers
    tokens = re.split(r"[:\s\-]+", line)
    for token in tokens:
        # Token containing numbers and letters, or a long numeric value
        if (re.search(r"[A-Z]", token, re.IGNORECASE) and re.search(r"\d", token)) or (re.match(r"^\d{4,}$", token)):
            # Strip trailing/leading non-alphanumeric chars (like commas/brackets)
            token_clean = re.sub(r"^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$", "", token)
            if len(token_clean) > 3:
                return token_clean
                
    # Ultimate fallback: return the raw line itself stripped of standard labels
    fallback = re.sub(r"^(?:invoice\s*(?:no|number|id)?|bill\s*no|document\s*no|ref\s*no)[:\-\s]+", "", line, flags=re.IGNORECASE)
    return fallback.strip()

def extract_vendor_name(line: str) -> str:
    """
    Extracts vendor/company name from a line by stripping prefix labels.
    """
    # Prefix indicators to strip
    prefix_pattern = r"^(?:billed\s+by|payee|supplier|vendor|from|service\s+provider|tax\s+invoice\s+by)[:\s]*"
    cleaned = re.sub(prefix_pattern, "", line, flags=re.IGNORECASE).strip()
    
    # Strip any trailing punctuation (like commas or colons)
    cleaned = re.sub(r"^[:\-\s,]+|[:\-\s,]+$", "", cleaned)
    return cleaned
