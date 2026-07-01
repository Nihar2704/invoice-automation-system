# Smart Invoice Automation System using OCR and Machine Learning

## Complete MVP Roadmap and Implementation Guide

**Recommended project title:** Smart Invoice Automation System using OCR and Machine Learning  
**Core ML approach:** OCR + Invoice Line Classification + Rule-based Value Extraction + Human Verification  
**Best MVP UI:** Streamlit, minimalist professional dashboard  
**Target duration:** 30 days  
**Primary domain:** Machine Learning, NLP, Smart Automation, FinTech  

---

## 1. Executive Summary

This project solves a real business problem faced by **Accounts Payable (AP) departments**. In companies, vendors send invoices in different formats such as PDFs, scanned images, email text, and digital documents. AP teams manually read these invoices, identify important fields, enter the information into accounting systems, check for duplicates, verify due dates, and process payments.

Manual invoice processing is slow, repetitive, costly, and error-prone. It can lead to incorrect payments, duplicate payments, late fees, poor audit trails, and inefficient financial operations.

The proposed system automates this process using **OCR and Machine Learning**. It reads invoice documents, extracts text, classifies invoice lines using an ML model, extracts important values, standardizes the data, flags uncertain fields for human review, detects duplicates, and exports the final verified output as JSON/CSV.

The MVP is designed to be practical, presentable, and suitable for a one-month machine learning vocational training project.

---

## 2. AP Department Problem We Are Solving

### 2.1 What is Accounts Payable?

**Accounts Payable (AP)** is the department responsible for managing the money a company owes to vendors, suppliers, service providers, and contractors.

For example, a company may purchase:

- Laptops from a hardware supplier
- Office furniture from a furniture vendor
- Raw materials from a manufacturer
- Internet services from a telecom provider
- Cloud services from AWS, Azure, or Google Cloud
- Software subscriptions from Microsoft, Adobe, or other vendors

After delivering goods or services, the vendor sends an **invoice** requesting payment. The AP department verifies the invoice and ensures that payment is made correctly and on time.

### 2.2 How AP is Related to Vendors

The business relationship is:

```text
Vendor provides goods/services
        ↓
Vendor sends invoice
        ↓
AP department receives invoice
        ↓
AP verifies invoice details
        ↓
AP schedules payment
        ↓
Vendor receives payment
```

The AP department acts as the company’s financial checkpoint before money goes out of the business.

### 2.3 Manual AP Workflow

A typical manual AP workflow looks like this:

```text
1. Vendor sends invoice by email/PDF/scanned copy
2. AP employee opens and reads the invoice
3. Employee manually identifies invoice number, vendor name, date, due date, amount, tax, etc.
4. Employee enters the data into Excel/accounting software/ERP
5. Employee checks for duplicate invoices
6. Employee sends invoice for approval
7. Payment is scheduled
8. Final records are stored for audit and compliance
```

### 2.4 Pain Points in Manual Invoice Processing

| Problem | Explanation | Business Impact |
|---|---|---|
| High manual effort | Employees manually read and enter invoice details | Wastes time and increases cost |
| Different invoice formats | Every vendor uses a different layout and wording | Rule-based extraction becomes unreliable |
| Data entry mistakes | Wrong amount, date, vendor, or invoice number can be entered | Incorrect payments and accounting errors |
| Duplicate invoices | Same invoice may be submitted more than once | Duplicate payments and financial loss |
| Late processing | Slow approval/payment cycle | Late fees and damaged vendor relationships |
| Poor audit trail | Invoice data scattered across emails and files | Hard to track and audit |
| Scaling issue | More vendors mean more invoices | AP team cannot scale efficiently |

### 2.5 Project Problem Statement

Companies receive large numbers of invoices from multiple vendors in inconsistent formats. AP teams manually extract important invoice details and enter them into accounting systems. This manual process is slow, repetitive, error-prone, and difficult to scale.

The project aims to build an **AI-powered invoice automation system** that can extract, classify, verify, standardize, and export invoice data using OCR and machine learning.

---

## 3. Aim of the Project

The aim of this project is to build a machine learning-based invoice automation system that:

1. Accepts invoice PDFs or images.
2. Extracts text using OCR or PDF text extraction.
3. Classifies invoice text lines using a trained ML model.
4. Extracts key financial fields such as invoice number, vendor name, invoice date, due date, total amount, tax amount, GSTIN, and currency.
5. Assigns confidence scores to extracted fields.
6. Flags low-confidence fields for human verification.
7. Standardizes dates, currencies, and vendor names.
8. Detects possible duplicate invoices.
9. Exports verified data in JSON/CSV format.
10. Provides a simple, modern, professional dashboard for live demonstration.

---

## 4. Why OCR + Line Classification?

### 4.1 Core Idea

Instead of trying to extract all values directly from the whole invoice, the system first splits extracted text into separate lines. Then a supervised ML model classifies each line into a category.

Example:

```text
ABC Traders Pvt Ltd
Invoice No: INV-1023
Invoice Date: 12/06/2026
Due Date: 25/06/2026
GST Amount: ₹2,400
Grand Total: ₹45,600
```

The model predicts:

| Invoice Line | Predicted Class |
|---|---|
| ABC Traders Pvt Ltd | VENDOR_NAME |
| Invoice No: INV-1023 | INVOICE_ID |
| Invoice Date: 12/06/2026 | INVOICE_DATE |
| Due Date: 25/06/2026 | DUE_DATE |
| GST Amount: ₹2,400 | TAX_AMOUNT |
| Grand Total: ₹45,600 | TOTAL_AMOUNT |

After classification, regex and validation rules extract the exact value.

Example:

```text
Line: Grand Total: ₹45,600
ML Prediction: TOTAL_AMOUNT
Final Extracted Value: INR 45600
```

### 4.2 Why This is Suitable for 1-Month VT

This approach is ideal because:

- It clearly includes a trainable ML model.
- Dataset preparation is easier than NER.
- It is easier to explain to professors.
- It works well for small-to-medium labelled datasets.
- It gives confidence scores through model probabilities.
- It allows stable live demo even with limited training data.
- It can be built fully in Python using Streamlit and scikit-learn.

