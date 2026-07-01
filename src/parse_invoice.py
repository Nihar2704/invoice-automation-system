import os
import sys
import json
from prediction import InvoiceParserPipeline

def main():
    if len(sys.argv) < 2:
        print("\nSmart Invoice Automation - CLI Parser")
        print("=" * 40)
        print("Usage:")
        print("  .venv\\Scripts\\python.exe src/parse_invoice.py <path_to_invoice_file>")
        print("\nExample:")
        print("  .venv\\Scripts\\python.exe src/parse_invoice.py data/raw_invoices/mock_invoice_1.pdf")
        sys.exit(1)
        
    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' does not exist.")
        sys.exit(1)
        
    print(f"\nProcessing: {os.path.basename(filepath)}")
    print("-" * 50)
    
    try:
        # Initialize pipeline
        parser = InvoiceParserPipeline()
        
        # Run invoice parser
        result = parser.process_invoice(filepath)
        
        if "error" in result:
            print(f"Pipeline Error: {result['error']}")
            sys.exit(1)
            
        # Format and output the extracted values
        print("\nExtracted Invoice Data (Canonical):")
        print("=" * 50)
        print(json.dumps(result["extracted_values"], indent=4))
        print("=" * 50)
        
        print(f"\nAverage Confidence Score: {result['average_confidence']:.2%}")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("Please verify that Tesseract OCR is installed and properly configured if processing scanned images.")

if __name__ == "__main__":
    main()
