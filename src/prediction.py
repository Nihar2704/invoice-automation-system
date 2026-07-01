import os
import joblib
import pandas as pd
import numpy as np

# Import custom processing modules
from text_extraction import extract_raw_text, split_and_clean_lines
from field_extraction import (
    extract_gstin, extract_date, extract_amount,
    extract_invoice_id, extract_vendor_name
)
from canonicalization import (
    canonicalize_date, canonicalize_amount,
    canonicalize_vendor, canonicalize_gstin, detect_currency
)

class InvoiceParserPipeline:
    def __init__(self, model_path: str = None):
        if model_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, "models", "invoice_line_classifier.joblib")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}. Please train the model first.")
            
        print(f"Loading line classification model from {model_path}...")
        self.pipeline = joblib.load(model_path)
        self.classes = list(self.pipeline.classes_)

    def get_confidence_status(self, confidence: float) -> str:
        """
        Determines the review status of a field based on confidence thresholds.
        """
        if confidence >= 0.80:
            return "Accepted"
        elif confidence >= 0.60:
            return "Review Needed"
        else:
            return "Low Confidence"

    def process_invoice(self, filepath: str) -> dict:
        """
        Processes an invoice file through text extraction, ML classification,
        value extraction, and canonicalization.
        """
        # 1. Text Extraction and Line Splitting
        raw_text = extract_raw_text(filepath)
        line_pairs = split_and_clean_lines(raw_text)
        
        if not line_pairs:
            return {
                "error": "No text could be extracted from the document.",
                "status": "Failed"
            }
            
        # 2. ML Classification
        cleaned_lines = [pair[1] for pair in line_pairs]
        predictions = self.pipeline.predict(cleaned_lines)
        probabilities = self.pipeline.predict_proba(cleaned_lines)
        
        # 3. Store All Predictions for Debug/Raw View
        all_predictions = []
        for i, (raw, clean) in enumerate(line_pairs):
            label = predictions[i]
            class_idx = self.classes.index(label)
            conf = probabilities[i][class_idx]
            
            all_predictions.append({
                "line_no": i + 1,
                "raw_text": raw,
                "cleaned_text": clean,
                "predicted_label": label,
                "confidence": float(conf)
            })
            
        # Group candidate lines by predicted label
        candidates = {label: [] for label in self.classes}
        for pred in all_predictions:
            candidates[pred["predicted_label"]].append(pred)
            
        # Sort candidates of each class by confidence (descending)
        for label in candidates:
            candidates[label] = sorted(candidates[label], key=lambda x: x["confidence"], reverse=True)
            
        # 4. Field Extraction Rules
        extracted_fields = {
            "invoice_id": None,
            "vendor_name": None,
            "invoice_date": None,
            "due_date": None,
            "total_amount": None,
            "tax_amount": None,
            "gstin": None
        }
        
        field_metadata = {}
        
        # Define extraction functions and standardizers for each target field
        extraction_mapping = {
            "INVOICE_ID": (extract_invoice_id, lambda x: x, "invoice_id"),
            "VENDOR_NAME": (extract_vendor_name, lambda x: canonicalize_vendor(x)[0], "vendor_name"),
            "INVOICE_DATE": (extract_date, canonicalize_date, "invoice_date"),
            "DUE_DATE": (extract_date, canonicalize_date, "due_date"),
            "TOTAL_AMOUNT": (extract_amount, lambda x: canonicalize_amount(x), "total_amount"),
            "TAX_AMOUNT": (extract_amount, lambda x: canonicalize_amount(x), "tax_amount"),
            "GSTIN": (extract_gstin, canonicalize_gstin, "gstin")
        }
        
        for label, (extractor, standardizer, field_key) in extraction_mapping.items():
            value = ""
            best_raw = ""
            best_conf = 0.0
            
            # Iterate through model-predicted candidates
            for cand in candidates.get(label, []):
                raw_line = cand["raw_text"]
                extracted = extractor(raw_line)
                if extracted:
                    value = standardizer(extracted)
                    best_raw = raw_line
                    best_conf = cand["confidence"]
                    break
            
            # Fallback if no matching regex found on model candidates but candidates exist
            # Useful for unstructured fields like VENDOR_NAME or complex INVOICE_ID
            if not value and candidates.get(label):
                best_cand = candidates[label][0]
                best_raw = best_cand["raw_text"]
                best_conf = best_cand["confidence"]
                
                # Apply fallback extraction
                fallback_val = extractor(best_raw)
                if fallback_val:
                    value = standardizer(fallback_val)
                else:
                    # Only default to the raw line text for unstructured text fields
                    if label in ["VENDOR_NAME", "INVOICE_ID"]:
                        value = standardizer(best_raw)
            
            # Store extracted field
            extracted_fields[field_key] = value
            field_metadata[field_key] = {
                "raw_text_source": best_raw,
                "raw_value": extractor(best_raw) if best_raw else "",
                "canonical_value": value,
                "confidence": best_conf,
                "status": self.get_confidence_status(best_conf) if best_conf > 0 else "Low Confidence"
            }
            
        # 5. Resiliency Fallbacks (Scan whole doc if key fields are missing)
        # GSTIN Fallback
        if not extracted_fields["gstin"]:
            for raw, _ in line_pairs:
                val = extract_gstin(raw)
                if val:
                    gst = canonicalize_gstin(val)
                    extracted_fields["gstin"] = gst
                    field_metadata["gstin"] = {
                        "raw_text_source": raw,
                        "raw_value": val,
                        "canonical_value": gst,
                        "confidence": 0.50, # Arbitrary default for non-model matching
                        "status": "Review Needed"
                    }
                    break
                    
        # Date Fallbacks (Check if dates were misclassified or missing)
        # Invoice Date fallback
        if not extracted_fields["invoice_date"]:
            for raw, _ in line_pairs:
                val = extract_date(raw)
                if val and any(k in raw.lower() for k in ["invoice date", "issue", "billing date", "date"]):
                    canon = canonicalize_date(val)
                    extracted_fields["invoice_date"] = canon
                    field_metadata["invoice_date"] = {
                        "raw_text_source": raw,
                        "raw_value": val,
                        "canonical_value": canon,
                        "confidence": 0.50,
                        "status": "Review Needed"
                    }
                    break
                    
        # Due Date fallback
        if not extracted_fields["due_date"]:
            for raw, _ in line_pairs:
                val = extract_date(raw)
                if val and any(k in raw.lower() for k in ["due", "pay before", "last date", "payment date", "terms"]):
                    canon = canonicalize_date(val)
                    extracted_fields["due_date"] = canon
                    field_metadata["due_date"] = {
                        "raw_text_source": raw,
                        "raw_value": val,
                        "canonical_value": canon,
                        "confidence": 0.50,
                        "status": "Review Needed"
                    }
                    break

        # 6. Canonicalize Vendor ID and detect Currency
        vendor_name = extracted_fields["vendor_name"] or ""
        _, canonical_vendor_id = canonicalize_vendor(vendor_name)
        extracted_fields["canonical_vendor_id"] = canonical_vendor_id
        
        # Detect currency from total amount line source
        total_source = field_metadata["total_amount"]["raw_text_source"]
        currency = detect_currency(total_source) if total_source else "INR"
        extracted_fields["currency"] = currency
        
        # 7. Compute Average Confidence
        valid_confidences = [meta["confidence"] for meta in field_metadata.values() if meta["confidence"] > 0]
        avg_conf = float(np.mean(valid_confidences)) if valid_confidences else 0.0
        
        # Build complete response
        result = {
            "file_name": os.path.basename(filepath),
            "extracted_values": extracted_fields,
            "field_metadata": field_metadata,
            "average_confidence": avg_conf,
            "all_predictions": all_predictions,
            "raw_text": raw_text
        }
        
        return result

if __name__ == "__main__":
    # Test script setup
    print("Prediction pipeline loaded.")
