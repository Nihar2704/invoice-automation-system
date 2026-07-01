# Build Prompt: "InvoiceAI Enterprise" Streamlit Application

Use this prompt to have an AI coding assistant (or yourself) build a pixel-close, fully responsive Streamlit clone of the InvoiceAI dashboard shown in the reference screenshots.

---

## 1. Project Brief

Build a multi-page Streamlit web app called **"InvoiceAI — Enterprise Edition"**, an AP (Accounts Payable) automation dashboard that shows invoice OCR/extraction results, a human verification workflow, and ML model performance metrics.

Since native Streamlit widgets are visually limited, use **custom CSS injected via `st.markdown(..., unsafe_allow_html=True)`** to recreate the card-based, dark-sidebar SaaS look shown in the screenshots. Use `st.columns`, `st.container(border=True)`, and HTML/CSS "cards" together — don't rely on default Streamlit styling.

---

## 2. Design System

**Layout**
- `st.set_page_config(layout="wide", page_title="InvoiceAI", page_icon="🧾")`
- Fixed dark sidebar (left) + light content area (right), matching a modern SaaS admin panel.
- Global rounded-corner cards (`border-radius: 16px`), soft drop shadows (`box-shadow: 0 1px 3px rgba(0,0,0,0.08)`), generous white space.

**Color palette**
| Token | Hex | Usage |
|---|---|---|
| `--bg-sidebar` | `#12142B` | Sidebar background (near-black navy) |
| `--bg-app` | `#F4F5FA` | Main content background |
| `--accent-primary` | `#5B5FEF` | Buttons, active nav item, links, chart lines |
| `--accent-primary-dark` | `#12142B` | Dark CTA buttons (e.g. "Verify and Save" alt state, "Retrain Model") |
| `--success` | `#22C55E` / bg `#DCFCE7` | Verified, high confidence, positive trend |
| `--warning` | `#F59E0B` / bg `#FEF3C7` | Pending, medium confidence, review needed |
| `--danger` | `#EF4444` / bg `#FEE2E2` | Critical, duplicates, low confidence |
| `--text-primary` | `#0F1222` | Headings |
| `--text-secondary` | `#6B7280` | Labels, captions |
| `--border` | `#E5E7EB` | Card borders, table dividers |

**Typography**
- Font family: `Inter, "Segoe UI", sans-serif` (import from Google Fonts via CSS `@import`).
- Page titles: `28px / 700 weight`.
- Card metric numbers: `32–40px / 800 weight`.
- Labels/eyebrows: `11–12px / 600 weight / uppercase / letter-spacing: 0.05em / --text-secondary`.

**Components to standardize as reusable CSS classes / Python helper functions**
- `.metric-card` — white card with icon chip top-left, colored status pill top-right, big number, label underneath.
- `.status-pill` — rounded-full badge, colored per status (success/warning/danger).
- `.confidence-badge` — small dot + percentage text, colored by confidence tier.
- `.sidebar-nav-item` — icon + label, active state = filled indigo rounded rect with white text; inactive = muted gray-white icon+label.
- `.section-card` — generic white rounded container used for charts, tables, forms.

---

## 3. Global Shell (applies to every page)

**Sidebar (`st.sidebar`, styled dark via CSS)**
- Logo block: small indigo rounded-square icon + "InvoiceAI" (bold, white) + "ENTERPRISE EDITION" (small, muted, letter-spaced) underneath.
- Nav items (icon + label), in order: Dashboard, Upload & Process, Human Verification, Invoice History, Model Performance, Settings. Highlight the current page with the indigo active-pill style.
- Bottom of sidebar: user mini-profile (avatar, name, role e.g. "Senior AP Manager") + a "Quick Upload" primary button (indigo, full width, rounded, with a "+" icon). On the Human Verification page this bottom block also shows a "Sign Out" outlined button.

**Top header bar (every page)**
- Left: either a page title (Dashboard) OR a search input ("Search invoices, batches, or vendors…") OR a breadcrumb (e.g. "VERIFICATION QUEUE › INV-8842-X").
- Right: notification bell (with red dot badge when active), help "?" icon, and a user chip (name + role + circular avatar photo).
- On Dashboard, also include a date-range pill selector (e.g. "📅 Aug 1, 2024 – Aug 31, 2024").
- On Upload & Process, include an "Export Template" outlined button top-right.
- On Model Performance, include "Export Report" (outlined) and "Retrain Model" (solid dark, with refresh icon) buttons top-right, plus a "PRODUCTION v4.2" badge and pipeline label ("Pipeline: TF-IDF + Logistic Regression").

---

## 4. Page-by-Page Specification

