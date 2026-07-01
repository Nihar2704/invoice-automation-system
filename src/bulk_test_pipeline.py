import os
import sys
import json
import glob
from prediction import InvoiceParserPipeline

def run_bulk_test():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    samples_dir = os.path.join(base_dir, "data", "raw_invoices", "test_pack", "demo_samples")
    
    if not os.path.exists(samples_dir):
        print(f"Error: Demo samples directory not found at {samples_dir}")
        sys.exit(1)
        
    pdf_files = sorted(glob.glob(os.path.join(samples_dir, "*.pdf")))
    
    if not pdf_files:
        print("No PDF files found in the demo samples directory.")
        sys.exit(1)
        
    print(f"Found {len(pdf_files)} demo invoices to test.")
    print("=" * 80)
    
    # Initialize pipeline
    try:
        parser = InvoiceParserPipeline()
    except Exception as e:
        print(f"Error initializing pipeline: {e}")
        sys.exit(1)
        
    bulk_results = []
    
    for pdf_path in pdf_files:
        file_name = os.path.basename(pdf_path)
        print(f"\nProcessing {file_name}...")
        print("-" * 50)
        
        try:
            result = parser.process_invoice(pdf_path)
            
            if "error" in result:
                print(f"  Failed: {result['error']}")
                bulk_results.append({
                    "file_name": file_name,
                    "status": "Failed",
                    "error": result["error"]
                })
                continue
                
            vals = result["extracted_values"]
            conf = result["average_confidence"]
            
            print(f"  Vendor Name:   {vals.get('vendor_name')}")
            print(f"  Invoice ID:    {vals.get('invoice_id')}")
            print(f"  Invoice Date:  {vals.get('invoice_date')}")
            print(f"  Due Date:      {vals.get('due_date')}")
            print(f"  Total Amount:  {vals.get('total_amount')} {vals.get('currency')}")
            print(f"  GSTIN:         {vals.get('gstin')}")
            print(f"  Confidence:    {conf:.2%}")
            
            # Identify warnings / alerts
            warnings = []
            if not vals.get("due_date"):
                warnings.append("Missing Due Date")
            if not vals.get("invoice_id"):
                warnings.append("Missing Invoice ID")
            if not vals.get("total_amount"):
                warnings.append("Missing Total Amount")
                
            bulk_results.append({
                "file_name": file_name,
                "status": "Success",
                "extracted_values": vals,
                "average_confidence": conf,
                "warnings": warnings
            })
            
        except Exception as e:
            print(f"  Error processing: {e}")
            bulk_results.append({
                "file_name": file_name,
                "status": "Error",
                "error": str(e)
            })
            
    # Save bulk test report
    report_path = os.path.join(base_dir, "reports", "bulk_test_report.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(bulk_results, f, indent=4)
        
    print("\n" + "=" * 80)
    print("BULK TEST SUMMARY REPORT:")
    print("=" * 80)
    print(f"{'File Name':<42} | {'Status':<7} | {'Conf.':<7} | {'Warnings'}")
    print("-" * 80)
    for res in bulk_results:
        warnings_str = ", ".join(res.get("warnings", [])) if "warnings" in res else res.get("error", "Error")
        conf_str = f"{res['average_confidence']:.1%}" if "average_confidence" in res else "N/A"
        print(f"{res['file_name']:<42} | {res['status']:<7} | {conf_str:<7} | {warnings_str}")
    print("=" * 80)
    print(f"Detailed report saved to {report_path}")

if __name__ == "__main__":
    run_bulk_test()
