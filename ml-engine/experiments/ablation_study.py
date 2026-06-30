import numpy as np
import xgboost as xgb
import joblib
import json
import os
from sklearn.metrics import f1_score
from loguru import logger

# === SECOPSAI: Day 3 - Ablation Study (Optimized) ===

def run_study():
    print("\n" + "="*55)
    print("ABLATION STUDY — Feature Group Importance")
    print("="*55)

    # 1. Load the 32-bit data we just generated
    X_train = np.load('../models/X_train.npy')
    X_test = np.load('../models/X_test.npy')
    y_train = np.load('../models/y_train.npy')
    y_test = np.load('../models/y_test.npy')
    
    # 2. Define the 5 Feature Groups (Based on project PDF)
    # We use slices based on the 70+ columns in CICIDS
    FEATURE_GROUPS = {
        'Group_A_Basic_Flow': list(range(0, 15)),
        'Group_B_Timing': list(range(15, 30)),
        'Group_C_DNS_Proxy': list(range(30, 45)),
        'Group_D_Communication': list(range(45, 60)),
        'Group_E_Volume_Rate': list(range(60, X_train.shape[1])),
    }

    # 3. Train Baseline (All Features)
    logger.info("Training baseline model...")
    base_model = xgb.XGBClassifier(n_estimators=50, max_depth=4, random_state=42)
    base_model.fit(X_train, y_train)
    base_f1 = f1_score(y_test, base_model.predict(X_test), average='weighted')
    print(f"\nBaseline F1 Score: {base_f1:.4f}\n")

    results = {}

    # 4. Run Ablation Loop
    for name, indices in FEATURE_GROUPS.items():
        logger.info(f"Testing impact of removing: {name}")
        
        all_indices = list(range(X_train.shape[1]))
        keep = [i for i in all_indices if i not in indices]
        
        # Create reduced data
        X_train_red = X_train[:, keep]
        X_test_red = X_test[:, keep]

        # Train new model
        model = xgb.XGBClassifier(n_estimators=50, max_depth=4, random_state=42)
        model.fit(X_train_red, y_train)
        new_f1 = f1_score(y_test, model.predict(X_test_red), average='weighted')
        
        delta = new_f1 - base_f1
        importance = "CRITICAL" if delta < -0.01 else "LOW"
        
        print(f"-> {name:<25} | F1: {new_f1:.4f} | Delta: {delta:+.4f} | [{importance}]")
        results[name] = {"f1": float(new_f1), "delta": float(delta), "importance": importance}

    # 5. Save Report
    os.makedirs('../../docs/reports', exist_ok=True)
    with open('../../docs/reports/ablation_study_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    logger.success("Ablation Study Complete!")

if __name__ == "__main__":
    run_study()
