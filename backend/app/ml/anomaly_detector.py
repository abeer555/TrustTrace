from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
import joblib
from app.ml.baseline_profiler import BaselineProfiler
from app.ml.feature_engineering import get_feature_names

class AnomalyDetector:
    def __init__(self):
        self.isolation_forest = IsolationForest(contamination=0.02, n_estimators=200, random_state=42)
        self.scaler = StandardScaler()
        self.profiler = BaselineProfiler()
        self.features = get_feature_names()
        
    def fit(self, X_train: pd.DataFrame):
        X = X_train[self.features].fillna(0)
        X_scaled = self.scaler.fit_transform(X)
        self.isolation_forest.fit(X_scaled)
        
    def score(self, features: dict, entity_id: str) -> float:
        df = pd.DataFrame([features])
        for col in self.features:
            if col not in df.columns:
                df[col] = 0.0
        df = df[self.features].fillna(0)
        X_scaled = self.scaler.transform(df)
        
        if_score_raw = self.isolation_forest.decision_function(X_scaled)[0]
        if_score = 1.0 - (1.0 / (1.0 + np.exp(-if_score_raw)))
        
        prof_score = self.profiler.compute_deviation_score(entity_id, features)
        
        rule_score = 1.0 if features.get('geo_velocity', 0) > 800 else 0.0
        
        ensemble_score = 0.4 * if_score + 0.4 * prof_score + 0.2 * rule_score
        return float(min(max(ensemble_score, 0.0), 1.0))
        
    def save(self, path: str):
        joblib.dump({'if': self.isolation_forest, 'scaler': self.scaler}, path)
        
    def load(self, path: str):
        try:
            data = joblib.load(path)
            self.isolation_forest = data['if']
            self.scaler = data['scaler']
        except Exception:
            pass
