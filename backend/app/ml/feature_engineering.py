import pandas as pd
import numpy as np
import json
import math
from sklearn.preprocessing import LabelEncoder
import joblib


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def extract_features(events_df: pd.DataFrame, fit_encoders=False, encoder_path=None) -> pd.DataFrame:
    df = events_df.copy()

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour_of_day'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    df['is_business_hours'] = df['hour_of_day'].between(9, 18).astype(int)

    # Parse geo_location
    def parse_geo(x):
        try:
            d = json.loads(x) if isinstance(x, str) else x
            return float(d.get('lat', 0)), float(d.get('lon', 0))
        except Exception:
            return 0.0, 0.0

    lats_lons = df['geo_location'].apply(parse_geo)
    df['geo_lat'] = [v[0] for v in lats_lons]
    df['geo_lon'] = [v[1] for v in lats_lons]

    # Geo velocity (haversine between consecutive events per entity)
    df = df.sort_values(['entity_id', 'timestamp']).reset_index(drop=True)
    df['prev_lat'] = df.groupby('entity_id')['geo_lat'].shift(1)
    df['prev_lon'] = df.groupby('entity_id')['geo_lon'].shift(1)
    df['prev_time'] = df.groupby('entity_id')['timestamp'].shift(1)

    def calc_velocity(row):
        if pd.isna(row['prev_lat']) or pd.isna(row['prev_time']):
            return 0.0
        dist = haversine(row['geo_lat'], row['geo_lon'], row['prev_lat'], row['prev_lon'])
        time_diff = (row['timestamp'] - row['prev_time']).total_seconds() / 3600.0
        if time_diff <= 0:
            return 0.0
        return dist / time_diff

    df['geo_velocity'] = df.apply(calc_velocity, axis=1)

    df['session_duration_minutes'] = df['session_duration'].astype(float)
    df['resource_hash'] = df['resource_accessed'].apply(lambda x: abs(hash(str(x))) % 1000)

    # ── Rolling counts (numeric only, computed per entity using sort order) ──
    def rolling_count_1h(group):
        """Count events per entity in the past 1 hour using timestamp index."""
        group = group.sort_values('timestamp')
        ts = group['timestamp'].values.astype('datetime64[ns]')
        counts = []
        for i, t in enumerate(ts):
            window_start = t - np.timedelta64(1, 'h')
            counts.append(int(np.sum(ts[:i+1] >= window_start)))
        return pd.Series(counts, index=group.index)

    def rolling_count_24h(group):
        group = group.sort_values('timestamp')
        ts = group['timestamp'].values.astype('datetime64[ns]')
        counts = []
        for i, t in enumerate(ts):
            window_start = t - np.timedelta64(24, 'h')
            counts.append(int(np.sum(ts[:i+1] >= window_start)))
        return pd.Series(counts, index=group.index)

    def rolling_unique_resources_24h(group):
        group = group.sort_values('timestamp')
        ts = group['timestamp'].values.astype('datetime64[ns]')
        resources = group['resource_accessed'].values
        counts = []
        for i, t in enumerate(ts):
            window_start = t - np.timedelta64(24, 'h')
            mask = ts[:i+1] >= window_start
            counts.append(int(len(set(resources[:i+1][mask]))))
        return pd.Series(counts, index=group.index)

    def rolling_failed_1h(group):
        group = group.sort_values('timestamp')
        ts = group['timestamp'].values.astype('datetime64[ns]')
        failed = group['is_failed'].values.astype(float)
        counts = []
        for i, t in enumerate(ts):
            window_start = t - np.timedelta64(1, 'h')
            mask = ts[:i+1] >= window_start
            counts.append(float(np.sum(failed[:i+1][mask])))
        return pd.Series(counts, index=group.index)

    # is_failed flag
    df['is_failed'] = df['command_sequence'].apply(
        lambda x: 1 if (isinstance(x, list) and 'login_failed' in x)
                     or (isinstance(x, str) and 'login_failed' in x)
                  else 0
    )

    # Apply rolling functions per entity group
    df['n_events_last_1h'] = df.groupby('entity_id', group_keys=False).apply(rolling_count_1h)
    df['n_events_last_24h'] = df.groupby('entity_id', group_keys=False).apply(rolling_count_24h)
    df['n_unique_resources_last_24h'] = df.groupby('entity_id', group_keys=False).apply(rolling_unique_resources_24h)
    df['n_failed_auths_last_1h'] = df.groupby('entity_id', group_keys=False).apply(rolling_failed_1h)

    # Encoders
    if fit_encoders:
        auth_enc = LabelEncoder()
        os_enc = LabelEncoder()
        df['auth_method_encoded'] = auth_enc.fit_transform(df['auth_method'].fillna('unknown'))
        df['device_os_encoded'] = os_enc.fit_transform(
            df['device_fingerprint'].apply(
                lambda x: json.loads(x).get('os', 'Unknown') if isinstance(x, str) else 'Unknown'
            )
        )
        if encoder_path:
            joblib.dump({'auth': auth_enc, 'os': os_enc}, encoder_path)
    else:
        if encoder_path:
            try:
                encoders = joblib.load(encoder_path)
                def safe_transform(enc, values):
                    known = set(enc.classes_)
                    return enc.transform([v if v in known else enc.classes_[0] for v in values])
                df['auth_method_encoded'] = safe_transform(encoders['auth'], df['auth_method'].fillna('unknown'))
                df['device_os_encoded'] = safe_transform(
                    encoders['os'],
                    df['device_fingerprint'].apply(
                        lambda x: json.loads(x).get('os', 'Unknown') if isinstance(x, str) else 'Unknown'
                    )
                )
            except Exception:
                df['auth_method_encoded'] = 0
                df['device_os_encoded'] = 0
        else:
            df['auth_method_encoded'] = 0
            df['device_os_encoded'] = 0

    df['first_seen'] = df.groupby('entity_id')['timestamp'].transform('min')
    df['days_since_first_seen'] = (df['timestamp'] - df['first_seen']).dt.total_seconds() / 86400.0

    # Only fill NaN in numeric columns; leave datetime columns alone
    num_cols = df.select_dtypes(include=[np.number]).columns
    df[num_cols] = df[num_cols].fillna(0)
    return df


def get_feature_names() -> list[str]:
    return [
        'hour_of_day', 'day_of_week', 'is_weekend', 'is_business_hours',
        'geo_lat', 'geo_lon', 'geo_velocity', 'session_duration_minutes',
        'resource_hash', 'auth_method_encoded', 'n_events_last_1h',
        'n_events_last_24h', 'n_unique_resources_last_24h', 'n_failed_auths_last_1h',
        'device_os_encoded', 'days_since_first_seen'
    ]
