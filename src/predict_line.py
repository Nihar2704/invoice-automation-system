import os
import sys
import joblib
from preprocessing import clean_text

def predict_line(text: str, model_path: str):
    """
    Cleans the input text line and predicts its category using the trained model.
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}. Please train the model first.")
    
    # Load the trained model pipeline
    pipeline = joblib.load(model_path)
    
    # Clean the input text
    cleaned = clean_text(text)
    
    # Get predictions and probabilities
    pred_label = pipeline.predict([cleaned])[0]
    probabilities = pipeline.predict_proba([cleaned])[0]
    
    # Locate index of predicted class to get confidence
    class_idx = list(pipeline.classes_).index(pred_label)
    confidence = probabilities[class_idx]
    
    return cleaned, pred_label, confidence

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base_dir, "models", "invoice_line_classifier.joblib")
    
    # If the user provides a line as a command-line argument
    if len(sys.argv) > 1:
        input_text = " ".join(sys.argv[1:])
        try:
            cleaned, label, conf = predict_line(input_text, model_path)
            print("\nPrediction Result:")
            print("-" * 40)
            print(f"Original:   {input_text}")
            print(f"Cleaned:    {cleaned}")
            print(f"Prediction: {label}")
            print(f"Confidence: {conf:.2%}")
            print("-" * 40)
        except Exception as e:
            print(f"Error: {e}")
    else:
        # Default test cases
        test_samples = [
            "Tax Invoice No: GST-9987",
            "Sahu Furniture And Industries Pvt Ltd",
            "Due Date: 15/07/2026",
            "Total Amount Payable: Rs. 13,600.00",
            "GSTIN: 09ABCDE1234F1Z9",
            "Thank you for business with us"
        ]
        
        print("\nRunning predictions on sample lines:")
        print("=" * 60)
        for sample in test_samples:
            try:
                cleaned, label, conf = predict_line(sample, model_path)
                print(f"Text:       \"{sample}\"")
                print(f"Prediction: {label} (Confidence: {conf:.2%})")
                print("-" * 60)
            except Exception as e:
                print(f"Error for sample '{sample}': {e}")
        
        print("\nYou can also test custom text lines by running:")
        print("  .venv\\Scripts\\python.exe src/predict_line.py \"YOUR INVOICE LINE HERE\"")
