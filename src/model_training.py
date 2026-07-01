import os
import json
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.pipeline import FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

# Import local text cleaning utility
from preprocessing import clean_text

def load_and_preprocess_data(filepath: str):
    """
    Loads dataset from filepath, handles missing values, and cleans text.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset file not found at {filepath}")
    
    # Load dataset
    df = pd.read_csv(filepath)
    
    # Check required columns
    if 'text' not in df.columns or 'label' not in df.columns:
        raise ValueError("Dataset CSV must contain 'text' and 'label' columns.")
    
    # Drop rows with missing values in text or label
    df = df.dropna(subset=['text', 'label'])
    
    # Apply text cleaning (includes digit normalization to 0)
    df['cleaned_text'] = df['text'].apply(clean_text)
    
    # Filter out empty texts after cleaning
    df = df[df['cleaned_text'].str.strip() != ""]
    
    return df

def train_and_evaluate_optimized(data_path: str, model_save_path: str, metrics_save_path: str, plot_save_path: str):
    """
    Optimized training and evaluation pipeline with FeatureUnion and Grid Search.
    """
    print("Loading and preprocessing data...")
    df = load_and_preprocess_data(data_path)
    
    print(f"Dataset summary: {len(df)} total rows.")
    
    # Split features and target
    X = df['cleaned_text']
    y = df['label']
    
    # Train-test split (stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples.")
    
    # Define Feature Union for Word and Character N-grams
    features = FeatureUnion([
        ('word_tfidf', TfidfVectorizer(
            analyzer='word',
            lowercase=True,
            ngram_range=(1, 2),
            max_features=3000
        )),
        ('char_tfidf', TfidfVectorizer(
            analyzer='char_wb',
            lowercase=True,
            ngram_range=(3, 5),
            max_features=3000
        ))
    ])
    
    # Define overall Pipeline
    pipeline = Pipeline([
        ('features', features),
        ('clf', LogisticRegression(
            max_iter=1000,
            class_weight='balanced',
            random_state=42
        ))
    ])
    
    # Define parameter grid for GridSearchCV
    param_grid = {
        'clf__C': [0.1, 1.0, 10.0, 100.0]
    }
    
    print("Running Grid Search to find optimal hyperparameters...")
    grid_search = GridSearchCV(
        pipeline,
        param_grid=param_grid,
        cv=5,
        scoring='f1_macro',
        n_jobs=-1
    )
    
    grid_search.fit(X_train, y_train)
    
    print(f"Best hyperparameters found: {grid_search.best_params_}")
    best_model = grid_search.best_estimator_
    
    # Predict on test set
    y_pred = best_model.predict(X_test)
    
    # Calculate overall metrics
    accuracy = accuracy_score(y_test, y_pred)
    report_dict = classification_report(y_test, y_pred, output_dict=True)
    report_text = classification_report(y_test, y_pred)
    
    print("\nOptimized Model Evaluation Results:")
    print("-" * 50)
    print(report_text)
    print("-" * 50)
    print(f"Overall Accuracy: {accuracy:.4f}")
    
    # Save optimized model pipeline
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    joblib.dump(best_model, model_save_path)
    print(f"Saved optimized model pipeline to {model_save_path}")
    
    # Save metrics JSON
    os.makedirs(os.path.dirname(metrics_save_path), exist_ok=True)
    metrics = {
        "overall_accuracy": accuracy,
        "best_params": grid_search.best_params_,
        "classification_report": report_dict,
        "class_distribution": df['label'].value_counts().to_dict()
    }
    with open(metrics_save_path, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=4)
    print(f"Saved model metrics to {metrics_save_path}")
    
    # Generate and save Confusion Matrix plot
    print("Generating Confusion Matrix plot...")
    labels = sorted(df['label'].unique())
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', xticklabels=labels, yticklabels=labels, cmap='Blues')
    plt.title('Optimized Invoice Line Classifier Confusion Matrix')
    plt.ylabel('Actual Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(plot_save_path), exist_ok=True)
    plt.savefig(plot_save_path, dpi=300)
    plt.close()
    print(f"Saved confusion matrix plot to {plot_save_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "labelled_lines.csv")
    model_save_path = os.path.join(base_dir, "models", "invoice_line_classifier.joblib")
    metrics_save_path = os.path.join(base_dir, "reports", "model_metrics.json")
    plot_save_path = os.path.join(base_dir, "reports", "confusion_matrix.png")
    
    train_and_evaluate_optimized(data_path, model_save_path, metrics_save_path, plot_save_path)