---

## 5. System Architecture

### 5.1 High-Level Architecture

```text
User
 ↓
Streamlit Web App
 ↓
Invoice Upload Module
 ↓
File Type Detection
 ↓
Text Extraction Layer
 ├── Text-based PDF → pdfplumber / PyMuPDF
 └── Image/Scanned PDF → OCR using Tesseract/EasyOCR
 ↓
Text Cleaning and Line Splitting
 ↓
ML Line Classification Model
 ├── TF-IDF Vectorizer
 └── Logistic Regression Classifier
 ↓
Field-wise Value Extraction
 ↓
Confidence Score Calculation
 ↓
Human Verification Interface
 ↓
Data Canonicalization
 ↓
Duplicate Invoice Detection
 ↓
JSON/CSV Export
 ↓
Local Storage / SQLite Database
```

### 5.2 MVP System Flow

```text
1. User uploads invoice
2. System extracts raw text
3. Text is cleaned and split into lines
4. Each line is passed to ML model
5. Model predicts label and confidence
6. System extracts exact field values
7. Low-confidence fields are marked for review
8. User verifies/corrects fields
9. Data is standardized
10. Duplicate check is performed
11. Final data is saved/exported
```

### 5.3 Component Architecture

| Module | Responsibility |
|---|---|
| Upload Module | Accept PDF/image invoice files |
| OCR/PDF Parser | Convert invoice into machine-readable text |
| Text Cleaner | Remove noise, extra spaces, unwanted characters |
| Line Splitter | Break invoice text into meaningful lines |
| ML Classifier | Classify each line into invoice field category |
| Value Extractor | Extract exact value from classified line |
| Confidence Engine | Decide whether extraction is accepted or needs review |
| Verification UI | Allow user to manually correct extracted values |
| Canonicalization Engine | Convert raw values to standard format |
| Duplicate Detector | Detect repeated invoice submissions |
| Export Engine | Generate JSON/CSV/Excel output |
| Storage Layer | Save processed invoice records |

---

## 6. Recommended Tech Stack

### 6.1 Best MVP Stack

| Layer | Recommended Tool | Reason |
|---|---|---|
| UI | Streamlit | Fast, Python-native, ideal for ML demos |
| Language | Python | Best ecosystem for ML/OCR/data processing |
| ML Model | scikit-learn | Simple, reliable, easy to explain |
| Feature Extraction | TF-IDF Vectorizer | Converts invoice text lines into numerical features |
| Classifier | Logistic Regression | Strong baseline for text classification and supports probabilities |
| OCR | Tesseract OCR / EasyOCR | Extracts text from scanned images |
| PDF Text Extraction | pdfplumber / PyMuPDF | Extracts text from text-based PDFs |
| Data Handling | pandas | CSV, dataframe, preprocessing, export |
| Model Saving | joblib | Save and load trained ML pipeline |
| Database | SQLite | Lightweight local database for MVP |
| Charts | Streamlit charts / Matplotlib | Dashboard and model performance visualization |
| Export | CSV/JSON/Excel | Required for accounting-system compatibility |

### 6.2 Why Streamlit Instead of React for MVP

For a one-month ML vocational training project, Streamlit is better because:

- It keeps the entire project in Python.
- It is faster to develop.
- It directly supports file upload, tables, charts, forms, and download buttons.
- It makes model performance easy to display.
- It reduces frontend/backend/API complexity.

React can be used later if you want to convert the project into a full production web app.

### 6.3 Optional Advanced Stack After MVP

| Layer | Advanced Option |
|---|---|
| Frontend | React / Next.js |
| Backend | FastAPI |
| Database | PostgreSQL / MongoDB |
| OCR | PaddleOCR / Google Document AI / AWS Textract |
| ML/NLP | spaCy NER / LayoutLM / Donut |
| Deployment | Docker + Render/Railway/AWS |

---

## 7. ML Model Design

### 7.1 Model Objective

The ML model should classify invoice text lines into meaningful categories.

Input:

```text
"Grand Total: Rs. 45,600"
```

Output:

```text
TOTAL_AMOUNT
```

### 7.2 Target Labels

Recommended labels:

| Label | Meaning |
|---|---|
| VENDOR_NAME | Vendor/supplier/company name |
| INVOICE_ID | Invoice number, bill number, reference number |
| INVOICE_DATE | Date on which invoice was issued |
| DUE_DATE | Last date of payment |
| TOTAL_AMOUNT | Final payable amount |
| TAX_AMOUNT | GST/tax/CGST/SGST/IGST amount |
| GSTIN | GST identification number |
| CURRENCY | Currency symbol/code if explicitly present |
| PO_NUMBER | Purchase order number, optional |
| OTHER | Irrelevant lines like address, terms, thank-you text, footer, etc. |

For MVP, use these 8 labels:

```text
VENDOR_NAME
INVOICE_ID
INVOICE_DATE
DUE_DATE
TOTAL_AMOUNT
TAX_AMOUNT
GSTIN
OTHER
```

### 7.3 ML Pipeline

```text
Raw invoice line
        ↓
Text preprocessing
        ↓
TF-IDF vectorization
        ↓
Logistic Regression classifier
        ↓
Predicted label + confidence score
```

### 7.4 Why TF-IDF + Logistic Regression?

This combination is suitable because:

- Invoice line classification is a text classification problem.
- TF-IDF converts text into numerical features.
- Logistic Regression is fast, interpretable, and works well for small-to-medium datasets.
- It supports class probability output, which can be used as confidence score.
- It is easy to explain in viva/presentation.

### 7.5 Professor-Friendly Explanation

If asked “Where is the ML model?”, answer:

> The machine learning model is a supervised invoice-line classification model. I created a labelled dataset of invoice text lines. Each line is labelled as invoice number, vendor name, invoice date, due date, tax amount, total amount, GSTIN, or other. I used TF-IDF to convert text into numerical features and Logistic Regression to classify the lines. The model probability is used as a confidence score. Low-confidence predictions are sent for human verification.

