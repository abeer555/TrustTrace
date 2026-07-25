import pandas as pd
import json

class ColdStartHandler:
    def __init__(self):
        self.population_profiles = {}
        
    def fit(self, events_df: pd.DataFrame):
        for etype in events_df['entity_type'].unique():
            df_sub = events_df[events_df['entity_type'] == etype]
            self.population_profiles[etype] = {
                'geo_velocity': float(df_sub['geo_velocity'].mean()) if 'geo_velocity' in df_sub.columns else 0.0,
                'session_duration_minutes': float(df_sub['session_duration_minutes'].mean()) if 'session_duration_minutes' in df_sub.columns else 1.0,
                'n_events_last_1h': float(df_sub['n_events_last_1h'].mean()) if 'n_events_last_1h' in df_sub.columns else 1.0,
                'n_unique_resources_last_24h': float(df_sub['n_unique_resources_last_24h'].mean()) if 'n_unique_resources_last_24h' in df_sub.columns else 1.0
            }
            
    def get_baseline_features(self, entity_type: str) -> dict:
        return self.population_profiles.get(entity_type, {
            'geo_velocity': 0.0,
            'session_duration_minutes': 5.0,
            'n_events_last_1h': 1.0,
            'n_unique_resources_last_24h': 1.0
        })
        
    def save(self, path: str):
        with open(path, 'w') as f:
            json.dump(self.population_profiles, f)
            
    def load(self, path: str):
        try:
            with open(path, 'r') as f:
                self.population_profiles = json.load(f)
        except Exception:
            pass
