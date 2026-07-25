import shap
import pandas as pd
from app.ml.classifier import AnomalyClassifier
from app.ml.feature_engineering import get_feature_names

class AnomalyExplainer:
    def __init__(self, classifier: AnomalyClassifier):
        self.classifier = classifier
        self.shap_explainer = None
        self.features = get_feature_names()
        
    def setup_shap(self, X_background: pd.DataFrame):
        X = X_background[self.features].fillna(0)
        X_scaled = self.classifier.scaler.transform(X)
        self.shap_explainer = shap.TreeExplainer(self.classifier.model, X_scaled, feature_perturbation='interventional')
        
    def explain(self, features: dict, anomaly_type: str, risk_score: float) -> dict:
        summary = f"Flagged: {anomaly_type} (risk: {risk_score:.2f})"
        factors = []
        
        if self.shap_explainer is not None:
            df = pd.DataFrame([features])
            for col in self.features:
                if col not in df.columns:
                    df[col] = 0.0
            X = df[self.features].fillna(0)
            X_scaled = self.classifier.scaler.transform(X)
            shap_vals = self.shap_explainer.shap_values(X_scaled)
            
            try:
                class_idx = list(self.classifier.label_encoder.classes_).index(anomaly_type)
                if isinstance(shap_vals, list):
                    vals = shap_vals[class_idx][0]
                else:
                    if len(shap_vals.shape) == 3:
                        vals = shap_vals[0, :, class_idx]
                    else:
                        vals = shap_vals[0]
                        
                top_indices = sorted(range(len(vals)), key=lambda i: abs(vals[i]), reverse=True)[:5]
                for i in top_indices:
                    f_name = self.features[i]
                    f_val = features.get(f_name, 0)
                    contrib = float(vals[i])
                    factors.append({
                        'feature': f_name,
                        'value': float(f_val),
                        'contribution': contrib,
                        'description': f"Feature '{f_name}' contributed {contrib:.2f} to the score (value: {f_val})"
                    })
            except Exception:
                pass
                
        rule_triggers = self._rule_based_flags(features)
        
        return {
            'summary': summary,
            'factors': factors,
            'rule_triggers': rule_triggers,
            'is_cold_start': False
        }
        
    def _rule_based_flags(self, features: dict) -> list[str]:
        triggers = []
        if features.get('geo_velocity', 0) > 800:
            triggers.append('GEO_VELOCITY_EXCEEDED')
        if features.get('is_business_hours', 1) == 0 and features.get('is_weekend', 0) == 0:
            triggers.append('OFF_HOURS_ACCESS')
        if features.get('n_failed_auths_last_1h', 0) > 10:
            triggers.append('RAPID_AUTH_FAILURES')
        if features.get('n_unique_resources_last_24h', 0) > 20:
            triggers.append('UNUSUAL_RESOURCE_BREADTH')
        return triggers