---

## 8. Dataset Details

### 8.1 Dataset Strategy

Use a combination of:

1. **Custom labelled invoice-line dataset** for training the actual ML model.
2. **Synthetic Indian invoice samples** for testing and demo.
3. **Public receipt/invoice datasets** for reference and optional experimentation.

### 8.2 Custom Dataset Format

Create a CSV file:

```csv
text,label
"Invoice No: INV-1023",INVOICE_ID
"Bill Number: B-7781",INVOICE_ID
"Tax Invoice ID: TXN-9021",INVOICE_ID
"ABC Traders Pvt Ltd",VENDOR_NAME
"Vendor: Sharma Enterprises",VENDOR_NAME
"Invoice Date: 12/06/2026",INVOICE_DATE
"Date: 15-06-2026",INVOICE_DATE
"Due Date: 25/06/2026",DUE_DATE
"Payment Due: 30 June 2026",DUE_DATE
"Grand Total: Rs. 45,600",TOTAL_AMOUNT
"Amount Due: ₹52,000",TOTAL_AMOUNT
"GST Amount: ₹2,400",TAX_AMOUNT
"GSTIN: 22ABCDE1234F1Z5",GSTIN
"Thank you for your business",OTHER
```

### 8.3 Recommended Dataset Size

| Dataset Size | Suitability |
|---|---|
| 100–200 labelled lines | Basic prototype only |
| 300–500 labelled lines | Acceptable MVP |
| 700–1000 labelled lines | Strong college-level demo |
| 1500+ labelled lines | Better generalization |

Recommended target for your 1-month project:

```text
700–1000 labelled invoice lines
30–50 invoice templates
8 labels
```

### 8.4 Class Balance

Try to avoid a dataset where most examples are `OTHER`. Keep classes reasonably balanced.

Example target:

| Label | Approx Examples |
|---|---:|
| INVOICE_ID | 100 |
| VENDOR_NAME | 100 |
| INVOICE_DATE | 100 |
| DUE_DATE | 100 |
| TOTAL_AMOUNT | 120 |
| TAX_AMOUNT | 100 |
| GSTIN | 80 |
| OTHER | 200 |

### 8.5 Creating Synthetic Invoice Lines

Generate variations for each field.

#### Invoice ID Variations

```text
Invoice No: INV-1023
Invoice Number: INV/2026/045
Bill No: B-7781
Tax Invoice No: TXN-9021
Reference No: REF-5542
Document No: DOC-2026-008
```

#### Date Variations

```text
Invoice Date: 12/06/2026
Date: 12-Jun-2026
Issued On: June 12, 2026
Billing Date: 2026-06-12
Dated: 12-06-26
```

#### Due Date Variations

```text
Due Date: 25/06/2026
Payment Due: 25 June 2026
Pay Before: 2026-06-25
Last Date of Payment: 25-06-2026
```

#### Amount Variations

```text
Grand Total: ₹45,600
Total Amount: Rs. 45,600.00
Amount Due: INR 45600
Net Payable: ₹45,600
Balance Due: 45,600 INR
```

#### Tax Variations

```text
GST Amount: ₹2,400
CGST: ₹1,200
SGST: ₹1,200
IGST: ₹2,400
Tax Total: Rs. 2,400
```

### 8.6 Public Dataset References

Use these only as support/reference. Your custom dataset should remain the main training dataset.

| Dataset | Use |
|---|---|
| SROIE / ICDAR 2019 | Receipt OCR and key information extraction |
| CORD | Receipt understanding with OCR annotations and semantic labels |
| Kaggle Invoice OCR datasets | Invoice images and OCR-style annotations |
| Hugging Face invoice datasets | Synthetic or structured invoice document datasets |

### 8.7 Privacy Warning

Do not use real company invoices with private data unless fully anonymized. Invoices may contain addresses, GST numbers, bank details, vendor IDs, and financial information. For college demo, use synthetic or anonymized invoices.

---

## 9. Data Preprocessing

### 9.1 Text Cleaning Steps

For every extracted invoice line:

1. Strip leading/trailing spaces.
2. Replace multiple spaces with a single space.
3. Normalize currency symbols.
4. Remove unnecessary special characters where required.
5. Keep important symbols such as `/`, `-`, `.`, `₹`, `%`, `:` because they may help identify invoice fields.
6. Convert text to lowercase for model training if required.
7. Remove empty lines.

### 9.2 Example Cleaning

Raw line:

```text
   Grand   Total :    ₹ 45,600.00   
```

Cleaned line:

```text
Grand Total: ₹45,600.00
```

### 9.3 Line Splitting

After OCR/PDF extraction, split the text into lines:

```python
lines = raw_text.split("\n")
lines = [line.strip() for line in lines if line.strip()]
```

### 9.4 OCR Noise Handling

OCR may confuse characters:

| OCR Mistake | Possible Correction |
|---|---|
| `1NV` | `INV` |
| `O` | `0` in invoice numbers |
| `l` | `1` |
| `Rs,` | `Rs.` |
| `₹ 45,6OO` | `₹ 45,600` |

For MVP, handle common OCR mistakes using simple replacement rules.

---

## 10. Model Training Methodology

### 10.1 Training Steps

```text
1. Prepare labelled CSV dataset
2. Load dataset using pandas
3. Clean text lines
4. Split into train/test set
5. Build ML pipeline: TF-IDF + Logistic Regression
6. Train model
7. Evaluate using accuracy, precision, recall, F1-score
8. Save model using joblib
9. Load model in Streamlit app
10. Predict line labels during invoice processing
```

### 10.2 Suggested Training Pipeline

```python
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

model = Pipeline([
    ("tfidf", TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        max_features=5000
    )),
    ("clf", LogisticRegression(
        max_iter=1000,
        class_weight="balanced"
    ))
])
```

### 10.3 Train-Test Split

Use:

```text
80% training data
20% testing data
```

