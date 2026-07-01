import os
import fitz  # PyMuPDF
import json
from prediction import InvoiceParserPipeline

def generate_mock_pdf(pdf_path: str):
    """
    Generates a digital PDF with invoice text using PyMuPDF.
    """
    print(f"Generating mock digital PDF at: {pdf_path}")
    doc = fitz.open()
    page = doc.new_page()
    
    # Write text layout
    lines = [
        "Tax Invoice By: Shandilya Facility Services",
        "Prepared on behalf of supplier",
        "Invoice Code: GST-2026-9988",
        "Date: 12-Jun-2026",
        "Due Date: 25 June 2026",
        "GSTIN of Supplier: 22ABCDE1234F1Z5",
        "GST Tax Value: Rs. 2,400.00",
        "Total Payable After Tax: Rs. 45,600.00",
        "Thank you for your business!"
    ]
    
    y = 50
    for line in lines:
        page.insert_text(fitz.Point(50, y), line, fontsize=12, fontname="helv")
        y += 25
        
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    doc.save(pdf_path)
    doc.close()
    print("Mock PDF generated successfully.")

def test_pipeline():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mock_pdf_path = os.path.join(base_dir, "data", "raw_invoices", "mock_invoice_1.pdf")
    
    # 1. Generate test PDF
    generate_mock_pdf(mock_pdf_path)
    
    # 2. Initialize Parser Pipeline
    parser = InvoiceParserPipeline()
    
    # 3. Process Invoice
    print("\nProcessing invoice through extraction and classification pipeline...")
    result = parser.process_invoice(mock_pdf_path)
    
    # 4. Print Results
    print("\n" + "=" * 50)
    print("E2E PIPELINE EXTRACTION RESULTS:")
    print("=" * 50)
    print(json.dumps(result["extracted_values"], indent=4))
    print("=" * 50)
    
    print("\nField Metadata & Confidences:")
    print("-" * 50)
    for field, meta in result["field_metadata"].items():
        print(f"Field:       {field.upper()}")
        print(f"Source Line: \"{meta['raw_text_source']}\"")
        print(f"Raw Value:   \"{meta['raw_value']}\"")
        print(f"Canonical:   \"{meta['canonical_value']}\"")
        print(f"Confidence:  {meta['confidence']:.2%}")
        print(f"Status:      {meta['status']}")
        print("-" * 50)
        
    print(f"\nAverage Confidence Score: {result['average_confidence']:.2%}")

if __name__ == "__main__":
    test_pipeline()
