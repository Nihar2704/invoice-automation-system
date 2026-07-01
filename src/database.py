import sqlite3
import os
import json
from datetime import datetime

DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "processed", "invoices.db"
)

def get_connection(db_path=DEFAULT_DB_PATH):
    """
    Establishes connection to the SQLite database and creates parent directories if needed.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    # Enable dict factory to easily read rows as dictionary objects
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path=DEFAULT_DB_PATH):
    """
    Initializes database tables.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # Create invoices table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_name TEXT NOT NULL,
        invoice_id TEXT,
        vendor_name TEXT,
        canonical_vendor_id TEXT,
        invoice_date TEXT,
        due_date TEXT,
        total_amount REAL,
        tax_amount REAL,
        currency TEXT DEFAULT 'INR',
        gstin TEXT,
        status TEXT DEFAULT 'Pending Review',
        duplicate_flag INTEGER DEFAULT 0,
        average_confidence REAL,
        field_metadata_json TEXT,
        created_at TEXT NOT NULL
    )
    """)
    
    # Index for fast duplicate checks
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_invoice_dup 
    ON invoices(canonical_vendor_id, invoice_id, total_amount)
    """)
    
    conn.commit()
    conn.close()
    print("SQLite Database initialized successfully.")

def save_invoice(result_dict: dict, duplicate_flag: bool, db_path=DEFAULT_DB_PATH) -> int:
    """
    Saves a newly processed invoice dictionary into the database as 'Pending Review'.
    """
    init_db(db_path) # Safe check to ensure table exists
    
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    file_name = result_dict["file_name"]
    vals = result_dict["extracted_values"]
    conf = result_dict["average_confidence"]
    
    # Clean and format field metadata for JSON serialization
    metadata = {}
    for key, val in result_dict["field_metadata"].items():
        metadata[key] = {
            "raw_text_source": val["raw_text_source"],
            "raw_value": val["raw_value"],
            "canonical_value": val["canonical_value"],
            "confidence": val["confidence"],
            "status": val["status"]
        }
        
    metadata_json = json.dumps(metadata)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
    INSERT INTO invoices (
        file_name, invoice_id, vendor_name, canonical_vendor_id,
        invoice_date, due_date, total_amount, tax_amount,
        currency, gstin, status, duplicate_flag,
        average_confidence, field_metadata_json, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending Review', ?, ?, ?, ?)
    """, (
        file_name,
        vals.get("invoice_id"),
        vals.get("vendor_name"),
        vals.get("canonical_vendor_id"),
        vals.get("invoice_date"),
        vals.get("due_date"),
        vals.get("total_amount"),
        vals.get("tax_amount"),
        vals.get("currency", "INR"),
        vals.get("gstin"),
        1 if duplicate_flag else 0,
        conf,
        metadata_json,
        created_at
    ))
    
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id

def update_invoice(record_id: int, updated_fields: dict, status: str = "Verified", db_path=DEFAULT_DB_PATH):
    """
    Updates invoice fields and changes the status (typically to 'Verified').
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # Update main table columns
    cursor.execute("""
    UPDATE invoices SET
        invoice_id = ?,
        vendor_name = ?,
        canonical_vendor_id = ?,
        invoice_date = ?,
        due_date = ?,
        total_amount = ?,
        tax_amount = ?,
        currency = ?,
        gstin = ?,
        status = ?
    WHERE id = ?
    """, (
        updated_fields.get("invoice_id"),
        updated_fields.get("vendor_name"),
        updated_fields.get("canonical_vendor_id"),
        updated_fields.get("invoice_date"),
        updated_fields.get("due_date"),
        updated_fields.get("total_amount"),
        updated_fields.get("tax_amount"),
        updated_fields.get("currency"),
        updated_fields.get("gstin"),
        status,
        record_id
    ))
    
    conn.commit()
    conn.close()

def get_all_invoices(db_path=DEFAULT_DB_PATH) -> list:
    """
    Retrieves all invoice records sorted by creation time (descending).
    """
    init_db(db_path)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM invoices ORDER BY id DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_invoice_by_id(record_id: int, db_path=DEFAULT_DB_PATH) -> dict:
    """
    Retrieves a single invoice record by its ID.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM invoices WHERE id = ?", (record_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_invoice(record_id: int, db_path=DEFAULT_DB_PATH):
    """
    Deletes an invoice record.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM invoices WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
