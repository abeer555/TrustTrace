import os
import sys
from pathlib import Path
import pandas as pd

# Add backend dir to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from app.ml.data_generator import SyntheticDataGenerator
from app.core.config import settings

def main():
    os.makedirs(settings.GENERATED_DIR, exist_ok=True)
    generator = SyntheticDataGenerator()
    
    print("Generating dataset...")
    df, profiles = generator.generate_dataset(n_days=30, attack_rate=0.015)
    
    train_size = int(len(df) * 0.8)
    train_df = df.iloc[:train_size].copy()
    test_df = df.iloc[train_size:].copy()
    
    train_path = os.path.join(settings.GENERATED_DIR, 'events_train.csv')
    test_path = os.path.join(settings.GENERATED_DIR, 'events_test.csv')
    labels_test_path = os.path.join(settings.GENERATED_DIR, 'labels_test.csv')
    
    train_df.to_csv(train_path, index=False)
    
    test_labels = test_df[['label']]
    test_df_no_label = test_df.drop(columns=['label'])
    
    test_df_no_label.to_csv(test_path, index=False)
    test_labels.to_csv(labels_test_path, index=False)
    
    print(f"Total events: {len(df)}")
    print(f"Train size: {len(train_df)}")
    print(f"Test size: {len(test_df)}")
    print("\nAnomaly distribution in full dataset:")
    print(df['label'].value_counts())
    print(f"\nSaved to {settings.GENERATED_DIR}")

if __name__ == "__main__":
    main()