### Page 1 — Dashboard ("AP Manager Overview")
1. **KPI row** — 4 metric cards in a row (`st.columns(4)`):
   - Total Invoices Processed: `1,248`, green "↗ 12%" trend pill, document icon.
   - Pending Review: `42`, amber "Review Needed" pill, clipboard icon.
   - Possible Duplicates: `7`, red "Critical" pill, duplicate-file icon.
   - Avg. OCR Confidence: `94.2%`, small green bar-signal icon (no trend pill).
2. **Two-column row** (`st.columns([2,1])`):
   - Left (wide): "Invoice Processing Trends" card — combo chart (bar = volume, smooth line = processing time) over "Last 30 Days", with "Export CSV" (outlined) and "View Details" (solid dark) buttons in the card header. Build with **Plotly** (`go.Bar` + `go.Scatter` with `line_shape="spline"`) styled in indigo/lavender tones, no gridlines, minimal axes.
   - Right (narrow): "Field Distribution" card — a donut/gauge chart showing "88% RELIABILITY" in the center (green arc), with a legend below listing High Confidence 72% (green dot), Medium/Review 21% (amber dot), Low/Manual 7% (red dot). Build with Plotly `go.Pie(hole=0.75)` or `go.Indicator` gauge.
3. **Recent Activity table** — full-width card, header with title + subtitle + "View All Invoices" link (top-right). Table columns: Vendor (avatar-style 2-letter initials chip + name), Date, Amount, Confidence (colored pill %), Status (colored pill: VERIFIED=green, PENDING=amber). Render as styled HTML table or `st.dataframe` with custom cell formatting/pandas Styler.

### Page 2 — Upload & Process
1. **Main drag-and-drop zone** (large dashed-border card, centered content): upload icon in a light circle, "Drag & Drop Invoices" heading, helper text ("Supported formats: PDF, JPEG, PNG. Up to 50MB per file. AI will automatically detect vendor and extract line items."), and a solid indigo "Browse Files" button. Wire to `st.file_uploader` (hide default widget chrome via CSS, or overlay a styled button).
2. **Selected Files list card** below the dropzone: header "Selected Files (3)" + "STATUS" label. Each row: file-type icon (PDF=red, image=blue), filename, a horizontal progress bar (indigo, showing e.g. 85%), and a status label ("85%", "Ready" in green, "Queued" in gray) with an "✕" remove icon. Use `st.progress` per row or custom CSS progress bars for finer color control.
3. **Right sidebar column**:
   - Dark "ML Intelligence" card (matches sidebar dark navy): short description text ("Ready to analyze 3 documents. This will utilize the NeuralV3 extraction model with 99.4% historical accuracy."), and a white pill button "✨ Run ML Extraction".
   - "Processing Options" white card: two checkboxes ("Auto-validate amounts" — sub-label "Cross-check with PO numbers"; "Notify on completion" — sub-label "Send email summary to AP Team"), and a "Model Sensitivity" labeled range slider between "FAST" and "ACCURATE" endpoints (`st.slider` restyled indigo).
4. **Collapsible "Raw Text Preview (OCR Output)" bar** at the bottom, full width, with a "READ-ONLY" tag and a chevron to expand/collapse (`st.expander`).
5. Footer: small copyright text left ("© 2024 InvoiceAI Processing Terminal. All data encrypted via AES-256.") and links right ("API Docs · System Status · Contact Support").

### Page 3 — Human Verification
1. **Alert banner** at top, full width, amber background: warning icon + "Possible Duplicate Detected: An invoice with the same Vendor and Amount was processed 3 days ago." + right-aligned "View Match" link.
2. **Two-column split** (`st.columns([1,1])`, roughly equal):
   - **Left: Document preview card** — renders the invoice image/PDF (`st.image`), with a floating zoom/rotate/fullscreen toolbar (zoom in, zoom out, rotate, expand icons) centered below the document.
   - **Right: "Extraction Review" form card** — subtitle ("Confirm the AI-extracted fields before finalizing the invoice for processing."), then labeled inputs each with a small confidence indicator (colored dot + %) top-right of the label:
     - Invoice ID (96% confidence, green) — text input with an edit-pencil icon.
     - Vendor Name (88% confidence, green) — text input.
     - Invoice Date (91%) and Due Date (62%, amber-highlighted border + helper text "Needs verification from document") — two date inputs side by side.
     - Total Amount (95%, `$` prefix) and GSTIN/Tax ID (98%) — two inputs side by side.
     - Primary button: solid indigo, full width, "✓ Verify and Save".
     - Secondary row: two outlined buttons side by side — "Mark as Duplicate" and "Flag for Manager".
     - Keyboard-shortcut hints small and muted at the very bottom: "⌘+S SAVE · ⌘+F FLAG · ESC CLOSE".

