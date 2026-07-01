import re

def clean_text(text: str) -> str:
    """
    Cleans raw invoice line text by stripping leading/trailing whitespace,
    collapsing multiple spaces, and normalising digits to '0' to standardise structure.
    Punctuation is preserved as it contains valuable hints for line classification.
    """
    if not isinstance(text, str):
        return ""
    
    # Trim leading and trailing whitespace
    text = text.strip()
    
    # Replace multiple spaces/whitespace characters with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Normalize digits to '0' to reduce vocabulary sparseness
    text = re.sub(r'\d', '0', text)
    
    return text
