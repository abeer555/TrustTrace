import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from imblearn.over_sampling import SMOTE
import joblib
from app.ml.feature_engineering import get_feature_names

ANOMALY_TYPES = [
    'normal', 'brute_force', 'impossible_travel', 'credential_stuffing',
    'lateral_movement', 'device_spoofing', 'low_and_slow', 'insider_drift'
]

class AnomalyClassifier:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=200, class_weight='balanced', random_state=42)
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.features = get_feature_names()
        
    def fit(self, X_train: pd.DataFrame, y_train: pd.Series):
        X = X_train[self.features].fillna(0)
        y = self.label_encoder.fit_transform(y_train)
        X_scaled = self.scaler.fit_transform(X)

        # Adapt k_neighbors to the smallest class size (SMOTE requires k < n_samples per class)
        from collections import Counter
        min_class_count = min(Counter(y).values())
        k = max(1, min(5, min_class_count - 1))

        smote = SMOTE(random_state=42, k_neighbors=k)
        X_resampled, y_resampled = smote.fit_resample(X_scaled, y)

        self.model.fit(X_resampled, y_resampled)
        
    def predict(self, features: dict) -> tuple[str, float]:
        df = pd.DataFrame([features])
        for col in self.features:
            if col not in df.columns:
                df[col] = 0.0
        X = df[self.features].fillna(0)
        X_scaled = self.scaler.transform(X)
        
        pred_idx = self.model.predict(X_scaled)[0]
        proba = self.model.predict_proba(X_scaled)[0]
        conf = float(proba[pred_idx])
        label = self.label_encoder.inverse_transform([pred_idx])[0]
        
        return label, conf
        
    def predict_proba_all(self, features: dict) -> dict[str, float]:
        df = pd.DataFrame([features])
        for col in self.features:
            if col not in df.columns:
                df[col] = 0.0
        X = df[self.features].fillna(0)
        X_scaled = self.scaler.transform(X)
        proba = self.model.predict_proba(X_scaled)[0]
        classes = self.label_encoder.inverse_transform(range(len(proba)))
        return {str(k): float(v) for k, v in zip(classes, proba)}
        
    def save(self, path: str):
        joblib.dump({'model': self.model, 'encoder': self.label_encoder, 'scaler': self.scaler}, path)
        
    def load(self, path: str):
        try:
            data = joblib.load(path)
            self.model = data['model']
            self.label_encoder = data['encoder']
            self.scaler = data['scaler']
        except Exception:
            pass