Example:

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    df["text"],
    df["label"],
    test_size=0.2,
    random_state=42,
    stratify=df["label"]
)
```

### 10.4 Evaluation Metrics

Show these metrics in the project:

| Metric | Meaning |
|---|---|
| Accuracy | Overall correct predictions |
| Precision | How many predicted labels were actually correct |
| Recall | How many actual labels were correctly found |
| F1-score | Balance between precision and recall |
| Confusion Matrix | Shows which classes are being confused |

### 10.5 Expected MVP Performance

For a good custom dataset, you can aim for:

```text
Accuracy: 85% to 95%
F1-score: 0.80+
```

Be honest in your report. Do not claim unrealistic results unless your test data proves it.

### 10.6 Model Output

For every line:

```json
{
  "line": "Grand Total: ₹45,600",
  "predicted_label": "TOTAL_AMOUNT",
  "confidence": 0.96
}
```

---

## 11. Field Extraction Logic

The model classifies the line. Then extraction rules take the exact value.

### 11.1 Invoice ID Extraction

Input:

```text
Invoice No: INV-1023
```

Output:

```text
INV-1023
```

Suggested regex idea:

```python
r"(?:invoice\s*(?:no|number|id)?|bill\s*no|ref\s*no)[:\-\s]*([A-Z0-9\-/]+)"
```

### 11.2 Date Extraction

Input:

```text
Invoice Date: 12/06/2026
```

Output:

```text
2026-06-12
```

Use `dateparser` or Python `datetime` with multiple formats.

### 11.3 Amount Extraction

Input:

```text
Grand Total: ₹45,600.00
```

Output:

```text
45600.00
```

Remove:

```text
₹
Rs.
INR
commas
extra spaces
```

### 11.4 GSTIN Extraction

Indian GSTIN format:

```text
22ABCDE1234F1Z5
```

Pattern idea:

```python
r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]\b"
```

### 11.5 Vendor Name Extraction

Vendor name is the hardest field because it may appear without a clear keyword. Use a mix of:

- ML label `VENDOR_NAME`
- Top section of invoice
- Keywords like `Vendor`, `Supplier`, `From`, `Billed By`
- Company suffixes like `Pvt Ltd`, `LLP`, `Enterprises`, `Solutions`, `Industries`

---

## 12. Confidence Score Design

### 12.1 Source of Confidence

Use the model probability:

```python
proba = model.predict_proba([line])
confidence = max(proba[0])
```

### 12.2 Confidence Thresholds

| Confidence | Status |
|---:|---|
| >= 0.80 | Accepted |
| 0.60 to 0.79 | Needs Review |
| < 0.60 | Low Confidence / Manual Check Required |

### 12.3 Field-Level Confidence

If multiple lines are predicted for the same field, choose the line with the highest confidence.

Example:

| Field | Candidate Line | Confidence |
|---|---|---:|
| TOTAL_AMOUNT | Subtotal: ₹40,000 | 0.71 |
| TOTAL_AMOUNT | Grand Total: ₹45,600 | 0.96 |

Choose:

```text
Grand Total: ₹45,600
```

### 12.4 Confidence Display in UI

Use badges:

```text
High Confidence
Review Needed
Low Confidence
```

---

## 13. Human-in-the-Loop Verification

### 13.1 Why Human Verification is Important

Financial data must be accurate. If the system is uncertain, it should not blindly approve the value. Instead, it should send the field for human verification.

### 13.2 Verification Screen

Show editable fields:

```text
Invoice ID:      [INV-1023]
Vendor Name:     [ABC Traders Pvt Ltd]
Invoice Date:    [2026-06-12]
Due Date:        [2026-06-25]
Total Amount:    [45600]
Tax Amount:      [2400]
GSTIN:           [22ABCDE1234F1Z5]
```

Button:

```text
Verify and Save Invoice
```

### 13.3 What to Store After Verification

Store:

- Original extracted value
- Corrected value
- Confidence score
- Verification status
- Timestamp
- Uploaded file name
- Duplicate warning status

This creates a useful audit trail.

---

## 14. Data Canonicalization

Canonicalization means converting extracted values into a standard format.

### 14.1 Date Standardization

| Raw Date | Standard Date |
|---|---|
| 12/06/26 | 2026-06-12 |
| 12 June 2026 | 2026-06-12 |
| Jun 12, 2026 | 2026-06-12 |
| 2026/06/12 | 2026-06-12 |

Standard format:

```text
YYYY-MM-DD
```

### 14.2 Currency Standardization

| Raw Value | Standard Value |
|---|---|
| ₹45,600 | INR 45600 |
| Rs. 45,600.00 | INR 45600.00 |
| INR 45,600 | INR 45600 |

### 14.3 Vendor Standardization

| Raw Vendor Name | Canonical Vendor ID |
|---|---|
| ABC Traders Pvt Ltd | VENDOR_ABC_TRADERS |
| ABC Traders Pvt. Limited | VENDOR_ABC_TRADERS |
| A.B.C. Traders | VENDOR_ABC_TRADERS |

For MVP, use simple normalization:

```text
uppercase
remove dots
remove extra spaces
replace common suffix variations
```

### 14.4 Amount Standardization

Convert:

```text
Rs. 45,600.00
```

To:

```json
{
  "currency": "INR",
  "amount": 45600.00
}
```

---

## 15. Duplicate Invoice Detection

### 15.1 Why It Matters

Duplicate invoice payments are one of the major AP risks. If the same invoice is processed twice, the company may pay the vendor twice.

### 15.2 Basic MVP Logic

Flag duplicate if:

```text
same vendor + same invoice id
```

Better duplicate check:

```text
same vendor + same invoice id + same total amount
```

### 15.3 Similarity-Based Duplicate Detection

Optional improvement:

Use TF-IDF similarity between current invoice text and previous invoice text.

If similarity > 90%, show:

```text
Possible duplicate invoice detected.
```

### 15.4 UI Warning

Display:

```text
⚠ Possible Duplicate Invoice
This invoice has similar vendor, invoice number, and amount as a previously processed invoice.
```

---

## 16. MVP Features

### 16.1 Must-Have Features

| Feature | Description |
|---|---|
| Invoice upload | Upload PDF/image invoice |
| OCR/PDF extraction | Extract raw text |
| ML line classifier | Classify invoice lines using trained model |
| Field extraction | Extract exact invoice values |
| Confidence score | Show prediction confidence |
| Human verification | Allow manual correction |
| Canonicalization | Standardize date, amount, currency, vendor |
| Export | Download JSON/CSV |
| History | View processed invoices |

### 16.2 Should-Have Features

| Feature | Description |
|---|---|
| Duplicate detection | Warn if invoice already exists |
| Dashboard cards | Show counts and summary |
| Model performance page | Show accuracy, F1-score, confusion matrix |
| Raw text preview | Show OCR output |
| Field status badges | Accepted / Review Needed |

### 16.3 Good-to-Have Features

| Feature | Description |
|---|---|
| Email invoice ingestion | Read invoice text from email body |
| Line item extraction | Extract product/service table |
| Vendor master database | Map vendors to standard IDs |
| Approval workflow | Pending → Verified → Approved |
| Role-based login | AP user/admin/verifier |
| React frontend | More production-like UI |

---

## 17. Minimalist Professional UI Design

### 17.1 UI Style

Use a clean, modern business dashboard style.

Recommended theme:

```text
Background: light gray / off-white
Primary color: navy blue or deep indigo
Accent color: teal/cyan/emerald
Cards: white with soft shadow
Typography: clean sans-serif
Spacing: generous whitespace
Tables: simple, readable, professional
```

### 17.2 Suggested App Navigation

Use sidebar navigation:

```text
Dashboard
Upload Invoice
Extraction Result
Human Verification
Model Performance
Invoice History
Export Data
```

### 17.3 Dashboard Page

Display cards:

```text
Total Invoices Processed
Verified Invoices
Pending Review
Duplicate Warnings
Average Confidence
Total Invoice Amount
```

Charts:

- Verified vs Pending
- Field confidence distribution
- Invoice amount trend
- Duplicate warning count

### 17.4 Upload Page

Components:

- File uploader
- File type indicator
- Preview section
- Extract text button
- Raw extracted text area

### 17.5 Extraction Result Page

Table:

| Field | Extracted Value | Confidence | Status |
|---|---|---:|---|
| Invoice ID | INV-1023 | 96% | Accepted |
| Vendor | ABC Traders Pvt Ltd | 88% | Accepted |
| Invoice Date | 2026-06-12 | 91% | Accepted |
| Due Date | 2026-06-25 | 62% | Review Needed |
| Total Amount | INR 45600 | 95% | Accepted |

### 17.6 Human Verification Page

Use editable form fields:

```text
Invoice ID
Vendor Name
Invoice Date
Due Date
Total Amount
Tax Amount
GSTIN
```

Buttons:

```text
Verify and Save
Reset Values
Export JSON
Export CSV
```

### 17.7 Model Performance Page

Show:

- Model name
- Dataset size
- Labels/classes
- Train-test split
- Accuracy
- Precision/Recall/F1-score
- Confusion matrix
- Sample predictions

This page is very important for professor evaluation.

---

## 18. Database / Storage Design

### 18.1 Simple SQLite Tables

#### invoices table

| Column | Type |
|---|---|
| id | INTEGER PRIMARY KEY |
| invoice_id | TEXT |
| vendor_name | TEXT |
| canonical_vendor_id | TEXT |
| invoice_date | TEXT |
| due_date | TEXT |
| total_amount | REAL |
| tax_amount | REAL |
| currency | TEXT |
| gstin | TEXT |
| status | TEXT |
| duplicate_flag | INTEGER |
| average_confidence | REAL |
| created_at | TEXT |

#### invoice_fields table

| Column | Type |
|---|---|
| id | INTEGER PRIMARY KEY |
| invoice_record_id | INTEGER |
| field_name | TEXT |
| raw_value | TEXT |
| corrected_value | TEXT |
| confidence | REAL |
| status | TEXT |

#### audit_log table

| Column | Type |
|---|---|
| id | INTEGER PRIMARY KEY |
| invoice_record_id | INTEGER |
| action | TEXT |
| old_value | TEXT |
| new_value | TEXT |
| timestamp | TEXT |

### 18.2 Simpler MVP Alternative

If SQLite feels too much, save records in:

```text
data/processed_invoices.csv
```

But SQLite looks more professional.

---

## 19. Project Folder Structure

Recommended structure:

```text
invoice-automation-system/
│
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── raw_invoices/
│   ├── processed/
│   ├── labelled_lines.csv
│   └── sample_outputs/
│
├── models/
│   ├── invoice_line_classifier.joblib
│   └── label_encoder.joblib
│
├── notebooks/
│   ├── 01_dataset_preparation.ipynb
│   ├── 02_model_training.ipynb
│   └── 03_model_evaluation.ipynb
│
├── src/
│   ├── text_extraction.py
│   ├── preprocessing.py
│   ├── model_training.py
│   ├── prediction.py
│   ├── field_extraction.py
│   ├── canonicalization.py
│   ├── duplicate_detection.py
│   ├── database.py
│   └── export_utils.py
│
├── reports/
│   ├── figures/
│   ├── confusion_matrix.png
│   └── model_metrics.json
│
└── demo_samples/
    ├── invoice_1.pdf
    ├── invoice_2.png
    └── invoice_3.pdf
