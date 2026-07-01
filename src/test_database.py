import os
import sqlite3
import json
from database import save_invoice, update_invoice, get_all_invoices, get_invoice_by_id, delete_invoice
from duplicate_detection import check_duplicate_invoice

def test_database_operations():
    print("Initializing Database Test...")
    db_path = "data/processed/test_invoices.db"
    
    # Clean up previous test DB if exists
    if os.path.exists(db_path):
        os.remove(db_path)
        
    # Mock parser output dictionary
    mock_result = {
        "file_name": "test_invoice_99.pdf",
        "extracted_values": {
            "invoice_id": "INV-TEST-001",
            "vendor_name": "Test Labs Inc",
            "canonical_vendor_id": "VENDOR_TEST_LABS",
            "invoice_date": "2026-06-01",
            "due_date": "2026-06-15",
            "total_amount": 12500.50,
            "tax_amount": 1500.00,
            "currency": "INR",
            "gstin": "22TESTS1234A1Z1"
        },
        "average_confidence": 0.95,
        "field_metadata": {
            "invoice_id": {"raw_text_source": "Invoice Ref: INV-TEST-001", "raw_value": "INV-TEST-001", "canonical_value": "INV-TEST-001", "confidence": 0.97, "status": "Accepted"},
            "vendor_name": {"raw_text_source": "Supplier: Test Labs Inc", "raw_value": "Test Labs Inc", "canonical_value": "Test Labs Inc", "confidence": 0.92, "status": "Accepted"},
            "invoice_date": {"raw_text_source": "Billing Date: 01/06/2026", "raw_value": "01/06/2026", "canonical_value": "2026-06-01", "confidence": 0.96, "status": "Accepted"},
            "due_date": {"raw_text_source": "Pay before: 15/06/2026", "raw_value": "15/06/2026", "canonical_value": "2026-06-15", "confidence": 0.94, "status": "Accepted"},
            "total_amount": {"raw_text_source": "Grand Total: 12,500.50", "raw_value": "12,500.50", "canonical_value": "12500.5", "confidence": 0.95, "status": "Accepted"},
            "tax_amount": {"raw_text_source": "GST: 1,500.00", "raw_value": "1,500.00", "canonical_value": "1500.0", "confidence": 0.93, "status": "Accepted"},
            "gstin": {"raw_text_source": "GSTIN: 22TESTS1234A1Z1", "raw_value": "22TESTS1234A1Z1", "canonical_value": "22TESTS1234A1Z1", "confidence": 0.98, "status": "Accepted"}
        }
    }
    
    # 1. Save invoice
    print("Saving invoice to test database...")
    record_id = save_invoice(mock_result, duplicate_flag=False, db_path=db_path)
    assert record_id is not None, "Failed to get record ID from save_invoice."
    print(f"Record saved with ID: {record_id}")
    
    # 2. Check duplicate (should find the duplicate now)
    print("Checking duplicate invoice detection...")
    dup, high_dup = check_duplicate_invoice(
        "VENDOR_TEST_LABS", "INV-TEST-001", 12500.50, db_path=db_path
    )
    assert dup is True, "Duplicate check failed to detect matching invoice."
    assert high_dup is True, "Duplicate check failed to detect matching high-risk amount."
    print("Duplicate detection succeeded.")
    
    # 3. Get invoice by ID
    print("Retrieving invoice by ID...")
    record = get_invoice_by_id(record_id, db_path=db_path)
    assert record is not None, "Failed to retrieve saved invoice."
    assert record["invoice_id"] == "INV-TEST-001"
    assert record["status"] == "Pending Review"
    print("Retrieval succeeded.")
    
    # 4. Update invoice (Human Verification mock)
    print("Simulating human verification edit...")
    updated_fields = {
        "invoice_id": "INV-TEST-001-MOD",
        "vendor_name": "TEST LABS INC MODIFIED",
        "canonical_vendor_id": "VENDOR_TEST_LABS_MODIFIED",
        "invoice_date": "2026-06-02",
        "due_date": "2026-06-16",
        "total_amount": 13000.00,
        "tax_amount": 1600.00,
        "currency": "INR",
        "gstin": "22TESTS1234A1Z2"
    }
    update_invoice(record_id, updated_fields, status="Verified", db_path=db_path)
    
    # Verify update
    updated_record = get_invoice_by_id(record_id, db_path=db_path)
    assert updated_record["invoice_id"] == "INV-TEST-001-MOD"
    assert updated_record["status"] == "Verified"
    assert updated_record["total_amount"] == 13000.00
    print("Update (human verification) succeeded.")
    
    # 5. List all invoices
    print("Retrieving all invoices...")
    all_invoices = get_all_invoices(db_path=db_path)
    assert len(all_invoices) == 1
    print("Listing succeeded.")
    
    # 6. Delete invoice
    print("Deleting invoice...")
    delete_invoice(record_id, db_path=db_path)
    deleted_record = get_invoice_by_id(record_id, db_path=db_path)
    assert deleted_record is None, "Invoice deletion failed."
    print("Deletion succeeded.")
    
    # Clean up test DB
    if os.path.exists(db_path):
        os.remove(db_path)
        
    print("\nALL DATABASE AND DUPLICATE DETECTION TESTS PASSED SUCCESSFULLY! [SUCCESS]")

if __name__ == "__main__":
    test_database_operations()
