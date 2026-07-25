import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import uuid
import json

class SyntheticDataGenerator:
    def __init__(self, seed=42):
        self.fake = Faker()
        Faker.seed(seed)
        np.random.seed(seed)
        random.seed(seed)
        self.cities = [
            ("New York", 40.7128, -74.0060), ("London", 51.5074, -0.1278),
            ("Tokyo", 35.6762, 139.6503), ("Paris", 48.8566, 2.3522),
            ("Berlin", 52.5200, 13.4050), ("Sydney", -33.8688, 151.2093),
            ("Toronto", 43.6510, -79.3470), ("Singapore", 1.3521, 103.8198),
            ("San Francisco", 37.7749, -122.4194), ("Mumbai", 19.0760, 72.8777)
        ]
        self.resources = [f"/api/resource_{i}" for i in range(1, 21)] + [
            "/admin/config", "/files/reports/Q1", "/api/users", "/auth/login"
        ]
        self.auth_methods = ["password", "mfa", "sso", "api_key", "biometric"]
        
    def generate_entity_profiles(self, n_users=200, n_service_accounts=50, n_devices=100):
        profiles = {}
        for i in range(n_users):
            eid = f"user_{i}"
            city = random.choice(self.cities)
            profiles[eid] = {
                "entity_type": "user",
                "home_geo": {"city": city[0], "lat": city[1], "lon": city[2]},
                "typical_hours": random.sample(range(8, 18), 4),
                "typical_resources": random.sample(self.resources, 5),
                "typical_auth_method": "mfa",
                "typical_session_duration": (60, 15),
                "typical_device_fingerprint": {"os": "Windows 11", "mac": self.fake.mac_address(), "protocol": "TLS 1.3"}
            }
        for i in range(n_service_accounts):
            eid = f"svc_{i}"
            city = random.choice(self.cities)
            profiles[eid] = {
                "entity_type": "service_account",
                "home_geo": {"city": city[0], "lat": city[1], "lon": city[2]},
                "typical_hours": list(range(24)),
                "typical_resources": random.sample(self.resources, 10),
                "typical_auth_method": "api_key",
                "typical_session_duration": (300, 50),
                "typical_device_fingerprint": {"os": "Linux", "mac": self.fake.mac_address(), "protocol": "TLS 1.2"}
            }
        return profiles

    def generate_normal_event(self, entity_id, profile, timestamp):
        hour = timestamp.hour
        if random.random() < 0.1:
            hour = random.choice(range(24))
        
        return {
            "entity_id": entity_id,
            "entity_type": profile["entity_type"],
            "timestamp": timestamp,
            "source_ip": self.fake.ipv4(),
            "geo_location": json.dumps(profile["home_geo"]),
            "resource_accessed": random.choice(profile["typical_resources"] + [random.choice(self.resources)]),
            "auth_method": profile["typical_auth_method"] if random.random() < 0.9 else random.choice(self.auth_methods),
            "session_duration": max(1.0, np.random.normal(*profile["typical_session_duration"])),
            "command_sequence": ["login", "read", "logout"],
            "device_fingerprint": json.dumps(profile["typical_device_fingerprint"]),
            "label": "normal"
        }

    def inject_brute_force(self, entity_id, profile, base_time):
        events = []
        ip = self.fake.ipv4()
        for i in range(random.randint(10, 30)):
            t = base_time + timedelta(seconds=i*4)
            events.append({
                "entity_id": entity_id,
                "entity_type": profile["entity_type"],
                "timestamp": t,
                "source_ip": ip,
                "geo_location": json.dumps(profile["home_geo"]),
                "resource_accessed": "/auth/login",
                "auth_method": "password",
                "session_duration": 0.0,
                "command_sequence": ["login_failed"],
                "device_fingerprint": json.dumps(profile["typical_device_fingerprint"]),
                "label": "brute_force"
            })
        return events

    def inject_impossible_travel(self, entity_id, profile, base_time):
        e1 = self.generate_normal_event(entity_id, profile, base_time)
        e1["label"] = "impossible_travel"
        e2 = self.generate_normal_event(entity_id, profile, base_time + timedelta(minutes=45))
        other_city = random.choice([c for c in self.cities if c[0] != profile["home_geo"]["city"]])
        e2["geo_location"] = json.dumps({"city": other_city[0], "lat": other_city[1], "lon": other_city[2]})
        e2["label"] = "impossible_travel"
        return [e1, e2]

    def inject_credential_stuffing(self, entity_profiles, base_time):
        events = []
        ip = self.fake.ipv4()
        for eid, profile in random.sample(list(entity_profiles.items()), 10):
            events.append({
                "entity_id": eid,
                "entity_type": profile["entity_type"],
                "timestamp": base_time + timedelta(seconds=random.randint(1, 60)),
                "source_ip": ip,
                "geo_location": json.dumps(profile["home_geo"]),
                "resource_accessed": "/auth/login",
                "auth_method": "password",
                "session_duration": 0.0,
                "command_sequence": ["login_failed"],
                "device_fingerprint": json.dumps(profile["typical_device_fingerprint"]),
                "label": "credential_stuffing"
            })
        return events

    def inject_lateral_movement(self, entity_id, profile, base_time):
        events = []
        for i in range(20):
            t = base_time + timedelta(minutes=i*2)
            events.append({
                "entity_id": entity_id,
                "entity_type": profile["entity_type"],
                "timestamp": t,
                "source_ip": self.fake.ipv4(),
                "geo_location": json.dumps(profile["home_geo"]),
                "resource_accessed": random.choice(self.resources),
                "auth_method": "sso",
                "session_duration": random.uniform(5.0, 15.0),
                "command_sequence": ["read", "download"],
                "device_fingerprint": json.dumps(profile["typical_device_fingerprint"]),
                "label": "lateral_movement"
            })
        return events

    def inject_device_spoofing(self, entity_id, profile, base_time):
        e = self.generate_normal_event(entity_id, profile, base_time)
        e["device_fingerprint"] = json.dumps({"os": "Unknown", "mac": self.fake.mac_address(), "protocol": "HTTP"})
        e["label"] = "device_spoofing"
        return [e]

    def inject_low_and_slow(self, entity_id, profile, start_time, end_time):
        events = []
        current = start_time
        while current < end_time:
            if random.random() < 0.1:
                e = self.generate_normal_event(entity_id, profile, current)
                e["resource_accessed"] = "/admin/config"
                e["label"] = "low_and_slow"
                events.append(e)
            current += timedelta(hours=12)
        return events

    def inject_insider_drift(self, entity_id, profile, base_time):
        events = []
        for i in range(5):
            t = base_time + timedelta(days=i)
            e = self.generate_normal_event(entity_id, profile, t)
            e["resource_accessed"] = random.choice([r for r in self.resources if r not in profile["typical_resources"]])
            e["label"] = "insider_drift"
            events.append(e)
        return events

    def generate_dataset(self, n_days=30, attack_rate=0.015):
        profiles = self.generate_entity_profiles()
        all_events = []
        start_date = datetime.now() - timedelta(days=n_days)
        
        for day in range(n_days):
            current_date = start_date + timedelta(days=day)
            for eid, profile in profiles.items():
                for _ in range(random.randint(1, 5)):
                    t = current_date + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
                    all_events.append(self.generate_normal_event(eid, profile, t))
                    
                if random.random() < attack_rate:
                    attack_type = random.choice([
                        "brute_force", "impossible_travel", "credential_stuffing",
                        "lateral_movement", "device_spoofing", "low_and_slow", "insider_drift"
                    ])
                    t = current_date + timedelta(hours=random.randint(0, 23))
                    if attack_type == "brute_force":
                        all_events.extend(self.inject_brute_force(eid, profile, t))
                    elif attack_type == "impossible_travel":
                        all_events.extend(self.inject_impossible_travel(eid, profile, t))
                    elif attack_type == "credential_stuffing":
                        all_events.extend(self.inject_credential_stuffing(profiles, t))
                    elif attack_type == "lateral_movement":
                        all_events.extend(self.inject_lateral_movement(eid, profile, t))
                    elif attack_type == "device_spoofing":
                        all_events.extend(self.inject_device_spoofing(eid, profile, t))
                    elif attack_type == "low_and_slow":
                        all_events.extend(self.inject_low_and_slow(eid, profile, t, t + timedelta(days=3)))
                    elif attack_type == "insider_drift":
                        all_events.extend(self.inject_insider_drift(eid, profile, t))
                        
        df = pd.DataFrame(all_events)
        df = df.sort_values("timestamp").reset_index(drop=True)
        return df, profiles
