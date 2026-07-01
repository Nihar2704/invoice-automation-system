import sqlite3
import os
from database import get_connection, DEFAULT_DB_PATH

def check_duplicate_invoice(canonical_vendor_id: str, invoice_id: str, total_amount: float, current_record_id: int = None, db_path=DEFAULT_DB_PATH) -> tuple:
    """
    Checks the SQLite database for duplicate invoice submissions.
    Returns: (is_duplicate, is_high_risk)
    - is_duplicate: True if there is an invoice with the same Vendor ID and Invoice ID.
    - is_high_risk: True if the Vendor ID, Invoice ID, and Total Amount all match exactly.
    """
    if not canonical_vendor_id or not invoice_id:
        return False, False
        
    # Ensure database path exists
    if not os.path.exists(db_path):
        return False, False
        
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # Fetch existing invoices matching the same vendor ID and invoice ID.
    # If checking during editing, exclude the current record ID from the search.
    if current_record_id is not None:
        cursor.execute("""
            SELECT id, total_amount FROM invoices 
            WHERE canonical_vendor_id = ? AND invoice_id = ? AND id != ?
        """, (canonical_vendor_id, invoice_id, current_record_id))
    else:
        cursor.execute("""
            SELECT id, total_amount FROM invoices 
            WHERE canonical_vendor_id = ? AND invoice_id = ?
        """, (canonical_vendor_id, invoice_id))
        
    matches = cursor.fetchall()
    conn.close()
    
    if not matches:
        return False, False
        
    # Vendor and Invoice ID match means it's a duplicate check warning
    is_duplicate = True
    is_high_risk = False
    
    # Check if any matching record shares the exact same total amount
    for match in matches:
        match_amount = match["total_amount"]
        if match_amount is not None and total_amount is not None:
            # Check for float equality with epsilon tolerance
            if abs(float(match_amount) - float(total_amount)) < 0.01:
                is_high_risk = True
                break
                
    return is_duplicate, is_high_risk
