import os
import re
import json
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

from config import Config

def clean_text(text):
    """Clean text by lowercasing and stripping redundant whitespace."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def train_and_evaluate():
    print("=" * 60)
    print(" TRUTHLENS AI - MACHINE LEARNING MODEL TRAINING ")
    print("=" * 60)

    # 1. Ensure directories exist
    os.makedirs(Config.MODEL_DIR, exist_ok=True)

    # 2. Check dataset existence
    if not os.path.exists(Config.DATASET_PATH):
        raise FileNotFoundError(f"Dataset file not found at: {Config.DATASET_PATH}")

    print(f"[1/6] Loading dataset from: {Config.DATASET_PATH}")
    df = pd.read_csv(Config.DATASET_PATH)

    # 3. Combine Title and Text columns if present
    if 'title' in df.columns and 'text' in df.columns:
        df['combined_text'] = df['title'].fillna('') + " " + df['text'].fillna('')
    elif 'text' in df.columns:
        df['combined_text'] = df['text'].fillna('')
    elif 'title' in df.columns:
        df['combined_text'] = df['title'].fillna('')
    else:
        raise ValueError("Dataset must contain either 'text' or 'title' columns.")

    # 4. Normalize Labels
    if 'label' not in df.columns:
        raise ValueError("Dataset missing 'label' column.")

    df['label'] = df['label'].astype(str).str.strip().str.upper()
    # Standardize label names (0 -> FAKE, 1 -> REAL if numeric)
    df['label'] = df['label'].replace({'0': 'FAKE', '1': 'REAL', 'FALSE': 'FAKE', 'TRUE': 'REAL'})

    # Filter out invalid labels
    df = df[df['label'].isin(['FAKE', 'REAL'])].copy()
    print(f"      Dataset successfully loaded. Total samples: {len(df)}")
    print(f"      Label Breakdown -> FAKE: {(df['label'] == 'FAKE').sum()}, REAL: {(df['label'] == 'REAL').sum()}")

    # 5. Clean text
    print("[2/6] Preprocessing and cleaning news text...")
    df['cleaned_text'] = df['combined_text'].apply(clean_text)

    # Filter out empty texts
    df = df[df['cleaned_text'].str.len() > 5].copy()

    X = df['cleaned_text']
    y = df['label']

    # 6. Train/Test Split (stratified)
    print("[3/6] Splitting data into Training (80%) and Test (20%) sets...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # 7. TF-IDF Vectorization
    print("[4/6] Extracting TF-IDF features...")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        sublinear_tf=True
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    # 8. Model Benchmarking & Selection
    print("[5/6] Benchmarking Candidate Machine Learning Classifiers...")
    candidate_models = {
        'Logistic Regression': LogisticRegression(C=1.0, max_iter=1000, random_state=42),
        'Multinomial Naive Bayes': MultinomialNB(alpha=0.5),
        'Linear SVM': LinearSVC(C=1.0, random_state=42)
    }

    comparison_results = {}
    best_model_name = None
    best_f1 = -1.0
    best_model = None

    for name, model in candidate_models.items():
        model.fit(X_train_tfidf, y_train)
        y_pred = model.predict(X_test_tfidf)

        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, pos_label='REAL', zero_division=0))
        rec = float(recall_score(y_test, y_pred, pos_label='REAL', zero_division=0))
        f1 = float(f1_score(y_test, y_pred, pos_label='REAL', zero_division=0))

        comparison_results[name] = {
            'accuracy': round(acc * 100, 2),
            'precision': round(prec * 100, 2),
            'recall': round(rec * 100, 2),
            'f1_score': round(f1 * 100, 2)
        }

        print(f"      - {name:<24} | Accuracy: {acc*100:6.2f}% | F1-Score: {f1*100:6.2f}%")

        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_model = model

    print(f"\n      [*] Selected Best Model: {best_model_name} (F1-Score: {best_f1*100:.2f}%)")

    # Evaluate Best Model fully
    y_best_pred = best_model.predict(X_test_tfidf)
    acc = accuracy_score(y_test, y_best_pred)
    prec = precision_score(y_test, y_best_pred, pos_label='REAL', zero_division=0)
    rec = recall_score(y_test, y_best_pred, pos_label='REAL', zero_division=0)
    f1 = f1_score(y_test, y_best_pred, pos_label='REAL', zero_division=0)

    cm = confusion_matrix(y_test, y_best_pred, labels=['FAKE', 'REAL']).tolist()

    metrics_payload = {
        'model_name': best_model_name,
        'accuracy': round(acc * 100, 2),
        'precision': round(prec * 100, 2),
        'recall': round(rec * 100, 2),
        'f1_score': round(f1 * 100, 2),
        'confusion_matrix': cm,
        'total_samples': len(df),
        'train_samples': len(X_train),
        'test_samples': len(X_test),
        'comparison': comparison_results
    }

    # 9. Save Artifacts
    print("[6/6] Saving trained model, vectorizer, and metrics payload...")
    joblib.dump(best_model, Config.MODEL_PATH)
    joblib.dump(vectorizer, Config.VECTORIZER_PATH)

    with open(Config.METRICS_PATH, 'w') as f:
        json.dump(metrics_payload, f, indent=4)

    print(f"      [+] Model saved to: {Config.MODEL_PATH}")
    print(f"      [+] Vectorizer saved to: {Config.VECTORIZER_PATH}")
    print(f"      [+] Metrics saved to: {Config.METRICS_PATH}")
    print("=" * 60)
    print(" MODEL TRAINING COMPLETED SUCCESSFULLY! ")
    print("=" * 60)

if __name__ == '__main__':
    train_and_evaluate()