### Page 4 — Model Performance
1. **Header row**: title "Model Performance", a "PRODUCTION v4.2" badge pill + "Pipeline: TF-IDF + Logistic Regression" caption, and top-right "Export Report" / "Retrain Model" buttons (as described in section 3).
2. **Metric row** (`st.columns(4)`): Accuracy `92%` (↑1.2% green), F1-Score `0.89` (—0% neutral gray), Precision `0.91` (↑0.4% green), Recall `0.88` (↓0.2% red) — each card also has a one-line descriptive caption underneath the number.
3. **Two-column row**:
   - Left (wide): "Confusion Matrix" card — 8x8 heatmap table (columns/rows: VEN, INV, DAT, TOT, TAX, CUR, ADD, TRM), diagonal cells shown as solid indigo filled squares with white % text (true positives), off-diagonal cells light gray/lavender with small dark text. Legend top-right ("High Accuracy" solid dot / "Low Accuracy" light dot). Caption below: "Normalized accuracy scores across 8 semantic entity classes. Diagonal represent true positives." Build with Plotly `go.Heatmap` + text annotations, or a styled `st.dataframe`/HTML table.
   - Right (narrow): "Label Distribution" card — subtitle ("Balance of the 1,000 labelled lines in training set."), then a horizontal bar-per-label list (VENDOR_NAME 180, INVOICE_ID 150, DATE 120, TOTAL_AMOUNT 210, TAX_AMOUNT 90, CURRENCY 100, ADDRESS 80, TERMS 70) each rendered as a label + count + thin horizontal progress bar. Below that, a green-tinted info callout box with a checkmark/info icon: "Distribution is healthy. We suggest adding **50 more samples** for 'TERMS' to improve recall on complex payment clauses."
4. **"Sample Predictions" section** below (partially visible in reference — implement as a simple additional card/table showing a few sample extraction predictions vs. ground truth, since it's cut off in the source design; use your best judgment for columns like Field, Predicted, Actual, Match).

---

## 5. Responsiveness Requirements

Streamlit's default column layout does **not** reflow well on narrow viewports, so add explicit responsive CSS:

1. Always call `st.set_page_config(layout="wide")`.
2. Inject a global `<style>` block with **CSS Grid/Flexbox + media queries**, e.g.:
   ```css
   /* Stack KPI cards from 4-across to 2-across to 1-across */
   .kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
   @media (max-width: 1200px) { .kpi-row { grid-template-columns: repeat(2, 1fr); } }
   @media (max-width: 640px)  { .kpi-row { grid-template-columns: 1fr; } }
   ```
   Apply the same pattern to the two-column dashboard/model-performance rows (`grid-template-columns: 2fr 1fr` → `1fr` under ~900px) and to the verification split-view (`1fr 1fr` → `1fr` under ~900px, with the document preview stacking above the form).
3. Since Streamlit's `st.columns()` ratios are fixed and don't naturally collapse, prefer **rendering card groups as raw HTML/CSS grids inside a single `st.markdown` block** for anything that needs true reflow (KPI rows, confusion matrix + distribution panel). Reserve `st.columns()` for structural layout where a simple 1-column mobile fallback is acceptable (e.g. detect narrow viewport isn't natively possible in Streamlit, so default to letting CSS grid handle the reflow instead of Python-side breakpoint logic).
4. Make the sidebar collapsible — Streamlit's built-in sidebar already collapses to an icon/drawer on small screens; don't fight this behavior, just ensure sidebar CSS (dark background, nav item styling) still applies when collapsed/expanded.
5. Set a `max-width` and `overflow-x: auto` on wide elements like the confusion-matrix table so it scrolls horizontally on mobile instead of breaking layout.
6. Use relative units (`rem`, `%`, `minmax()` in grid tracks) rather than fixed pixel widths for card containers.
7. Test at three breakpoints: **desktop (≥1200px)**, **tablet (768–1199px)**, **mobile (≤767px)** — confirm KPI cards, the two-column rows, and the verification split view all stack cleanly to single-column at the mobile breakpoint.

---

## 6. Suggested Tech Stack & File Structure

- `streamlit`, `plotly`, `pandas`
- `app.py` — page config, shared CSS injection, sidebar nav, router (`st.session_state["page"]` or `st.navigation`/multipage `pages/` folder).
- `pages/1_Dashboard.py`, `pages/2_Upload_Process.py`, `pages/3_Human_Verification.py`, `pages/4_Model_Performance.py`
- `assets/styles.css` — all custom CSS (loaded once via `st.markdown(f"<style>{open('assets/styles.css').read()}</style>", unsafe_allow_html=True)`)
- `components.py` — reusable Python helpers: `metric_card()`, `status_pill()`, `confidence_badge()`, `section_card()` that return/render styled HTML.
- Use `st.session_state` to persist mock data (uploaded files list, invoice queue, verification form values) across the multipage app so the demo feels stateful.

Use realistic mock/sample data matching the numbers above so the built app visually matches the reference screenshots on first load.
