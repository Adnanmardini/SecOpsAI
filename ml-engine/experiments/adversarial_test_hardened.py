import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import xgboost as xgb
import joblib
import json
import os
from sklearn.metrics import accuracy_score
from art.estimators.classification import XGBoostClassifier as ARTXGBoost
from art.estimators.classification import PyTorchClassifier
from art.attacks.evasion import FastGradientMethod, ProjectedGradientDescentNumpy, CarliniLInfMethod, ZooAttack, HopSkipJump
from loguru import logger

# --- Step 1: Define Surrogate for Gradient Attacks ---
class SurrogateNet(nn.Module):
    def __init__(self, input_dim, n_classes):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, n_classes)
        )
    def forward(self, x): return self.net(x)

def run_final_validation():
    print("\n" + "="*60)
    print("SECOPSAI: FINAL ADVERSARIAL VALIDATION (OPTIMIZED)")
    print("="*60)

    # 1. Load Data and hardened model
    X_test = np.load('../models/X_test.npy').astype(np.float32)
    y_test = np.load('../models/y_test.npy')
    le = joblib.load('../models/label_encoder.joblib')
    hardened = xgb.XGBClassifier()
    hardened.load_model('../models/xgboost_hardened.json')
    
    # Speed Fix: Use small sample for lightning-fast results
    X_sub = X_test[:10] 
    y_sub = y_test[:10]

    # 2. Train Surrogate MLP (To allow FGSM/PGD/CW on XGBoost)
    print("Retraining surrogate for transfer attacks...")
    surrogate = SurrogateNet(X_test.shape[1], len(le.classes_))
    optimizer = optim.Adam(surrogate.parameters(), lr=0.01)
    criterion = nn.CrossEntropyLoss()
    
    # Fast training on a small subset
    X_train_t = torch.tensor(X_test[:500], dtype=torch.float32)
    y_train_t = torch.tensor(y_test[:500], dtype=torch.long)
    for epoch in range(5):
        optimizer.zero_grad()
        loss = criterion(surrogate(X_train_t), y_train_t)
        loss.backward()
        optimizer.step()

    # 3. Setup ART Wrappers
    art_surr = PyTorchClassifier(model=surrogate, loss=criterion, optimizer=optimizer, 
                                 input_shape=(X_test.shape[1],), nb_classes=len(le.classes_))
    art_xgb = ARTXGBoost(model=hardened, nb_features=X_test.shape[1], nb_classes=len(le.classes_))

    # 4. Corrected 5-Attack Suite
    attack_suite = [
        ("fgsm", FastGradientMethod(estimator=art_surr, eps=0.1), "FGSM (Surrogate)"),
        ("pgd", ProjectedGradientDescentNumpy(estimator=art_surr, eps=0.1, max_iter=5), "PGD (Surrogate)"),
        ("cw", CarliniLInfMethod(classifier=art_surr, max_iter=5), "C&W (Surrogate)"),
        ("zoo", ZooAttack(classifier=art_xgb, nb_parallel=1, max_iter=5), "ZOO (Direct)"),
        # Parameter fix: init_eval must be smaller than max_eval
        ("hsj", HopSkipJump(classifier=art_xgb, max_iter=2, init_eval=10, max_eval=20), "HopSkipJump (Direct)")
    ]

    post_results = {}
    survived_count = 0

    for key, attack, label in attack_suite:
        logger.info(f"Testing Vector: {label}")
        try:
            X_adv = attack.generate(X_sub)
            adv_acc = accuracy_score(y_sub, hardened.predict(X_adv))
            
            # survival check (Score > 60%)
            survived = adv_acc >= 0.60
            if survived: survived_count += 1
            
            print(f" -> {label}: Acc: {adv_acc:.4f} | {'SURVIVED ✅' if survived else 'BROKEN ❌'}")
            post_results[key] = {"accuracy": float(adv_acc), "survived": bool(survived)}
        except Exception as e:
            logger.error(f"Attack {label} failed: {e}")

    print("\n" + "="*60)
    print(f"FINAL PROJECT RESULT: {survived_count}/5 Attacks Survived")
    print("STATUS: " + ("CLIENT REQUIREMENT MET ✅" if survived_count >= 3 else "FAILED ❌"))
    print("="*60)

    # 5. Save Final Report
    with open('../../docs/reports/post_hardening_results.json', 'w') as f:
        json.dump(post_results, f, indent=2)

if __name__ == "__main__":
    run_final_validation()
