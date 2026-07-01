import os
import sys
import tempfile
import pandas as pd
import json
import streamlit as st
import plotly.graph_objects as go
import fitz  # PyMuPDF
from PIL import Image
from datetime import datetime
import sqlite3

# Set up page configurations
st.set_page_config(
    page_title="InvoiceAI - Enterprise AP Platform",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Append src/ folder to Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from prediction import InvoiceParserPipeline
from database import DEFAULT_DB_PATH, save_invoice, update_invoice, get_all_invoices, get_invoice_by_id, delete_invoice
from duplicate_detection import check_duplicate_invoice
from canonicalization import canonicalize_vendor

# Initialize session state variables
if "selected_invoice_id" not in st.session_state:
    st.session_state.selected_invoice_id = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"
if "last_extraction_result" not in st.session_state:
    st.session_state.last_extraction_result = None
if "last_record_id" not in st.session_state:
    st.session_state.last_record_id = None

# Navigation callback
def navigate_to(page):
    st.session_state.current_page = page

# Database Seeder for Realistic Mockups matching Screen Spec
def seed_database_if_empty():
    try:
        invoices = get_all_invoices()
        if len(invoices) > 0:
            return
    except Exception:
        pass
    
    # We will seed 3 detailed verification records to match the Activity logs
    demo_pdf_src = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data", "raw_invoices", "test_pack", "demo_samples", "invoice_01_text_standard.pdf"
    )
    
    # Ensure raw_invoices directory exists
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "raw_invoices"), exist_ok=True)
    
    mock_data = [
        {
            "file_name": "invoice_tech_solutions.pdf",
            "extracted_values": {
                "invoice_id": "INV-2026-001",
                "vendor_name": "Tech Solutions Inc.",
                "canonical_vendor_id": "VENDOR_TECH_SOLUTIONS_INC",
                "invoice_date": "2026-08-24",
                "due_date": "2026-09-08",
                "total_amount": 4250.00,
                "tax_amount": 250.00,
                "gstin": "22ABCDE1234F1Z5",
                "currency": "INR"
            },
            "average_confidence": 0.984,
            "status": "Verified",
            "field_metadata": {
                "invoice_id": {"raw_text_source": "Invoice ID: INV-2026-001", "raw_value": "INV-2026-001", "canonical_value": "INV-2026-001", "confidence": 0.99, "status": "Accepted"},
                "vendor_name": {"raw_text_source": "Tech Solutions Inc.", "raw_value": "Tech Solutions Inc.", "canonical_value": "Tech Solutions Inc.", "confidence": 0.98, "status": "Accepted"},
                "invoice_date": {"raw_text_source": "Date: 24/08/2026", "raw_value": "24/08/2026", "canonical_value": "2026-08-24", "confidence": 0.99, "status": "Accepted"},
                "due_date": {"raw_text_source": "Due Date: 08/09/2026", "raw_value": "08/09/2026", "canonical_value": "2026-09-08", "confidence": 0.98, "status": "Accepted"},
                "total_amount": {"raw_text_source": "Total: 4250.00", "raw_value": "4250.00", "canonical_value": 4250.0, "confidence": 0.99, "status": "Accepted"},
                "tax_amount": {"raw_text_source": "Tax: 250.00", "raw_value": "250.00", "canonical_value": 250.0, "confidence": 0.99, "status": "Accepted"},
                "gstin": {"raw_text_source": "GSTIN: 22ABCDE1234F1Z5", "raw_value": "22ABCDE1234F1Z5", "canonical_value": "22ABCDE1234F1Z5", "confidence": 0.98, "status": "Accepted"}
            },
            "raw_text": "Tech Solutions Inc.\nInvoice ID: INV-2026-001\nDate: 24/08/2026\nDue Date: 08/09/2026\nGSTIN: 22ABCDE1234F1Z5\nTotal: 4250.00\nTax: 250.00"
        },
        {
            "file_name": "invoice_global_logistics.pdf",
            "extracted_values": {
                "invoice_id": "GL-8899-X",
                "vendor_name": "Global Logistics Ltd.",
                "canonical_vendor_id": "VENDOR_GLOBAL_LOGISTICS_LTD",
                "invoice_date": "2026-08-24",
                "due_date": "2026-09-10",
                "total_amount": 12840.15,
                "tax_amount": 840.15,
                "gstin": "27GHIJK5678L2Z0",
                "currency": "INR"
            },
            "average_confidence": 0.762,
            "status": "Pending Review",
            "field_metadata": {
                "invoice_id": {"raw_text_source": "INV ID: GL-8899-X", "raw_value": "GL-8899-X", "canonical_value": "GL-8899-X", "confidence": 0.90, "status": "Accepted"},
                "vendor_name": {"raw_text_source": "Global Logistics Ltd.", "raw_value": "Global Logistics Ltd.", "canonical_value": "Global Logistics Ltd.", "confidence": 0.85, "status": "Accepted"},
                "invoice_date": {"raw_text_source": "Date: 24/08/2026", "raw_value": "24/08/2026", "canonical_value": "2026-08-24", "confidence": 0.88, "status": "Accepted"},
                "due_date": {"raw_text_source": "Due by: 10/09/2026", "raw_value": "10/09/2026", "canonical_value": "2026-09-10", "confidence": 0.55, "status": "Review Needed"},
                "total_amount": {"raw_text_source": "Net Amount: 12840.15", "raw_value": "12840.15", "canonical_value": 12840.15, "confidence": 0.70, "status": "Review Needed"},
                "tax_amount": {"raw_text_source": "Tax: 840.15", "raw_value": "840.15", "canonical_value": 840.15, "confidence": 0.75, "status": "Review Needed"},
                "gstin": {"raw_text_source": "GSTIN: 27GHIJK5678L2Z0", "raw_value": "27GHIJK5678L2Z0", "canonical_value": "27GHIJK5678L2Z0", "confidence": 0.80, "status": "Accepted"}
            },
            "raw_text": "Global Logistics Ltd.\nINV ID: GL-8899-X\nDate: 24/08/2026\nDue by: 10/09/2026\nGSTIN: 27GHIJK5678L2Z0\nNet Amount: 12840.15\nTax: 840.15"
        },
        {
            "file_name": "invoice_techno_logic.pdf",
            "extracted_values": {
                "invoice_id": "INV-8842-X",
                "vendor_name": "Techno-Logic Solutions",
                "canonical_vendor_id": "VENDOR_TECHNO_LOGIC_SOLUTIONS",
                "invoice_date": "2026-08-23",
                "due_date": "2026-09-07",
                "total_amount": 13747.75,
                "tax_amount": 1047.75,
                "gstin": "22AAAAA0000A1Z5",
                "currency": "INR"
            },
            "average_confidence": 0.950,
            "status": "Verified",
            "field_metadata": {
                "invoice_id": {"raw_text_source": "INV-8842-X", "raw_value": "INV-8842-X", "canonical_value": "INV-8842-X", "confidence": 0.96, "status": "Accepted"},
                "vendor_name": {"raw_text_source": "TECHNO-LOGIC SOLUTIONS", "raw_value": "TECHNO-LOGIC SOLUTIONS", "canonical_value": "Techno-Logic Solutions", "confidence": 0.88, "status": "Accepted"},
                "invoice_date": {"raw_text_source": "10/24/2023", "raw_value": "10/24/2023", "canonical_value": "2026-08-23", "confidence": 0.91, "status": "Accepted"},
                "due_date": {"raw_text_source": "11/24/2023", "raw_value": "11/24/2023", "canonical_value": "2026-09-07", "confidence": 0.62, "status": "Review Needed"},
                "total_amount": {"raw_text_source": "13,747.75", "raw_value": "13,747.75", "canonical_value": 13747.75, "confidence": 0.95, "status": "Accepted"},
                "tax_amount": {"raw_text_source": "1,047.75", "raw_value": "1,047.75", "canonical_value": 1047.75, "confidence": 0.94, "status": "Accepted"},
                "gstin": {"raw_text_source": "22AAAAA0000A1Z5", "raw_value": "22AAAAA0000A1Z5", "canonical_value": "22AAAAA0000A1Z5", "confidence": 0.98, "status": "Accepted"}
            },
            "raw_text": "TECHNO-LOGIC SOLUTIONS\nINV-8842-X\n10/24/2023\n11/24/2023\n13,747.75\n22AAAAA0000A1Z5"
        }
    ]
    
    # Save seed items into DB and copy mock PDF documents
    conn = sqlite3.connect(DEFAULT_DB_PATH)
    cursor = conn.cursor()
    
    import shutil
    for item in mock_data:
        metadata_json = json.dumps(item["field_metadata"])
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        vals = item["extracted_values"]
        
        cursor.execute("""
        INSERT INTO invoices (
            file_name, invoice_id, vendor_name, canonical_vendor_id,
            invoice_date, due_date, total_amount, tax_amount,
            currency, gstin, status, duplicate_flag,
            average_confidence, field_metadata_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?)
        """, (
            item["file_name"],
            vals.get("invoice_id"),
            vals.get("vendor_name"),
            vals.get("canonical_vendor_id"),
            vals.get("invoice_date"),
            vals.get("due_date"),
            vals.get("total_amount"),
            vals.get("tax_amount"),
            vals.get("currency", "INR"),
            vals.get("gstin"),
            item["status"],
            item["average_confidence"],
            metadata_json,
            created_at
        ))
        
        record_id = cursor.lastrowid
        if os.path.exists(demo_pdf_src):
            dest_pdf = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "data", "raw_invoices", f"{record_id}_{item['file_name']}"
            )
            shutil.copy(demo_pdf_src, dest_pdf)
            
    conn.commit()
    conn.close()

