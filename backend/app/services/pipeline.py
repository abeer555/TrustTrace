import pandas as pd
import os
import json
from datetime import datetime, timezone
from app.models.schemas import AccessEvent, RiskScoreResponse
from app.ml.anomaly_detector import AnomalyDetector
from app.ml.classifier import AnomalyClassifier
from app.ml.explainer import AnomalyExplainer
from app.ml.cold_start import ColdStartHandler
from app.ml.feature_engineering import extract_features
from app.core.config import settings

class InferencePipeline:
    def __init__(self):
        self.detector = AnomalyDetector()
        self.classifier = AnomalyClassifier()
        self.explainer = AnomalyExplainer(self.classifier)
        self.cold_start = ColdStartHandler()
        self.entity_event_counts = {}
        self._models_loaded = False
        
    def load_models(self):
        if self._models_loaded: return
        self.detector.load(os.path.join(settings.MODELS_DIR, 'detector.joblib'))
        self.detector.profiler.load(os.path.join(settings.MODELS_DIR, 'profiler.json'))
        self.classifier.load(os.path.join(settings.MODELS_DIR, 'classifier.joblib'))
        self.cold_start.load(os.path.join(settings.MODELS_DIR, 'cold_start.json'))
        
        # We need a small background dataset for SHAP, but we can bypass it if not available
        try:
            bg_df = pd.read_csv(os.path.join(settings.MODELS_DIR, 'shap_background.csv'))
            self.explainer.setup_shap(bg_df)
        except Exception:
            pass
            
        self._models_loaded = True

    def process_event(self, event: AccessEvent) -> RiskScoreResponse:
        self.load_models()
        
        # Build a 1-row dataframe for feature extraction (this is basic, missing real history)
        event_dict = event.model_dump()
        event_dict['device_fingerprint'] = json.dumps(event_dict['device_fingerprint'])
        df = pd.DataFrame([event_dict])
        
        features_df = extract_features(df, encoder_path=os.path.join(settings.MODELS_DIR, 'encoders.joblib'))
        features = features_df.iloc[0].to_dict()
        
        is_cold = self.detector.profiler.is_cold_start(event.entity_id)
        
        if is_cold:
            baseline = self.cold_start.get_baseline_features(event.entity_type)
            for k, v in baseline.items():
                if pd.isna(features.get(k)) or features.get(k) == 0:
                    features[k] = v
                    
        risk_score = self.detector.score(features, event.entity_id)
        
        anomaly_type = "normal"
        if risk_score > settings.ANOMALY_THRESHOLD:
            anomaly_type, conf = self.classifier.predict(features)
            
        explanation = self.explainer.explain(features, anomaly_type, risk_score)
        explanation['is_cold_start'] = is_cold
        
        self.detector.profiler.update_profile(event.entity_id, features)
        self.entity_event_counts[event.entity_id] = self.entity_event_counts.get(event.entity_id, 0) + 1
        
        return RiskScoreResponse(
            entity_id=event.entity_id,
            risk_score=risk_score,
            anomaly_type=anomaly_type,
            explanation=[explanation['summary']] + [f['description'] for f in explanation['factors']] + explanation['rule_triggers'],
            is_cold_start=is_cold
        )
        
    def batch_process(self, events_df: pd.DataFrame) -> pd.DataFrame:
        self.load_models()
        features_df = extract_features(events_df, encoder_path=os.path.join(settings.MODELS_DIR, 'encoders.joblib'))
        
        results = []
        for i, row in events_df.iterrows():
            features = features_df.iloc[i].to_dict()
            eid = row['entity_id']
            etype = row['entity_type']
            
            is_cold = self.detector.profiler.is_cold_start(eid)
            if is_cold:
                baseline = self.cold_start.get_baseline_features(etype)
                for k, v in baseline.items():
                    if pd.isna(features.get(k)) or features.get(k) == 0:
                        features[k] = v
                        
            risk_score = self.detector.score(features, eid)
            
            anomaly_type = "normal"
            if risk_score > settings.ANOMALY_THRESHOLD:
                anomaly_type, _ = self.classifier.predict(features)
                
            self.detector.profiler.update_profile(eid, features)
            self.entity_event_counts[eid] = self.entity_event_counts.get(eid, 0) + 1
            
            results.append({
                'risk_score': risk_score,
                'anomaly_type': anomaly_type
            })
            
        results_df = pd.DataFrame(results)
        return pd.concat([events_df, results_df], axis=1)

pipeline = InferencePipeline()