```

---

## 20. Step-by-Step Implementation Plan

## Phase 0: Setup

### Tasks

1. Create project folder.
2. Create virtual environment.
3. Install dependencies.
4. Set up GitHub repository.
5. Create basic README.

### Suggested Dependencies

```txt
streamlit
pandas
numpy
scikit-learn
joblib
pdfplumber
PyMuPDF
pytesseract
Pillow
opencv-python
python-dateutil
dateparser
matplotlib
seaborn
openpyxl
```

Note: If `pytesseract` setup becomes difficult on Windows, use EasyOCR or start with text-based PDFs first.

---

## Phase 1: Dataset Creation

### Tasks

1. Create `labelled_lines.csv`.
2. Add 700–1000 labelled invoice lines.
3. Include variations from different invoice formats.
4. Include Indian invoice terms such as GSTIN, CGST, SGST, IGST, HSN, Tax Invoice.
5. Keep class balance.
6. Clean and validate labels.

### Output

```text
data/labelled_lines.csv
```

---

## Phase 2: Model Training

### Tasks

1. Load labelled dataset.
2. Clean text.
3. Split into train/test sets.
4. Build TF-IDF + Logistic Regression pipeline.
5. Train model.
6. Evaluate accuracy, precision, recall, F1-score.
7. Generate confusion matrix.
8. Save model using joblib.

### Output

```text
models/invoice_line_classifier.joblib
reports/model_metrics.json
reports/confusion_matrix.png
```

---

## Phase 3: Text Extraction Pipeline

### Tasks

1. Implement PDF text extraction using pdfplumber/PyMuPDF.
2. Implement image OCR using Tesseract/EasyOCR.
3. Detect file type.
4. Extract raw text.
5. Clean raw text.
6. Split into lines.

### Output

```text
src/text_extraction.py
src/preprocessing.py
```

---

## Phase 4: Prediction Pipeline

### Tasks

1. Load saved ML model.
2. Pass extracted lines to model.
3. Predict label for every line.
4. Get confidence score using predicted probabilities.
5. Store predictions in dataframe.

### Output Example

| Line | Predicted Label | Confidence |
|---|---|---:|
| Invoice No: INV-1023 | INVOICE_ID | 0.96 |
| Grand Total: ₹45,600 | TOTAL_AMOUNT | 0.94 |

---

## Phase 5: Field Extraction

### Tasks

1. For each label, choose highest-confidence line.
2. Apply regex/value extraction.
3. Extract exact values.
4. Handle missing fields.
5. Handle multiple candidate lines.
6. Create structured dictionary.

### Output Example

```json
{
  "invoice_id": "INV-1023",
  "vendor_name": "ABC Traders Pvt Ltd",
  "invoice_date": "12/06/2026",
  "due_date": "25/06/2026",
  "total_amount": "₹45,600",
  "tax_amount": "₹2,400",
  "gstin": "22ABCDE1234F1Z5"
}
```

---

## Phase 6: Canonicalization

### Tasks

1. Convert dates to `YYYY-MM-DD`.
2. Convert amounts to numeric format.
3. Convert currency to standard code `INR`.
4. Normalize vendor names.
5. Validate GSTIN format.

### Output Example

```json
{
  "invoice_id": "INV-1023",
  "vendor_name": "ABC Traders Pvt Ltd",
  "canonical_vendor_id": "VENDOR_ABC_TRADERS",
  "invoice_date": "2026-06-12",
  "due_date": "2026-06-25",
  "total_amount": 45600.00,
  "tax_amount": 2400.00,
  "currency": "INR",
  "gstin": "22ABCDE1234F1Z5"
}
```

---

## Phase 7: Human Verification UI

### Tasks

1. Show extracted fields in editable form.
2. Mark fields as `Accepted` or `Review Needed`.
3. Allow user correction.
4. Save corrected data.
5. Store both raw and verified values.

### Output

Verified invoice record.

---

## Phase 8: Duplicate Detection

### Tasks

1. Check whether invoice ID already exists for same vendor.
2. Check same vendor + same invoice ID + same amount.
3. Optional: compute text similarity.
4. Show duplicate warning.

### Output

```text
Duplicate Flag: True/False
```

---

## Phase 9: Export and History

### Tasks

1. Save verified invoice in SQLite/CSV.
2. Allow JSON download.
3. Allow CSV download.
4. Show invoice history table.
5. Add filter by status/vendor/date.

---

## Phase 10: Final Polish

### Tasks

1. Improve UI spacing and theme.
2. Add dashboard cards.
3. Add model performance page.
4. Add sample invoices.
5. Add README.
6. Prepare PPT.
7. Prepare project report.
8. Prepare viva answers.
9. Test demo multiple times.

---

## 21. 30-Day Development Roadmap

### Week 1: Dataset and Model Foundation

| Day | Task |
|---|---|
| Day 1 | Finalize scope, create repo, setup environment |
| Day 2 | Create invoice label classes and dataset format |
| Day 3–4 | Prepare 300–500 labelled lines |
| Day 5 | Train first TF-IDF + Logistic Regression model |
| Day 6 | Evaluate model and improve dataset |
| Day 7 | Save model and document metrics |

### Week 2: OCR and Extraction Pipeline

| Day | Task |
|---|---|
| Day 8 | Implement PDF text extraction |
| Day 9 | Implement image OCR |
| Day 10 | Text cleaning and line splitting |
| Day 11 | Load model and classify lines |
| Day 12 | Extract exact values from classified lines |
| Day 13 | Add confidence thresholds |
| Day 14 | Test on 10 invoice samples |

### Week 3: Streamlit UI and Verification

| Day | Task |
|---|---|
| Day 15 | Build Streamlit layout and sidebar |
| Day 16 | Upload page + raw text preview |
| Day 17 | Extraction result table |
| Day 18 | Human verification form |
| Day 19 | Canonicalization module |
| Day 20 | CSV/JSON export |
| Day 21 | Invoice history storage |

### Week 4: Advanced MVP Polish

| Day | Task |
|---|---|
| Day 22 | Duplicate detection |
| Day 23 | Dashboard cards and charts |
| Day 24 | Model performance page |
| Day 25 | Improve UI and error handling |
| Day 26 | Add 20–30 demo invoices |
| Day 27 | Write report and README |
| Day 28 | Prepare PPT |
| Day 29 | Full demo rehearsal |
| Day 30 | Final testing and backup plan |

---

## 22. Edge Cases to Handle

### 22.1 Document-Level Edge Cases

| Edge Case | Handling |
|---|---|
| Text-based PDF | Extract using pdfplumber/PyMuPDF |
| Scanned PDF | Convert page to image and apply OCR |
| Image invoice | Apply OCR directly |
| Blurry image | Show low OCR quality warning |
| Rotated invoice | Optional rotation correction |
| Multi-page invoice | Process first page for MVP, optionally all pages |
| Password-protected PDF | Show unsupported file warning |
| Large file | Show size limit warning |

### 22.2 Extraction Edge Cases

| Edge Case | Handling |
|---|---|
| Missing due date | Mark as missing/review needed |
| Multiple dates | Use ML label to distinguish invoice date vs due date |
| Multiple amounts | Prefer total/grand total/amount due over subtotal |
| Multiple GST values | Extract CGST/SGST/IGST separately if possible |
| Vendor and buyer both present | Prefer top section or `Vendor/Supplier/From` keywords |
| Invoice number without keyword | Mark low confidence |
| OCR mistakes in amount | Clean common OCR errors |
| Currency not found | Default to INR for Indian invoice MVP, but mark assumption |

### 22.3 ML Edge Cases

| Edge Case | Handling |
|---|---|
| Unknown format | Low confidence and human review |
| Class imbalance | Use class_weight='balanced' |
| Similar labels confused | Add more examples for confusing labels |
| Wrong prediction | User correction stored for future dataset improvement |
| Poor OCR text | Show raw text preview and confidence warning |

---

## 23. Why This Project is Good, Efficient, and Better

### 23.1 Good for Jury

This project is strong because:

- It solves a real business problem.
- It has a live demo.
- It clearly uses a trained ML model.
- It combines OCR, NLP, classification, confidence scoring, and automation.
- It produces structured output like JSON/CSV.
- It includes human-in-the-loop verification.
- It has direct practical value in finance and accounting.

### 23.2 Efficient Compared to Manual Processing

Manual processing:

```text
Human opens invoice → reads fields → types into system → checks manually
```

Automated processing:

```text
Upload invoice → system extracts fields → human reviews only uncertain values → export data
```

Benefits:

- Reduces manual typing.
- Speeds up invoice processing.
- Reduces data entry errors.
- Prevents duplicate invoice payments.
- Improves data consistency.
- Creates digital records for audit.

### 23.3 Better than Simple OCR Project

A simple OCR project only extracts text.

This project extracts meaning.

| Simple OCR | Proposed System |
|---|---|
| Reads text only | Understands invoice lines using ML |
| No structured output | Gives JSON/CSV output |
| No confidence score | Shows field confidence |
| No human review | Has human-in-the-loop |
| No duplicate check | Detects possible duplicates |
| No canonicalization | Standardizes dates, amounts, vendors |

### 23.4 Better than Only Regex

Regex depends on fixed patterns. Invoices vary by vendor.

Example same field:

```text
Invoice No
Bill No
Tax Invoice ID
Reference Number
Document Number
```

A line classification model can learn these variations, while regex alone becomes hard to maintain.

---

## 24. Project Challenges

### 24.1 OCR Quality

Poor scan quality, rotation, shadows, or low resolution can reduce OCR accuracy.

Mitigation:

- Show raw OCR text preview.
- Use image preprocessing.
- Allow manual correction.
- Test with clean demo invoices.

### 24.2 Different Invoice Layouts

Every vendor has a different design.

Mitigation:

- Train model on varied invoice lines.
- Use keyword variations.
- Keep human verification for uncertain results.

### 24.3 Vendor Name Extraction

Vendor name may not always have a clear label.

Mitigation:

- Use ML prediction.
- Give priority to top invoice lines.
- Use company suffix rules.
- Allow human correction.

### 24.4 Multiple Amounts

Invoices contain subtotal, tax, shipping, discount, and final total.

Mitigation:

- Use class labels carefully.
- Prefer lines containing `Grand Total`, `Amount Due`, `Total Payable`, `Net Payable`.
- Avoid selecting subtotal as final amount.

### 24.5 Small Dataset

A small dataset may reduce model generalization.

Mitigation:

- Create enough synthetic variations.
- Balance labels.
- Add examples from real-like invoice templates.
- Continuously add corrected lines to dataset.

### 24.6 Overclaiming ML

Do not claim that the system perfectly understands all invoices.

Correct claim:

> The system is an MVP that uses OCR and a supervised ML line classifier to extract important invoice fields from common invoice formats. Low-confidence outputs are flagged for human verification.

---

## 25. Use Cases

### 25.1 Small Business Invoice Entry

A small business receives monthly vendor invoices and wants to digitize them quickly.

### 25.2 College/Department Finance Office

Departments can upload invoices and generate structured records for reports.

### 25.3 Accounting Firms

Accounting firms process invoices for multiple clients and can save time using automation.

### 25.4 Vendor Payment Verification

AP teams can verify vendor invoices before making payments.

### 25.5 Duplicate Payment Prevention

The system can warn users if the same invoice has already been processed.

### 25.6 Audit Preparation

The system keeps structured invoice history, useful for audit and compliance.

---

## 26. Model Performance Page Requirements

Your app must have a page called **Model Performance**.

Show:

```text
Model: TF-IDF + Logistic Regression
Dataset: Custom labelled invoice-line dataset
Classes: 8
Training size: e.g., 800 lines
Train-test split: 80:20
Accuracy: actual value
Precision: actual value
Recall: actual value
F1-score: actual value
```

Also show:

- Confusion matrix
- Sample predictions
- Misclassified examples
- Label distribution chart

This page will protect you when professors ask about ML.

---

## 27. Demo Script for Jury

Use this script during presentation:

1. Start with AP problem.
2. Explain manual invoice processing pain.
3. Show system architecture.
4. Show dataset and ML model.
5. Show model performance page.
6. Upload a sample invoice.
7. Show raw extracted text.
8. Show line classification output.
9. Show extracted fields with confidence score.
10. Show low-confidence field marked for review.
11. Correct one field manually.
12. Click verify.
13. Show canonicalized final output.
14. Export JSON/CSV.
15. Upload same invoice again to show duplicate warning.
16. End with benefits and future scope.

---

## 28. Expected Professor Questions and Answers

### Q1. Where is Machine Learning in this project?

**Answer:**  
The ML part is the supervised invoice-line classification model. It classifies extracted invoice text lines into categories like invoice ID, vendor name, invoice date, due date, total amount, tax amount, GSTIN, and other. I trained it using TF-IDF features and Logistic Regression.

### Q2. Why did you use TF-IDF?

**Answer:**  
TF-IDF converts text into numerical features by giving importance to meaningful words. Since invoice line classification is a text classification problem, TF-IDF is suitable and efficient for this MVP.

### Q3. Why Logistic Regression?

**Answer:**  
Logistic Regression is simple, fast, interpretable, and performs well on text classification tasks with TF-IDF features. It also provides prediction probabilities, which I use as confidence scores.

### Q4. Why not only OCR?

**Answer:**  
OCR only reads text. It does not understand which line contains invoice number, amount, due date, or vendor name. The ML model adds understanding by classifying each invoice line.

### Q5. Why not only regex?

**Answer:**  
Regex works only for fixed formats. Vendors use different invoice templates and different words like Invoice No, Bill No, Tax Invoice ID, or Reference Number. The ML model can learn these variations better than hard-coded rules alone.

### Q6. What happens when the model is wrong?

**Answer:**  
The system uses confidence scoring. If confidence is low, the field is sent for human verification. The user can correct it before final export.

### Q7. What is canonicalization?

**Answer:**  
Canonicalization means standardizing data. For example, all dates are converted to YYYY-MM-DD, currency values are converted to INR numeric format, and vendor names are mapped to consistent IDs.

### Q8. Can this system handle all invoices?

**Answer:**  
This is an MVP designed for common invoice formats. It can handle text PDFs and scanned invoice images. For production, it can be extended with larger datasets, LayoutLM/NER models, ERP integration, and better OCR.

---

## 29. Future Scope

After the MVP, the project can be extended with:

1. Custom NER model using spaCy.
2. Layout-aware models like LayoutLM.
3. Full line-item table extraction.
4. ERP/accounting software integration.
5. Email invoice ingestion.
6. Vendor master database.
7. Role-based approval workflow.
8. GST validation API.
9. Fraud detection.
10. Multi-language invoice support.
11. Cloud deployment.
12. React + FastAPI production version.

---

## 30. Final MVP Scope Checklist

Use this checklist before final submission.

### ML Checklist

- [ ] Custom labelled dataset created
- [ ] TF-IDF + Logistic Regression model trained
- [ ] Model saved using joblib
- [ ] Accuracy/F1-score calculated
- [ ] Confusion matrix generated
- [ ] Model performance page added

### OCR/Extraction Checklist

- [ ] PDF text extraction working
- [ ] Image OCR working
- [ ] Text cleaning working
- [ ] Line splitting working
- [ ] Model prediction working
- [ ] Confidence score working
- [ ] Field extraction working

### Business Feature Checklist

- [ ] Human verification added
- [ ] Date canonicalization added
- [ ] Currency canonicalization added
- [ ] Vendor normalization added
- [ ] Duplicate detection added
- [ ] JSON/CSV export added
- [ ] Invoice history added

### UI Checklist

- [ ] Minimalist dashboard
- [ ] Upload page
- [ ] Raw text preview
- [ ] Extraction result table
- [ ] Verification form
- [ ] Model performance page
- [ ] Export buttons
- [ ] Clean professional layout

### Presentation Checklist

- [ ] Problem clearly explained
- [ ] Architecture diagram included
- [ ] ML model explained
- [ ] Dataset shown
- [ ] Metrics shown
- [ ] Live demo ready
- [ ] Backup screenshots ready
- [ ] PPT ready
- [ ] Report ready

---

## 31. Suggested Final Project Title Options

1. **Smart Invoice Automation System using OCR and Machine Learning**
2. **AI-Powered Invoice Data Extraction and Verification System**
3. **Machine Learning-Based Invoice Processing System for Accounts Payable Automation**
4. **OCR and NLP-Based Invoice Field Extraction System**
5. **Automated Invoice Processing using Supervised Text Classification**

Best title for your presentation:

```text
Smart Invoice Automation System using OCR and Machine Learning
```

---

## 32. Recommended Final Deliverables

At the end of 30 days, submit/present:

1. Working Streamlit app.
2. Trained ML model file.
3. Labelled dataset CSV.
4. Model evaluation report.
5. Sample invoices.
6. JSON/CSV output samples.
7. GitHub repository.
8. Project report.
9. PPT.
10. Demo video or screenshots.

---

## 33. References and Useful Resources

These resources can be used for learning, dataset reference, and implementation support:

1. SROIE / ICDAR 2019 Robust Reading Challenge on Scanned Receipts OCR and Information Extraction  
   https://rrc.cvc.uab.es/?ch=13

2. SROIE dataset paper/report  
   https://arxiv.org/abs/2103.10213

3. CORD dataset GitHub repository  
   https://github.com/clovaai/cord

4. CORD dataset paper page  
   https://openreview.net/forum?id=SJl3z659UH

5. scikit-learn TF-IDF Vectorizer documentation  
   https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html

6. scikit-learn Logistic Regression documentation  
   https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html

7. Streamlit file uploader documentation  
   https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader

8. Streamlit download button documentation  
   https://docs.streamlit.io/develop/api-reference/widgets/st.download_button

---

## 34. Final Recommendation

For a one-month machine learning vocational training project, build the MVP using:

```text
Streamlit + Python + OCR + TF-IDF + Logistic Regression + Human Verification + JSON/CSV Export
```

This is the safest and strongest approach because it is:

- Practical
- ML-focused
- Presentable
- Easy to demonstrate
- Easy to explain to professors
- Achievable in 30 days
- Directly connected to a real AP department problem

Do not overbuild the project. A polished MVP with a clear ML model, confidence score, verification screen, canonicalization, duplicate detection, and export feature will look much better than an incomplete advanced system.