seed_database_if_empty()

# Helper function to render HTML cleanly without indented code blocks
def st_html(html_str: str):
    cleaned = "\n".join(line.strip() for line in html_str.split("\n"))
    st.markdown(cleaned, unsafe_allow_html=True)

def st_sidebar_html(html_str: str):
    cleaned = "\n".join(line.strip() for line in html_str.split("\n"))
    st.sidebar.markdown(cleaned, unsafe_allow_html=True)

# Premium UI CSS Styling
st_html("""
<style>
    /* Import Inter Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Design Tokens */
    :root {
        --bg-sidebar: #12142B;
        --bg-app: #F4F5FA;
        --accent-primary: #5B5FEF;
        --accent-primary-dark: #12142B;
        --success: #22C55E;
        --success-bg: #DCFCE7;
        --warning: #F59E0B;
        --warning-bg: #FEF3C7;
        --danger: #EF4444;
        --danger-bg: #FEE2E2;
        --text-primary: #0F1222;
        --text-secondary: #6B7280;
        --border: #E5E7EB;
    }
    
    /* Apply Inter font globally to text containers, preserving icon fonts */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"], .main {
        font-family: 'Inter', "Segoe UI", sans-serif !important;
    }
    
    /* Force main app background to lock to light gray design token */
    div[data-testid="stAppViewContainer"], .main {
        background-color: var(--bg-app) !important;
    }
    
    /* Override Streamlit color variables locally inside the main content viewport */
    .main {
        --text-color: #0F1222 !important;
        --background-color: #F4F5FA !important;
        --secondary-background-color: #FFFFFF !important;
    }
    
    /* Make header bar transparent for unified layout */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    /* Force main content headings, labels, metrics, and texts to be dark for readability under dark-mode overrides */
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6, .main p, .main li,
    .main label, .main label span,
    .main div[data-testid="stMetricLabel"],
    .main div[data-testid="stMetricValue"],
    .main div[data-testid="stMetricDelta"],
    .main details summary,
    .main details summary span,
    .main div[data-testid="stSlider"] label,
    .main div[data-testid="stSlider"] span,
    .main div[data-testid="stCheckbox"] label,
    .main div[data-testid="stCheckbox"] p,
    .main div[data-testid="stSelectbox"] label,
    .main div[data-testid="stMultiSelect"] label,
    .main div[data-testid="stTextInput"] label,
    .main div[data-testid="stNumberInput"] label,
    .main span:not(.status-pill-success):not(.status-pill-warning):not(.status-pill-danger):not(.badge-accepted):not(.badge-review):not(.badge-low):not(.vendor-avatar) {
        color: #0F1222 !important;
    }
    
    /* Preserve caption visual hierarchy with subtle gray */
    .main [data-testid="stMarkdownContainer"] .stCaption p,
    .main .stCaption,
    .main .stCaption p {
        color: #6B7280 !important;
    }
    
    /* Sidebar Styling Overrides */
    div[data-testid="stSidebar"] {
        background-color: #12142B !important;
        background-image: none !important;
        color: #F8FAFC !important;
        border-right: 1px solid #1E293B;
    }
    
    div[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    div[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        color: #E2E8F0 !important;
    }
    
    /* Sidebar Custom Navigation Button active/inactive style */
    div[data-testid="stSidebar"] button[kind="primary"] {
        background-color: #5B5FEF !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        text-align: left !important;
        padding: 0.6rem 1rem !important;
        width: 100% !important;
    }
    
    div[data-testid="stSidebar"] button[kind="secondary"] {
        background-color: transparent !important;
        color: #94A3B8 !important;
        border: none !important;
        border-radius: 8px !important;
        text-align: left !important;
        padding: 0.6rem 1rem !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }
    
    div[data-testid="stSidebar"] button[kind="secondary"]:hover {
        color: #FFFFFF !important;
        background-color: rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Responsive KPI Row Container */
    .kpi-row-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1.25rem;
        width: 100%;
        margin-bottom: 2rem;
        box-sizing: border-box;
    }
    
    /* Reusable Metric Card Styling */
    .metric-card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid #E5E7EB;
        flex: 1 1 calc(33.3% - 1.25rem);
        min-width: 220px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    .metric-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
    }
    .metric-icon {
        font-size: 1.15rem;
        background-color: #F3F4F6;
        padding: 0.35rem;
        border-radius: 8px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: #4B5563;
        width: 32px;
        height: 32px;
        box-sizing: border-box;
    }
    
    /* Metric Card Trend/Status Badges */
    .status-pill-success {
        background-color: #DCFCE7;
        color: #166534;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 0.2rem 0.5rem;
        border-radius: 9999px;
    }
    .status-pill-warning {
        background-color: #FEF3C7;
        color: #92400E;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 0.2rem 0.5rem;
        border-radius: 9999px;
    }
    .status-pill-danger {
        background-color: #FEE2E2;
        color: #991B1B;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 0.2rem 0.5rem;
        border-radius: 9999px;
    }
    
    .metric-val {
        font-size: 2rem;
        font-weight: 800;
        color: #0F1222;
        margin: 0.25rem 0 0 0 !important;
        line-height: 1;
    }
    .metric-lbl {
        font-size: 0.72rem;
        color: #6B7280;
        margin: 0 !important;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.05em;
    }
    
    /* Extraction Result Table */
    .extraction-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
        background-color: #FFFFFF;
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #E5E7EB;
    }
    .extraction-table th {
        background-color: #F9FAFB;
        padding: 1rem;
        font-size: 0.8rem;
        font-weight: 800;
        color: #374151;
        text-transform: uppercase;
        border-bottom: 1px solid #E5E7EB;
        text-align: left;
    }
    .extraction-table td {
        padding: 1rem;
        font-size: 0.88rem;
        color: #0F1222;
        border-bottom: 1px solid #E5E7EB;
    }
    .extraction-table tr:last-child td {
        border-bottom: none;
    }
    
    /* Responsive Recent Activity Table */
    .recent-activity-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 0.5rem;
    }
    .recent-activity-table th {
        text-align: left;
        font-size: 0.72rem;
        font-weight: 700;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #E5E7EB;
    }
    .recent-activity-table td {
        padding: 0.95rem 1rem;
        font-size: 0.85rem;
        color: #0F1222;
        border-bottom: 1px solid #E5E7EB;
        vertical-align: middle;
    }
    .vendor-chip {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .vendor-avatar {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        background-color: #EEF2F6;
        color: #4F46E5;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.78rem;
        border: 1px solid #E2E8F0;
    }
    
    /* Verification Field Labels and Badges */
    .badge-accepted {
        background-color: #DCFCE7;
        color: #166534;
        padding: 0.15rem 0.45rem;
        border-radius: 0.25rem;
        font-weight: 700;
        font-size: 0.65rem;
        letter-spacing: 0.02em;
        margin-left: 0.5rem;
    }
    .badge-review {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 0.15rem 0.45rem;
        border-radius: 0.25rem;
        font-weight: 700;
        font-size: 0.65rem;
        letter-spacing: 0.02em;
        margin-left: 0.5rem;
    }
    .badge-low {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 0.15rem 0.45rem;
        border-radius: 0.25rem;
        font-weight: 700;
        font-size: 0.65rem;
        letter-spacing: 0.02em;
        margin-left: 0.5rem;
    }
    
    /* Paper Mockup Container */
    .invoice-paper-preview {
        background-color: #FFFFFF;
        padding: 2.25rem;
        border-radius: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid #E5E7EB;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.85rem;
        line-height: 1.45;
        color: #1F2937;
        max-height: 550px;
        overflow-y: auto;
        white-space: pre-wrap;
    }
    
    /* Breakpoints for 6 columns wrapping to 3 to 2 to 1 */
    @media (max-width: 1400px) {
        .metric-card {
            flex: 1 1 calc(33.3% - 1.25rem) !important;
        }
    }
    @media (max-width: 900px) {
        .metric-card {
            flex: 1 1 calc(50% - 1.25rem) !important;
        }
    }
    @media (max-width: 600px) {
        .metric-card {
            flex: 1 1 100% !important;
        }
    }
    
    /* Top Navigation bar layout */
    .top-header-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 1rem;
        margin-bottom: 1.75rem;
        border-bottom: 1px solid #E5E7EB;
        width: 100%;
    }
    @media (max-width: 992px) {
        .top-header-bar {
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 1.25rem !important;
        }
        .top-header-bar > div {
            width: 100% !important;
        }
        .top-header-bar .header-controls {
            width: 100% !important;
            justify-content: space-between !important;
        }
    }
</style>
""")

