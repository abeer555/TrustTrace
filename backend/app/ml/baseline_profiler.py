import json
import numpy as np
from app.core.config import settings

class BaselineProfiler:
    def __init__(self, alpha=0.1):
        self.alpha = alpha
        self.entity_profiles = {}
        self.feature_names = ['geo_velocity', 'session_duration_minutes', 'n_events_last_1h', 'n_unique_resources_last_24h']
        
    def update_profile(self, entity_id: str, event_features: dict):
        if entity_id not in self.entity_profiles:
            self.entity_profiles[entity_id] = {
                'count': 0,
                'means': {f: event_features.get(f, 0) for f in self.feature_names},
                'stds': {f: 1.0 for f in self.feature_names}
            }
        
        prof = self.entity_profiles[entity_id]
        prof['count'] += 1
        
        for f in self.feature_names:
            val = event_features.get(f, 0)
            diff = val - prof['means'][f]
            prof['means'][f] += self.alpha * diff
            prof['stds'][f] = np.sqrt((1 - self.alpha) * (prof['stds'][f]**2) + self.alpha * (diff**2))

    def compute_deviation_score(self, entity_id: str, event_features: dict) -> float:
        if entity_id not in self.entity_profiles:
            return 0.5
            
        prof = self.entity_profiles[entity_id]
        if prof['count'] < settings.MIN_HISTORY_FOR_PROFILE:
            return 0.5
            
        z_scores = []
        for f in self.feature_names:
            val = event_features.get(f, 0)
            std = max(prof['stds'][f], 1e-6)
            z = abs(val - prof['means'][f]) / std
            z_scores.append(z)
            
        avg_z = np.mean(z_scores)
        score = 1.0 - (1.0 / (1.0 + np.exp(avg_z - 3.0)))
        return float(score)

    def get_profile(self, entity_id: str) -> dict:
        return self.entity_profiles.get(entity_id, {})

    def is_cold_start(self, entity_id: str) -> bool:
        prof = self.entity_profiles.get(entity_id)
        if not prof: return True
        return prof['count'] < settings.MIN_HISTORY_FOR_PROFILE

    def save(self, path: str):
        with open(path, 'w') as f:
            json.dump(self.entity_profiles, f)

    def load(self, path: str):
        try:
            with open(path, 'r') as f:
                self.entity_profiles = json.load(f)
        except Exception:
            pass
