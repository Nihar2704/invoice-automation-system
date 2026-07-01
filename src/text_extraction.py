import os
import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from PIL import Image
import io

# Auto-locate Tesseract OCR on Windows systems
TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Users\nihar\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
]

for path in TESSERACT_PATHS:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        break

def extract_text_from_pdf(filepath: str) -> str:
    """
    Extracts text from a digital PDF using pdfplumber.
    """
    text = ""
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting text with pdfplumber: {e}")
        
    # If pdfplumber yields no text, try PyMuPDF as a fallback
    if not text.strip():
        try:
            doc = fitz.open(filepath)
            for page in doc:
                page_text = page.get_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            print(f"Error extracting text with PyMuPDF: {e}")
            
    return text

def extract_text_via_ocr_from_pdf(filepath: str) -> str:
    """
    Converts scanned PDF pages to images using PyMuPDF and applies Tesseract OCR.
    Doesn't require external binaries like poppler.
    """
    text = ""
    try:
        doc = fitz.open(filepath)
        for page_num in range(len(doc)):
            page = doc[page_num]
            # Render page to a high-quality pixmap (DPI=200 for better OCR quality)
            pix = page.get_pixmap(dpi=200)
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            # Apply Tesseract OCR
            page_text = pytesseract.image_to_string(img)
            if page_text:
                text += page_text + "\n"
    except pytesseract.TesseractNotFoundError:
        raise RuntimeError("Tesseract OCR is not installed or not in the PATH. "
                           "Please install Tesseract OCR (Windows) or configure pytesseract.tesseract_cmd.")
    except Exception as e:
        print(f"Error performing OCR on PDF: {e}")
    return text

def extract_text_from_image(filepath: str) -> str:
    """
    Extracts text from image files (PNG, JPG, JPEG) using Tesseract OCR.
    """
    try:
        img = Image.open(filepath)
        text = pytesseract.image_to_string(img)
        return text
    except pytesseract.TesseractNotFoundError:
        raise RuntimeError("Tesseract OCR is not installed or not in the PATH. "
                           "Please install Tesseract OCR (Windows) or configure pytesseract.tesseract_cmd.")
    except Exception as e:
        print(f"Error performing OCR on image: {e}")
        return ""

def extract_raw_text(filepath: str) -> str:
    """
    Detects the file type and extracts raw text accordingly.
    Automatically switches to OCR if a PDF contains no digital text layers.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
        
    _, ext = os.path.splitext(filepath.lower())
    
    if ext == '.pdf':
        print(f"Extracting text from digital PDF: {filepath}")
        text = extract_text_from_pdf(filepath)
        
        # If no text is found, treat it as a scanned PDF and run OCR
        if not text.strip():
            print("No digital text found. Falling back to OCR on PDF pages...")
            text = extract_text_via_ocr_from_pdf(filepath)
        return text
    elif ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
        print(f"Running OCR on image file: {filepath}")
        return extract_text_from_image(filepath)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Only PDFs and images are supported.")

def split_and_clean_lines(raw_text: str):
    """
    Splits raw text into lines and cleans each line, returning pairs of (raw_line, cleaned_line).
    Stores only non-empty lines.
    """
    from preprocessing import clean_text
    
    lines = raw_text.split('\n')
    line_pairs = []
    
    for line in lines:
        stripped = line.strip()
        if stripped:
            cleaned = clean_text(stripped)
            # Ensure we don't return lines that become completely empty after cleaning
            if cleaned.strip():
                line_pairs.append((stripped, cleaned))
                
    return line_pairs

if __name__ == "__main__":
    # Test script with a simple mock file if executed directly
    print("Tesseract command path configured as:", getattr(pytesseract.pytesseract, 'tesseract_cmd', 'Not found'))