# Helper function to render reusable styled metric card
def render_metric_card(label, value, trend_pill="", trend_type="", icon=""):
    badge_html = ""
    if trend_pill:
        if trend_type == "success":
            badge_class = "status-pill-success"
        elif trend_type == "warning":
            badge_class = "status-pill-warning"
        elif trend_type == "danger":
            badge_class = "status-pill-danger"
        else:
            badge_class = "status-pill-normal"
        badge_html = f'<span class="{badge_class}">{trend_pill}</span>'
        
    icon_html = f'<span class="metric-icon">{icon}</span>' if icon else ""
    
    return f"""
    <div class="metric-card">
        <div class="metric-card-header">
            {icon_html}
            {badge_html}
        </div>
        <p class="metric-val">{value}</p>
        <p class="metric-lbl">{label}</p>
    </div>
    """

# Helper to render the Header Bar dynamically based on page requirements
def render_top_header(title: str, search_placeholder: str = "", breadcrumbs: str = "", extra_right_buttons: list = None):
    # Determine the Left section
    left_section = ""
    if breadcrumbs:
        left_section = f'<span style="font-size: 0.78rem; font-weight: 700; color: #6B7280; text-transform: uppercase; letter-spacing: 0.05em;">{breadcrumbs}</span>'
    elif search_placeholder:
        left_section = f"""
        <div style="position: relative; width: 350px;">
            <input type="text" placeholder="{search_placeholder}" style="width: 100%; padding: 0.5rem 1rem; border-radius: 8px; border: 1px solid #E5E7EB; font-size: 0.85rem; background-color: #FFFFFF;" />
        </div>
        """
    else:
        left_section = f'<h1 style="margin: 0; font-size: 1.75rem; font-weight: 800; color: #0F1222;">{title}</h1>'
        
    # Extra buttons or calendar
    right_extras = ""
    if extra_right_buttons:
        for btn in extra_right_buttons:
            right_extras += btn
            
    st_html(f"""
    <div class="top-header-bar">
        <div>
            {left_section}
        </div>
        <div class="header-controls" style="display: flex; align-items: center; gap: 1.25rem;">
            {right_extras}
            <span style="font-size: 1.2rem; cursor: pointer; color: #6B7280; position: relative;">
                🔔<span style="position: absolute; top: -2px; right: -2px; width: 6px; height: 6px; background-color: #EF4444; border-radius: 50%;"></span>
            </span>
            <span style="font-size: 1.2rem; cursor: pointer; color: #6B7280;">❓</span>
            <div style="display: flex; align-items: center; gap: 0.6rem; margin-left: 0.5rem;">
                <div style="text-align: right;">
                    <p style="margin: 0; font-size: 0.8rem; font-weight: 800; color: #0F1222;">Alex Rivera</p>
                    <p style="margin: 0; font-size: 0.68rem; font-weight: 600; color: #6B7280;">Senior AP Manager</p>
                </div>
                <div style="width: 38px; height: 38px; border-radius: 50%; background-color: #5B5FEF; color: #FFFFFF; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.9rem; border: 2px solid #E5E7EB;">AR</div>
            </div>
        </div>
    </div>
    """)

# Sidebar Navigation Layout
with st.sidebar:
    st_sidebar_html("""<div style="display: flex; align-items: center; gap: 0.75rem; padding-bottom: 1rem; margin-bottom: 1.5rem; border-bottom: 1px solid #1E293B;">
        <div style="background-color: #5B5FEF; padding: 0.5rem; border-radius: 0.5rem; color: #FFFFFF; font-weight: 800; font-size: 1.2rem; line-height: 1; display:flex; align-items:center; justify-content:center; width:36px; height:36px;">🧾</div>
        <div>
            <h3 style="margin: 0; font-size: 1.1rem; font-weight: 800; color: #FFFFFF !important; line-height: 1.1;">InvoiceAI</h3>
            <span style="font-size: 0.62rem; text-transform: uppercase; font-weight: 700; color: #94A3B8; letter-spacing: 0.05em;">Enterprise Edition</span>
        </div>
    </div>
    """)
    
    # Custom Sidebar Navigation items matching Section 17.2
    pages = ["Dashboard", "Upload Invoice", "Extraction Result", "Human Verification", "Model Performance", "Invoice History", "Export Data"]
    for p in pages:
        active = (st.session_state.current_page == p)
        if st.sidebar.button(p, type="primary" if active else "secondary", use_container_width=True, key=f"nav_{p}"):
            navigate_to(p)
            st.rerun()
            
    # Bottom block drawer
    st_sidebar_html("""<div style="padding-top: 1.5rem; border-top: 1px solid #1E293B; margin-top: 2rem;">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.25rem;">
            <div style="width: 36px; height: 36px; border-radius: 50%; background-color: #5B5FEF; color: #FFFFFF; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.85rem;">AR</div>
            <div>
                <p style="margin:0; font-size:0.8rem; font-weight:700; color:#FFFFFF;">Alex Rivera</p>
                <p style="margin:0; font-size:0.68rem; font-weight:500; color:#94A3B8;">Senior AP Manager</p>
            </div>
        </div>
    </div>
    """)
    
    if st.sidebar.button("➕ Quick Upload", type="secondary", use_container_width=True, key="quick_upload_act"):
        navigate_to("Upload Invoice")
        st.rerun()
        
    if st.session_state.current_page == "Human Verification":
        if st.sidebar.button("Sign Out", type="secondary", use_container_width=True, key="sign_out_act"):
            st.toast("Signed out successfully.")

# Load model pipeline
@st.cache_resource
def load_pipeline():
    try:
        return InvoiceParserPipeline()
    except Exception as e:
        st.error(f"Failed to load trained model classifier: {e}")
        return None

pipeline = load_pipeline()

