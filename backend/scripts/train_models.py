import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import joblib

sys.path.append(str(Path(__file__).resolve().parent.parent))
from app.ml.feature_engineering import extract_features, get_feature_names
from app.ml.anomaly_detector import AnomalyDetector
from app.ml.classifier import AnomalyClassifier
from app.ml.cold_start import ColdStartHandler
from app.core.config import settings

def main():
    os.makedirs(settings.MODELS_DIR, exist_ok=True)

    train_path = os.path.join(settings.GENERATED_DIR, 'events_train.csv')
    test_path  = os.path.join(settings.GENERATED_DIR, 'events_test.csv')
    labels_test_path = os.path.join(settings.GENERATED_DIR, 'labels_test.csv')

    print("Loading data...")
    train_df = pd.read_csv(train_path)
    test_df  = pd.read_csv(test_path)
    test_labels = pd.read_csv(labels_test_path)
    test_df['label'] = test_labels['label'].values

    # ── Add label as passthrough column so it survives sort inside extract_features ──
    train_df['_label'] = train_df['label']
    test_df['_label']  = test_df['label']

    print("Extracting features (Train)...")
    encoder_path = os.path.join(settings.MODELS_DIR, 'encoders.joblib')
    train_features = extract_features(train_df, fit_encoders=True, encoder_path=encoder_path)

    print("Extracting features (Test)...")
    test_features = extract_features(test_df, encoder_path=encoder_path)

    # Labels are now aligned because _label was carried through the sort
    train_labels = train_features['_label']
    test_labels_aligned = test_features['_label']

    print(f"\nTrain distribution:\n{train_labels.value_counts()}")
    print(f"\nTest distribution:\n{test_labels_aligned.value_counts()}\n")

    print("Training Cold Start Handler...")
    cs = ColdStartHandler()
    cs.fit(train_features)
    cs.save(os.path.join(settings.MODELS_DIR, 'cold_start.json'))

    print("Training Anomaly Detector (Isolation Forest)...")
    detector = AnomalyDetector()
    detector.fit(train_features)
    detector.save(os.path.join(settings.MODELS_DIR, 'detector.joblib'))

    print("Training Anomaly Classifier (Random Forest + SMOTE)...")
    classifier = AnomalyClassifier()
    classifier.fit(train_features, train_labels)
    classifier.save(os.path.join(settings.MODELS_DIR, 'classifier.joblib'))

    # Save SHAP background sample
    feat_names = get_feature_names()
    bg_df = train_features[feat_names].sample(n=min(200, len(train_features)), random_state=42)
    bg_df.to_csv(os.path.join(settings.MODELS_DIR, 'shap_background.csv'), index=False)

    # ── Evaluate ──────────────────────────────────────────────
    print("\nEvaluating classifier on test set...")
    y_test = test_labels_aligned.values
    y_pred = []

    for _, row in test_features.iterrows():
        try:
            pred_label, _ = classifier.predict(row.to_dict())
            y_pred.append(pred_label)
        except Exception:
            y_pred.append("normal")

    print("\n=== Classification Report ===")
    print(classification_report(y_test, y_pred, zero_division=0))

    # Binary anomaly detection metrics
    y_binary_true = (y_test != 'normal').astype(int)
    y_binary_pred = (np.array(y_pred) != 'normal').astype(int)

    # Ensemble scores for anomaly detection evaluation
    print("Computing anomaly detector scores...")
    scores = []
    for _, row in test_features.iterrows():
        s = detector.score(row.to_dict(), row.get('entity_id', ''))
        scores.append(s)

    from sklearn.metrics import roc_auc_score
    try:
        auc = roc_auc_score(y_binary_true, scores)
        print(f"\nAnomaly Detection AUC-ROC: {auc:.4f}")
    except Exception as e:
        print(f"AUC-ROC computation error: {e}")

    # Top-1% FPR
    threshold_idx = int(len(scores) * 0.99)
    sorted_scores = sorted(scores, reverse=True)
    top1_threshold = sorted_scores[threshold_idx] if threshold_idx < len(sorted_scores) else 0.5
    top1_flagged = np.array(scores) >= top1_threshold
    fp_top1 = np.sum(top1_flagged & (y_binary_true == 0))
    total_neg = np.sum(y_binary_true == 0)
    fpr_top1 = fp_top1 / total_neg if total_neg > 0 else 0
    print(f"FPR at top-1% threshold ({top1_threshold:.3f}): {fpr_top1:.4f}")

    print("\n✅ All models saved to:", settings.MODELS_DIR)

if __name__ == "__main__":
    main()
