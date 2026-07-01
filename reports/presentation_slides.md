# Presentation Slides: Smart Invoice Automation Platform

A comprehensive presentation outline to accompany the final project demo for evaluation juries and professors.

---

## Slide 1: Title Slide
* **Topic**: Automated AP Ledger Processing using Semantic Line Classification
* **Subtitle**: An E2E Machine Learning & Human-in-the-Loop Accounts Payable Solution
* **Presenter**: Student Team
* **Target Auditor**: Financial Auditing and Automated Operations Jury

---

## Slide 2: The Core Problem
* **Business Pain Point**: Manual invoice data entry is slow, error-prone, and leaves organizations vulnerable to duplicate invoice submissions and payment frauds.
* **Technical Challenge**: Invoice layouts are highly variable. Simple keyword rules or coordinates-based scrapers break when invoice styling or formatting shifts slightly.
* **Our Objectives**:
  * Implement intelligent semantic line classification using Machine Learning.
  * Extract key financial fields dynamically without relying on absolute coordinates.
  * Incorporate a clean, responsive human-in-the-loop dashboard to review low-confidence extractions.

---

## Slide 3: System Architecture
* **Ingestion Layer**: Uploads PDFs or raw images, dynamically extracts text layers via PyMuPDF or Tesseract OCR.
* **Extraction & Classification**: 
  * Lowercase normalization and digit token removal.
  * Word + Character TF-IDF feature unions.
  * Trained Logistic Regression classifier to tag lines as specific entity headers.
* **Orchestration & Validation**:
  * Regex-based canonical value extraction (amounts, GSTIN, dates).
  * Auto-validation and duplicate checks.
* **Persistence**: SQLite database storing ledger history and field-level extraction confidences.

---

## Slide 4: ML Model Performance
* **Features Used**: Char n-grams (1-5) and word-level TF-IDF vectors capture localized formatting styles (like colons, currencies, date dividers) in combination with keyword vocabularies.
* **Overall Accuracy**: **98.00%** on validation tests.
* **Accuracy Matrix**:
  * **Due Date, GSTIN, Total Amount**: 1.00 F1-Score (Flawless precision)
  * **Invoice ID, Vendor Name**: 0.96 F1-Score
  * **Other / Noise**: 0.93 F1-Score

---

## Slide 5: Portal Highlights
* **Dynamic AP Dashboard**: Houses 6 metric counts and interactive Plotly timelines of financial pipeline flows, directly synchronized with database CRUD entries.
* **Visual Document Viewport**: PyMuPDF renders the uploaded invoice PDF natively on the left column, overlaying toolbars to zoom/rotate in-memory.
* **HitL Verification Screen**: Form controls pre-populated with extracted values, color-coded confidence indicators (Accepted vs Review Needed), and reset actions to audit records before entry.
* **Duplicate Warnings Banner**: Emits yellow warning notices instantly if identical vendor, amount, and date pairings indicate possible duplicate payments.

---

## Slide 6: Business Benefits & ROI
* **Processing Efficiency**: Reduces invoice entry times by up to **80%** by shifting human workload from typing data to merely auditing low-confidence fields.
* **Error Prevention**: Dynamic duplicate validation acts as an active safety net, preventing double-processing errors.
* **Audit Tracking**: Full-ledger JSON and CSV exports store OCR confidence scores and verifier timestamps, ensuring 100% audit compliance.