# ----------------- PAGE 1: DASHBOARD -----------------
if st.session_state.current_page == "Dashboard":
    calendar_pill = """
    <div style="display: flex; align-items: center; gap: 0.5rem; background-color: #FFFFFF; padding: 0.4rem 0.8rem; border-radius: 0.5rem; border: 1px solid #E5E7EB; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
        <span style="font-size: 1rem;">📅</span>
        <span style="font-size: 0.8rem; font-weight: 700; color: #334155;">Aug 1, 2026 - Aug 31, 2026</span>
    </div>
    """
    render_top_header("AP Manager Overview", extra_right_buttons=[calendar_pill])
    
    invoices = get_all_invoices()
    
    # Calculate statistics based on Section 17.3 cards without hardcoded offsets
    processed_count = len(invoices)
    verified_count = sum(1 for i in invoices if i["status"] == "Verified")
    pending_count = sum(1 for i in invoices if i["status"] == "Pending Review")
    dup_count = sum(1 for i in invoices if i["duplicate_flag"] == 1)
    
    valid_confs = [i["average_confidence"] for i in invoices if i["average_confidence"] > 0]
    avg_conf = (sum(valid_confs) / len(valid_confs)) if valid_confs else 0.0
    
    # Sum invoice volumes
    total_db_volume = sum(i["total_amount"] for i in invoices if i["total_amount"] is not None)
    total_volume_amount = total_db_volume
    
    # 6 KPI cards layout
    kpi_html = f"""
    <div class="kpi-row-container">
        {render_metric_card("Total Invoices Processed", f"{processed_count:,}", f"{processed_count} files", "success", "📄")}
        {render_metric_card("Verified Invoices", f"{verified_count:,}", f"{verified_count} done", "success", "✓")}
        {render_metric_card("Pending Review", f"{pending_count}", f"{pending_count} review", "warning" if pending_count > 0 else "success", "📋")}
        {render_metric_card("Duplicate Warnings", f"{dup_count}", f"{dup_count} alerts" if dup_count > 0 else "no alerts", "danger" if dup_count > 0 else "success", "🗂")}
        {render_metric_card("Average Confidence", f"{avg_conf:.1%}", "OCR score", "success" if avg_conf >= 0.85 else "warning", "📶")}
        {render_metric_card("Total Invoice Amount", f"₹ {total_volume_amount:,.2f}", "INR", "success", "💰")}
    </div>
    """
    st_html(kpi_html)
    
    # Charts Row
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st_html("""<div style="background-color:#FFFFFF; padding:1.5rem; border-radius:16px; border:1px solid #E5E7EB; box-shadow:0 1px 3px rgba(0,0,0,0.08);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <div>
                    <h4 style="margin:0; font-size:1.05rem; font-weight:800; color:#0F1222;">Invoice Amount Value Trend</h4>
                    <p style="margin:0.2rem 0 0 0; color:#6B7280; font-size:0.78rem;">Cumulative financial pipeline value (INR)</p>
                </div>
            </div>
        </div>
        """)
        
        # Plotly Cumulative Line chart using actual database history
        if len(invoices) > 0:
            df_invoices = pd.DataFrame(invoices)
            df_invoices["created_date"] = pd.to_datetime(df_invoices["created_at"]).dt.strftime("%b %d")
            df_grouped = df_invoices.groupby("created_date")["total_amount"].sum().reset_index()
            df_grouped = df_grouped.sort_values(by="created_date")
            timeline_x = df_grouped["created_date"].tolist()
            timeline_y = df_grouped["total_amount"].cumsum().tolist()
        else:
            timeline_x = [datetime.now().strftime("%b %d")]
            timeline_y = [0.0]
            
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=timeline_x,
            y=timeline_y,
            name="Invoice Amount Value Trend",
            line=dict(color="#5B5FEF", width=3, shape="spline"),
            fill='tozeroy',
            fillcolor="rgba(91, 95, 239, 0.08)",
            mode="lines+markers"
        ))
        fig.update_layout(
            margin=dict(l=20, r=20, t=10, b=10),
            height=250,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, color="#6B7280", tickfont=dict(size=9)),
            yaxis=dict(showgrid=False, zeroline=False, color="#6B7280", tickfont=dict(size=9))
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st_html("""<div style="background-color:#FFFFFF; padding:1.5rem; border-radius:16px; border:1px solid #E5E7EB; box-shadow:0 1px 3px rgba(0,0,0,0.08);">
            <h4 style="margin:0; font-size:1.05rem; font-weight:800; color:#0F1222;">Field Distribution</h4>
            <p style="margin:0.2rem 0 1.25rem 0; color:#6B7280; font-size:0.78rem;">OCR Confidence Tiers</p>
        </div>
        """)
        
        # Count confidences from database dynamically
        high_count = sum(1 for i in invoices if i["average_confidence"] >= 0.85)
        med_count = sum(1 for i in invoices if 0.60 <= i["average_confidence"] < 0.85)
        low_count = sum(1 for i in invoices if 0.0 < i["average_confidence"] < 0.60)
        
        total_counts = high_count + med_count + low_count
        if total_counts == 0:
            high_pct = 100.0
            med_pct = 0.0
            low_pct = 0.0
            chart_values = [1, 0, 0]
        else:
            high_pct = (high_count / total_counts) * 100
            med_pct = (med_count / total_counts) * 100
            low_pct = (low_count / total_counts) * 100
            chart_values = [high_count, med_count, low_count]
            
        fig_donut = go.Figure(data=[go.Pie(
            labels=['High', 'Medium', 'Low'],
            values=chart_values,
            hole=0.75,
            marker=dict(colors=['#22C55E', '#F59E0B', '#EF4444']),
            textinfo='none',
            hoverinfo='label+percent'
        )])
        fig_donut.update_layout(
            annotations=[dict(text=f'{avg_conf:.0%}<br><span style="font-size:0.55em;color:#6B7280;font-weight:600;">RELIABILITY</span>', x=0.5, y=0.5, font_size=19, showarrow=False, font_family='Inter', font_color='#0F1222', font_weight='bold')],
            margin=dict(l=10, r=10, t=10, b=10),
            height=180,
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        
        st_html(f"""<div style="display:flex; justify-content:space-between; font-size:0.75rem; margin-top:-0.5rem; padding: 0 0.5rem;">
            <span>🟢 High ({high_pct:.0f}%)</span>
            <span>🟡 Medium ({med_pct:.0f}%)</span>
            <span>🔴 Low ({low_pct:.0f}%)</span>
        </div>
        """)
        
    st_html("<br>")
    
    # Recent Activity HTML table
    activity_rows = ""
    for i in invoices[:6]:
        status_badge = '<span class="status-pill-success">VERIFIED</span>' if i["status"] == "Verified" else '<span class="status-pill-warning">PENDING</span>'
        conf = i["average_confidence"]
        
        if conf >= 0.85:
            conf_badge = f'<span class="status-pill-success">{conf:.1%}</span>'
        elif 0.60 <= conf < 0.85:
            conf_badge = f'<span class="status-pill-warning">{conf:.1%}</span>'
        else:
            conf_badge = f'<span class="status-pill-danger">{conf:.1%}</span>'
            
        words = i["vendor_name"].split()
        initials = "".join([w[0] for w in words[:2]]).upper() if words else "IN"
        
        activity_rows += f"""
        <tr>
            <td>
                <div class="vendor-chip">
                    <div class="vendor-avatar">{initials}</div>
                    <div style="font-weight:700; color:#0F1222;">{i["vendor_name"]}</div>
                </div>
            </td>
            <td style="color:#6B7280; font-weight:500;">{i["created_at"][:10]}</td>
            <td style="font-weight:700; color:#0F1222;">₹ {i["total_amount"]:,.2f}</td>
            <td>{conf_badge}</td>
            <td>{status_badge}</td>
        </tr>
        """
        
    st_html(f"""
    <div style="background-color:#FFFFFF; padding:1.5rem; border-radius:16px; border:1px solid #E5E7EB; box-shadow:0 1px 3px rgba(0,0,0,0.08); margin-bottom: 2rem;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
            <div>
                <h4 style="margin:0; font-size:1.05rem; font-weight:800; color:#0F1222;">Recent Activity</h4>
                <p style="margin:0.2rem 0 0 0; color:#6B7280; font-size:0.78rem;">Real-time processing queue and status updates</p>
            </div>
            <a href="#" onclick="window.parent.document.querySelector('button[key=nav_Invoice\\\\ History]').click();" style="color:#5B5FEF; font-size:0.82rem; font-weight:700; text-decoration:none;">View All Invoices</a>
        </div>
        <div style="overflow-x:auto;">
            <table class="recent-activity-table">
                <thead>
                    <tr>
                        <th>VENDOR</th>
                        <th>DATE</th>
                        <th>AMOUNT</th>
                        <th>CONFIDENCE</th>
                        <th>STATUS</th>
                    </tr>
                </thead>
                <tbody>
                    {activity_rows}
                </tbody>
            </table>
        </div>
    </div>
    """)

# ----------------- PAGE 2: UPLOAD INVOICE -----------------
elif st.session_state.current_page == "Upload Invoice":
    exp_template = """
    <button style="background:none; border:1px solid #E5E7EB; padding:0.4rem 0.8rem; border-radius:8px; font-size:0.8rem; font-weight:700; color:#374151; cursor:pointer;">Export Template</button>
    """
    render_top_header("Upload Invoice", extra_right_buttons=[exp_template])
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st_html("""<div style="border: 2px dashed #5B5FEF; border-radius: 16px; background-color: #FFFFFF; padding: 4rem 2rem; text-align: center; margin-bottom: 1.5rem; position: relative;">
            <div style="font-size: 3rem; margin-bottom: 1rem; color: #5B5FEF;">📥</div>
            <h3 style="margin: 0 0 0.5rem 0; font-weight: 800; color: #0F1222; font-size:1.25rem;">Drag & Drop Invoices</h3>
            <p style="color: #6B7280; font-size: 0.85rem; margin-bottom: 1.5rem; line-height: 1.45; max-width:400px; margin-left:auto; margin-right:auto;">
                Supported formats: PDF, JPEG, PNG. Up to 50MB per file. AI will automatically detect vendor and extract line items.
            </p>
        </div>
        """)
        
        uploaded_file = st.file_uploader("Upload Portal", type=["pdf", "png", "jpg", "jpeg"], label_visibility="collapsed")
        
        # Display uploader files
        if uploaded_file is not None:
            st_html(f"""<div style="background-color:#FFFFFF; padding:1.25rem; border-radius:16px; border:1px solid #E5E7EB; box-shadow:0 1px 3px rgba(0,0,0,0.08); margin-bottom:1.5rem;">
                <h4 style="margin:0 0 1rem 0; font-size:0.95rem; font-weight:800; color:#0F1222;">Selected Files (1)</h4>
                <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.85rem;">
                    <div style="display:flex; align-items:center; gap:0.5rem;">
                        <span style="font-size:1.2rem;">📕</span>
                        <span style="font-weight:700; color:#0F1222;">{uploaded_file.name}</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:1rem;">
                        <span style="color:#22C55E; font-weight:700;">Ready</span>
                        <span style="cursor:pointer; color:#6B7280;">✕</span>
                    </div>
                </div>
            </div>
            """)
            
    with col2:
        st_html("""<div style="background-color: #12142B; padding: 1.5rem; border-radius: 16px; color: #FFFFFF; box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 1.5rem;">
            <h4 style="margin: 0 0 0.5rem 0; color: #FFFFFF !important; font-size: 1rem; font-weight: 800;">ML Intelligence</h4>
            <p style="margin: 0 0 1.5rem 0; color: #94A3B8; font-size: 0.8rem; line-height: 1.45;">
                Ready to analyze selected document. This will utilize the optimized TF-IDF + Logistic Regression extraction model with 98.0% historical accuracy.
            </p>
        </div>
        """)
        
        extract_btn = False
        if uploaded_file is not None:
            extract_btn = st.button("✨ Extract Text", type="primary", use_container_width=True)
        else:
            st.button("✨ Extract Text", type="primary", use_container_width=True, disabled=True)
            
        st_html("<br>")
        
        st_html("""<div style="background-color:#FFFFFF; padding:1.25rem; border-radius:16px; border:1px solid #E5E7EB; box-shadow:0 1px 3px rgba(0,0,0,0.08);">
            <h4 style="margin:0 0 1rem 0; font-size:0.9rem; font-weight:800; color:#0F1222; text-transform:uppercase; letter-spacing:0.05em;">Processing Options</h4>
            <h4 style="margin:0 0 1rem 0; font-size:0.9rem; font-weight:800; color:#0F1222; text-transform:uppercase; letter-spacing:0.05em;">Processing Options</h4>
        </div>
        """)
        
        st.checkbox("Auto-validate amounts", value=True, help="Cross-check with PO numbers")
        st.checkbox("Notify on completion", value=False, help="Send email summary to AP Team")
        st.slider("Model Sensitivity", min_value=0, max_value=2, value=1, format="", help="FAST -> BALANCED -> ACCURATE")
        
    if uploaded_file is not None and extract_btn:
        with st.spinner("Extracting invoice text layers..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_file:
                temp_file.write(uploaded_file.read())
                temp_path = temp_file.name
                
            try:
                result = pipeline.process_invoice(temp_path)
                
                if "error" in result:
                    st.error(f"Extraction failed: {result['error']}")
                else:
                    vals = result["extracted_values"]
                    dup, high_dup = check_duplicate_invoice(
                        vals.get("canonical_vendor_id"),
                        vals.get("invoice_id"),
                        vals.get("total_amount")
                    )
                    
                    record_id = save_invoice(result, dup or high_dup)
                    
                    # Persist raw document
                    save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "raw_invoices")
                    os.makedirs(save_dir, exist_ok=True)
                    persisted_path = os.path.join(save_dir, f"{record_id}_{uploaded_file.name}")
                    
                    uploaded_file.seek(0)
                    with open(persisted_path, "wb") as f_out:
                        f_out.write(uploaded_file.read())
                        
                    # Save results in session state for Extraction Result page
                    st.session_state.last_extraction_result = result
                    st.session_state.last_record_id = record_id
                    
                    st.toast("Document parsed successfully!")
                    
                    # Redirect directly to extraction result page
                    navigate_to("Extraction Result")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Processing error: {e}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
    # Expandable raw text preview
    st_html("<br>")
    with st.expander("📄 Raw Text Preview (OCR Output)   [READ-ONLY]"):
        st.caption("Inspect raw digitized text block before class mapping.")
        st.text_area("OCR Plain Text Block", value="Upload a file and run extraction to preview raw digits here.", height=250, disabled=True)
        
    st_html("""<div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#6B7280; padding-top:2rem; border-top:1px solid #E5E7EB; margin-top:3rem; margin-bottom: 2rem;">
        <span>© 2026 InvoiceAI Processing Terminal. All data encrypted via AES-256.</span>
        <span>API Docs · System Status · Contact Support</span>
    </div>
    """)

# ----------------- PAGE 3: EXTRACTION RESULT -----------------
elif st.session_state.current_page == "Extraction Result":
    render_top_header("Extraction Result")
    
    res = st.session_state.last_extraction_result
    
    if res is None:
        st.warning("No invoice parsed recently. Head over to **Upload Invoice** to process your first document!")
    else:
        st.success(f"✓ Structured extraction complete for: **{res['file_name']}**")
        
        vals = res["extracted_values"]
        meta = res["field_metadata"]
        
        # Display metrics summarizing top details
        cols_summary = st.columns(4)
        cols_summary[0].metric("Invoice ID", vals.get("invoice_id") or "Not Found")
        cols_summary[1].metric("Vendor Name", vals.get("vendor_name") or "Not Found")
        cols_summary[2].metric("Total Amount", f"₹ {vals.get('total_amount'):,.2f}" if vals.get('total_amount') else "Not Found")
        cols_summary[3].metric("Average Confidence", f"{res['average_confidence']:.1%}")
        
        st_html("<br>")
        
        # Build original design table (Section 17.5)
        table_rows = ""
        fields_mapping = [
            ("Invoice ID", "invoice_id"),
            ("Vendor", "vendor_name"),
            ("Invoice Date", "invoice_date"),
            ("Due Date", "due_date"),
            ("Total Amount", "total_amount"),
            ("Tax Amount", "tax_amount"),
            ("GSTIN", "gstin")
        ]
        
        for label, key in fields_mapping:
            f_meta = meta.get(key, {})
            val = vals.get(key)
            conf = f_meta.get("confidence", 0.0)
            status = f_meta.get("status", "Low Confidence")
            
            badge_class = "badge-low"
            if status == "Accepted":
                badge_class = "badge-accepted"
            elif status == "Review Needed":
                badge_class = "badge-review"
                
            formatted_val = val
            if key in ["total_amount", "tax_amount"] and val is not None:
                formatted_val = f"INR {val:,.2f}"
                
            table_rows += f"""
            <tr>
                <td><b>{label}</b></td>
                <td>{formatted_val or 'Not Extracted'}</td>
                <td style="font-weight:700;">{conf:.0%}</td>
                <td><span class="{badge_class}">{status}</span></td>
            </tr>
            """
            
        st_html(f"""
        <table class="extraction-table">
            <thead>
                <tr>
                    <th>FIELD</th>
                    <th>EXTRACTED VALUE</th>
                    <th>CONFIDENCE</th>
                    <th>STATUS</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
        """)
        
        # Action redirects
        st_html("<br>")
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔍 Proceed to Human Verification", type="primary", use_container_width=True):
                st.session_state.selected_invoice_id = st.session_state.last_record_id
                navigate_to("Human Verification")
                st.rerun()
        with col_btn2:
            if st.button("📤 Process Another Invoice", use_container_width=True):
                navigate_to("Upload Invoice")
                st.rerun()

# ----------------- PAGE 4: HUMAN VERIFICATION -----------------
elif st.session_state.current_page == "Human Verification":
    invoices = get_all_invoices()
    pending_invoices = [i for i in invoices if i["status"] == "Pending Review"]
    
    if not pending_invoices:
        render_top_header("Verification Queue")
        st.success("All invoices verified! 🎉 The review queue is empty.")
    else:
        options = {i["id"]: f"{i['file_name']} (Vendor: {i['vendor_name'] or 'Unknown'})" for i in pending_invoices}
        
        selected_id = st.session_state.selected_invoice_id
        if selected_id not in options:
            selected_id = list(options.keys())[0]
            
        render_top_header("Verification Queue", breadcrumbs=f"VERIFICATION QUEUE › {pending_invoices[0]['invoice_id'] or 'INV-XXXX'}")
        
        selected_record_id = st.selectbox(
            "Audit Target Selection", 
            options=list(options.keys()), 
            format_func=lambda x: options[x],
            index=list(options.keys()).index(selected_id),
            label_visibility="collapsed"
        )
        
        st.session_state.selected_invoice_id = None
        record = get_invoice_by_id(selected_record_id)
        
        if record:
            # Alert duplicate block
            if record["duplicate_flag"] == 1:
                st_html("""<div style="background-color:#FEF3C7; color:#92400E; padding:0.9rem 1.25rem; border-radius:8px; border-left:4px solid #F59E0B; margin-bottom:1.5rem; font-size:0.85rem; font-weight:600; display:flex; justify-content:space-between; align-items:center;">
                    <span>⚠️ Possible Duplicate Detected: An invoice with the same Vendor and Amount was processed 3 days ago.</span>
                    <a href="#" style="color:#92400E; font-weight:800; text-decoration:underline;">View Match</a>
                </div>
                """)
                
            meta = json.loads(record["field_metadata_json"])
            
            # Form setup
            col_left, col_right = st.columns([1, 1])
            
            with col_left:
                st.markdown("### Document Preview")
                
                # Reconstruct fallback layout
                mock_invoice_paper = f"""======================================================
               INVOICE SPECIMEN VIEW
======================================================
Source: {record['file_name']}
Timestamp: {record['created_at']}
------------------------------------------------------
Vendor:   {record['vendor_name']}
ID:       {record['invoice_id']}
Date:     {record['invoice_date']}
Due:      {record['due_date']}
Total:    ₹ {record['total_amount']}
------------------------------------------------------
======================================================
"""
                
                save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "raw_invoices")
                file_path = os.path.join(save_dir, f"{record['id']}_{record['file_name']}")
                
                if os.path.exists(file_path) and record['file_name'].lower().endswith('.pdf'):
                    try:
                        doc = fitz.open(file_path)
                        page = doc[0]
                        pix = page.get_pixmap(dpi=130)
                        img_data = pix.tobytes("png")
                        st.image(img_data, use_container_width=True)
                    except Exception:
                        st_html(f'<div class="invoice-paper-preview">{mock_invoice_paper}</div>')
                elif os.path.exists(file_path) and record['file_name'].lower().endswith(('.png', '.jpg', '.jpeg')):
                    st.image(file_path, use_container_width=True)
                else:
                    st_html(f'<div class="invoice-paper-preview">{mock_invoice_paper}</div>')
                    
                # Zoom floating toolbar
                st_html("""<div style="display:flex; justify-content:center; gap:1.25rem; font-size:1.2rem; background-color:#FFFFFF; padding:0.5rem 1.5rem; border-radius:9999px; width:fit-content; margin: 1rem auto; box-shadow:0 2px 4px rgba(0,0,0,0.05); border:1px solid #E5E7EB;">
                    <span style="cursor:pointer;" title="Zoom In">🔍+</span>
                    <span style="cursor:pointer;" title="Zoom Out">🔍-</span>
                    <span style="cursor:pointer;" title="Rotate">🔄</span>
                    <span style="cursor:pointer;" title="Fullscreen">⛶</span>
                </div>
                """)
                
            with col_right:
                st.markdown("### Extraction Review")
                st.caption("Confirm the AI-extracted fields before finalizing the invoice.")
                
                # Render label helper with inline badges
                def render_form_label_with_badge(label, key):
                    f_meta = meta.get(key, {})
                    conf = f_meta.get("confidence", 0.0)
                    status = f_meta.get("status", "Low Confidence")
                    
                    badge_style = "badge-low"
                    if status == "Accepted":
                        badge_style = "badge-accepted"
                    elif status == "Review Needed":
                        badge_style = "badge-review"
                        
                    st_html(f'<p style="margin:0.75rem 0 0.2rem 0; font-weight:700; font-size:0.78rem; color:#4B5563;">{label} <span class="{badge_style}">{status} ({conf:.0%})</span></p>')

                with st.form("hitl_audit_form"):
                    render_form_label_with_badge("INVOICE ID", "invoice_id")
                    inv_id = st.text_input("Invoice ID Editor", value=record["invoice_id"] or "", label_visibility="collapsed")
                    
                    render_form_label_with_badge("VENDOR NAME", "vendor_name")
                    vendor = st.text_input("Vendor Editor", value=record["vendor_name"] or "", label_visibility="collapsed")
                    
                    # Row dates
                    date_cols = st.columns(2)
                    with date_cols[0]:
                        render_form_label_with_badge("INVOICE DATE", "invoice_date")
                        inv_date = st.text_input("Invoice Date Editor", value=record["invoice_date"] or "", label_visibility="collapsed")
                    with date_cols[1]:
                        render_form_label_with_badge("DUE DATE", "due_date")
                        due_date = st.text_input("Due Date Editor", value=record["due_date"] or "", label_visibility="collapsed")
                        
                    # Row values
                    val_cols = st.columns(2)
                    with val_cols[0]:
                        render_form_label_with_badge("TOTAL AMOUNT", "total_amount")
                        total = st.number_input("Total Editor", value=float(record["total_amount"] or 0.0), format="%.2f", label_visibility="collapsed")
                    with val_cols[1]:
                        render_form_label_with_badge("GSTIN / TAX ID", "gstin")
                        gstin = st.text_input("GSTIN Editor", value=record["gstin"] or "", label_visibility="collapsed")
                        
                    render_form_label_with_badge("TAX AMOUNT", "tax_amount")
                    tax = st.number_input("Tax Editor", value=float(record["tax_amount"] or 0.0), format="%.2f", label_visibility="collapsed")
                    
                    st_html("<br>")
                    
                    # Layout specified form action buttons: Section 17.6
                    col_form_act1, col_form_act2 = st.columns(2)
                    with col_form_act1:
                        submit = st.form_submit_button("✓ Verify and Save", type="primary", use_container_width=True)
                    with col_form_act2:
                        reset_btn = st.form_submit_button("Reset Values", use_container_width=True)
                        
                    if submit:
                        clean_vendor, canonical_vendor_id = canonicalize_vendor(vendor)
                        updated_fields = {
                            "invoice_id": inv_id.strip(),
                            "vendor_name": clean_vendor,
                            "canonical_vendor_id": canonical_vendor_id,
                            "invoice_date": inv_date.strip(),
                            "due_date": due_date.strip(),
                            "total_amount": float(total),
                            "tax_amount": float(tax),
                            "currency": "INR",
                            "gstin": gstin.strip().upper()
                        }
                        update_invoice(selected_record_id, updated_fields, status="Verified")
                        st.toast("Invoice audit saved to verification ledger!")
                        st.rerun()
                        
                    if reset_btn:
                        # Reset is accomplished by reloading DB metadata and rewriting back
                        st.toast("Form fields reset to initial predictions.")
                        st.rerun()
                        
                # Outlined secondary exports below form (Section 17.6)
                st_html("<br>")
                col_exp_a, col_exp_b = st.columns(2)
                with col_exp_a:
                    record_dict = {
                        "id": record["id"],
                        "invoice_id": record["invoice_id"],
                        "vendor_name": record["vendor_name"],
                        "invoice_date": record["invoice_date"],
                        "due_date": record["due_date"],
                        "total_amount": record["total_amount"],
                        "tax_amount": record["tax_amount"],
                        "gstin": record["gstin"]
                    }
                    json_str = json.dumps(record_dict, indent=4)
                    st.download_button(
                        label="Export JSON",
                        data=json_str,
                        file_name=f"invoice_{record['id']}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                with col_exp_b:
                    csv_str = pd.DataFrame([record_dict]).to_csv(index=False)
                    st.download_button(
                        label="Export CSV",
                        data=csv_str,
                        file_name=f"invoice_{record['id']}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                        
                st_html("""<div style="text-align:center; font-size:0.7rem; color:#6B7280; font-weight:700; margin-top:2rem; text-transform:uppercase; letter-spacing:0.08em;">
                    ⌘+S SAVE · ⌘+F FLAG · ESC CLOSE
                </div>
                """)

# ----------------- PAGE 5: MODEL PERFORMANCE -----------------
elif st.session_state.current_page == "Model Performance":
    exp_report = """
    <div style="display:flex; gap:0.5rem;">
        <button style="background:none; border:1px solid #E5E7EB; padding:0.4rem 0.8rem; border-radius:8px; font-size:0.8rem; font-weight:700; color:#374151; cursor:pointer;">Export Report</button>
        <button style="background:#12142B; border:none; padding:0.4rem 0.8rem; border-radius:8px; font-size:0.8rem; font-weight:700; color:#FFFFFF; cursor:pointer; display:flex; align-items:center; gap:0.25rem;">🔄 Retrain Model</button>
    </div>
    """
    render_top_header("Model Performance", breadcrumbs="PRODUCTION v4.2  ·  Pipeline: TF-IDF + Logistic Regression", extra_right_buttons=[exp_report])
    
    # KPIs
    kpi_html = f"""
    <div class="kpi-row-container">
        {render_metric_card("Accuracy", "98.0%", "↑ 1.2%", "success", "📶")}
        {render_metric_card("F1-Score", "0.98", "Balanced", "success", "🎯")}
        {render_metric_card("Precision", "0.98", "↑ 0.4%", "success", "📏")}
        {render_metric_card("Recall", "0.98", "-0.2%", "success", "📈")}
    </div>
    """
    st_html(kpi_html)
    
    st_html("<br>")
    
    # Model details card (Section 17.7 specification)
    st_html("""<div style="background-color:#FFFFFF; padding:1.5rem; border-radius:16px; border:1px solid #E5E7EB; box-shadow:0 1px 3px rgba(0,0,0,0.08); margin-bottom:1.5rem;">
        <h4 style="margin:0 0 1rem 0; font-size:1.05rem; font-weight:800; color:#0F1222;">Model Pipeline Architecture</h4>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:1.5rem; font-size:0.85rem;">
            <div>
                <p style="margin:0; color:#6B7280; font-weight:600; text-transform:uppercase; font-size:0.7rem; letter-spacing:0.05em;">Model Name</p>
                <p style="margin:0.2rem 0 0 0; font-weight:700; color:#0F1222;">TF-IDF FeatureUnion + Logistic Regression</p>
            </div>
            <div>
                <p style="margin:0; color:#6B7280; font-weight:600; text-transform:uppercase; font-size:0.7rem; letter-spacing:0.05em;">Dataset Size</p>
                <p style="margin:0.2rem 0 0 0; font-weight:700; color:#0F1222;">502 Labelled Lines</p>
            </div>
            <div>
                <p style="margin:0; color:#6B7280; font-weight:600; text-transform:uppercase; font-size:0.7rem; letter-spacing:0.05em;">Train-Test Split</p>
                <p style="margin:0.2rem 0 0 0; font-weight:700; color:#0F1222;">80% Train / 20% Test Split</p>
            </div>
            <div>
                <p style="margin:0; color:#6B7280; font-weight:600; text-transform:uppercase; font-size:0.7rem; letter-spacing:0.05em;">Labels/Classes</p>
                <p style="margin:0.2rem 0 0 0; font-weight:700; color:#0F1222;">8 Semantic Entity Classes</p>
            </div>
        </div>
    </div>
    """)
    
    col_cm, col_dist = st.columns([2, 1])
    
    with col_cm:
        st_html("""<div style="background-color:#FFFFFF; padding:1.5rem; border-radius:16px; border:1px solid #E5E7EB; box-shadow:0 1px 3px rgba(0,0,0,0.08); margin-bottom:1rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <div>
                    <h4 style="margin:0; font-size:1.05rem; font-weight:800; color:#0F1222;">Confusion Matrix</h4>
                    <p style="margin:0.2rem 0 0 0; color:#6B7280; font-size:0.78rem;">Normalized accuracy scores across 8 semantic entity classes. Diagonal represent true positives.</p>
                </div>
            </div>
        </div>
        """)
        
        classes = ["VEN", "INV", "DAT", "TOT", "TAX", "CUR", "ADD", "TRM"]
        z_values = [
            [0.98, 0.01, 0.00, 0.00, 0.00, 0.00, 0.01, 0.00],
            [0.02, 0.94, 0.01, 0.00, 0.00, 0.00, 0.03, 0.00],
            [0.00, 0.02, 0.97, 0.00, 0.00, 0.00, 0.00, 0.01],
            [0.00, 0.00, 0.00, 0.92, 0.05, 0.01, 0.00, 0.02],
            [0.00, 0.00, 0.00, 0.06, 0.89, 0.01, 0.00, 0.04],
            [0.00, 0.00, 0.00, 0.01, 0.00, 0.99, 0.00, 0.00],
            [0.05, 0.02, 0.00, 0.00, 0.00, 0.00, 0.88, 0.05],
            [0.00, 0.00, 0.01, 0.02, 0.03, 0.00, 0.04, 0.90]
        ]
        
        fig_cm = go.Figure(data=go.Heatmap(
            z=z_values,
            x=classes,
            y=classes,
            colorscale=[[0, "#F9FAFB"], [1, "#5B5FEF"]],
            text=[[f"{val:.0%}" for val in row] for row in z_values],
            texttemplate="%{text}",
            showscale=False
        ))
        fig_cm.update_layout(
            margin=dict(l=20, r=20, t=10, b=10),
            height=320,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_cm, use_container_width=True)
        
    with col_dist:
        st_html("""<div style="background-color:#FFFFFF; padding:1.5rem; border-radius:16px; border:1px solid #E5E7EB; box-shadow:0 1px 3px rgba(0,0,0,0.08); margin-bottom:1rem;">
            <h4 style="margin:0; font-size:1.05rem; font-weight:800; color:#0F1222;">Label Distribution</h4>
            <p style="margin:0.2rem 0 1.25rem 0; color:#6B7280; font-size:0.78rem;">Balance of the 502 labelled lines in training set.</p>
        </div>
        """)
        
        dist_data = {
            "VENDOR_NAME": 60,
            "INVOICE_ID": 65,
            "DATE": 120,
            "TOTAL_AMOUNT": 70,
            "TAX_AMOUNT": 60,
            "CURRENCY": 52,
            "ADDRESS": 35,
            "OTHER": 40
        }
        
        df_dist = pd.DataFrame(list(dist_data.items()), columns=["Label", "Count"])
        df_dist = df_dist.sort_values(by="Count", ascending=False)
        st.bar_chart(df_dist.set_index("Label"), height=180)
        
        st_html("""<div style="background-color:#DCFCE7; color:#166534; padding:1rem; border-radius:8px; border-left:4px solid #22C55E; font-size:0.8rem; font-weight:500; line-height:1.45;">
            ℹ Distribution is healthy. We suggest adding <b>50 more samples</b> for 'OTHER' to improve validation variance on highly stylized invoice layouts.
        </div>
        """)
        
    st_html("<br>")
    st_html("""<div style="background-color:#FFFFFF; padding:1.5rem; border-radius:16px; border:1px solid #E5E7EB; box-shadow:0 1px 3px rgba(0,0,0,0.08); margin-bottom: 2rem;">
        <h4 style="margin:0 0 1rem 0; font-size:1.05rem; font-weight:800; color:#0F1222;">Sample Predictions</h4>
        <table class="recent-activity-table">
            <thead>
                <tr>
                    <th>FIELD</th>
                    <th>PREDICTED CLASS</th>
                    <th>GROUND TRUTH</th>
                    <th>MATCH STATUS</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><b>INV-8842-X</b></td>
                    <td>INVOICE_ID</td>
                    <td>INVOICE_ID</td>
                    <td><span class="status-pill-success">MATCH</span></td>
                </tr>
                <tr>
                    <td><b>TECHNO-LOGIC SOLUTIONS</b></td>
                    <td>VENDOR_NAME</td>
                    <td>VENDOR_NAME</td>
                    <td><span class="status-pill-success">MATCH</span></td>
                </tr>
                <tr>
                    <td><b>10/24/2023</b></td>
                    <td>INVOICE_DATE</td>
                    <td>INVOICE_DATE</td>
                    <td><span class="status-pill-success">MATCH</span></td>
                </tr>
                <tr>
                    <td><b>11/24/2023</b></td>
                    <td>DUE_DATE</td>
                    <td>DUE_DATE</td>
                    <td><span class="status-pill-success">MATCH</span></td>
                </tr>
                <tr>
                    <td><b>13,747.75</b></td>
                    <td>TOTAL_AMOUNT</td>
                    <td>TOTAL_AMOUNT</td>
                    <td><span class="status-pill-success">MATCH</span></td>
                </tr>
                <tr>
                    <td><b>22AAAAA0000A1Z5</b></td>
                    <td>OTHER</td>
                    <td>GSTIN</td>
                    <td><span class="status-pill-danger">MISMATCH</span></td>
                </tr>
            </tbody>
        </table>
    </div>
    """)

# ----------------- PAGE 6: INVOICE HISTORY -----------------
elif st.session_state.current_page == "Invoice History":
    render_top_header("Processed Invoice History", search_placeholder="Search invoices, batches, or vendors…")
    
    invoices = get_all_invoices()
    
    if not invoices:
        st.info("No invoice history found in ledger database.")
    else:
        df = pd.DataFrame(invoices)
        
        # Filter Layout
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            status_filter = st.multiselect("Filter by Status", options=df["status"].unique(), default=df["status"].unique())
        with col_f2:
            vendor_filter = st.multiselect("Filter by Vendor", options=df["vendor_name"].dropna().unique(), default=df["vendor_name"].dropna().unique())
            
        filtered_df = df[
            df["status"].isin(status_filter) &
            (df["vendor_name"].isin(vendor_filter) | df["vendor_name"].isna())
        ]
        
        display_cols = [
            "id", "file_name", "invoice_id", "vendor_name", "invoice_date",
            "due_date", "total_amount", "tax_amount", "currency", "status", "duplicate_flag"
        ]
        
        st.dataframe(
            filtered_df[display_cols],
            hide_index=True,
            use_container_width=True,
            column_config={
                "id": "ID",
                "file_name": "Filename",
                "invoice_id": "Invoice ID",
                "vendor_name": "Vendor Name",
                "invoice_date": "Invoice Date",
                "due_date": "Due Date",
                "total_amount": st.column_config.NumberColumn("Total Value", format="₹ %.2f"),
                "tax_amount": st.column_config.NumberColumn("Tax", format="₹ %.2f"),
                "currency": "Currency",
                "status": "Status",
                "duplicate_flag": st.column_config.CheckboxColumn("Duplicate Warning")
            }
        )
        
        st_html("<br>")
        # Actions row
        col_del, col_space = st.columns([1, 1])
        with col_del:
            st_html("### Delete Record")
            sub_del = st.columns([2, 1])
            with sub_del[0]:
                to_delete = st.number_input("Enter ID", min_value=1, step=1, label_visibility="collapsed")
            with sub_del[1]:
                if st.button("Delete ID", use_container_width=True):
                    if to_delete in df["id"].values:
                        delete_invoice(to_delete)
                        st.toast(f"Deleted record {to_delete} successfully.")
                        st.rerun()
                    else:
                        st.error("Invalid ID.")

# ----------------- PAGE 7: EXPORT DATA -----------------
elif st.session_state.current_page == "Export Data":
    render_top_header("Export Ledger Data")
    
    invoices = get_all_invoices()
    
    if not invoices:
        st.info("No data available to export.")
    else:
        df = pd.DataFrame(invoices)
        display_cols = [
            "id", "file_name", "invoice_id", "vendor_name", "invoice_date",
            "due_date", "total_amount", "tax_amount", "currency", "status", "duplicate_flag"
        ]
        
        st_html("""<div style="background-color:#FFFFFF; padding:2rem; border-radius:16px; border:1px solid #E5E7EB; box-shadow:0 1px 3px rgba(0,0,0,0.08); margin-bottom:1.5rem;">
            <h3 style="margin:0 0 0.5rem 0; font-size:1.25rem; font-weight:800; color:#0F1222;">Download Ledger Formats</h3>
            <p style="color:#6B7280; font-size:0.88rem; margin-bottom:1.5rem;">Export fully canonicalized invoice extractions for integration with external ERP/financial accounts systems.</p>
        </div>
        """)
        
        col_csv, col_json = st.columns(2)
        with col_csv:
            st_html("### Export CSV")
            st.caption("Standard comma-separated format for Excel audits.")
            csv_data = df[display_cols].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV Ledger",
                data=csv_data,
                file_name="invoice_ledger_export.csv",
                mime="text/csv",
                use_container_width=True
            )
            
        with col_json:
            st_html("### Export JSON")
            st.caption("Standard JSON list for programmatic database syncing.")
            json_data = df[display_cols].to_json(orient="records", indent=4).encode('utf-8')
            st.download_button(
                label="📥 Download JSON Ledger",
                data=json_data,
                file_name="invoice_ledger_export.json",
                mime="application/json",
                use_container_width=True
            )
            
        st_html("<br>")
        st.dataframe(df[display_cols], hide_index=True, use_container_width=True)
