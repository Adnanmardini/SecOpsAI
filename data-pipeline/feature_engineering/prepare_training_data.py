import pandas as pd
import numpy as np
import glob
import os
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from imblearn.over_sampling import RandomOverSampler
from loguru import logger

DATA_DIR  = "datasets/cicids2017"
MODEL_DIR = "ml-engine/models"

LABEL_MAP = {
    "BENIGN": "benign", "Benign": "benign",
    "Bot": "c2_beaconing", "DDoS": "dos",
    "DoS Hulk": "dos", "DoS GoldenEye": "dos",
    "DoS slowloris": "dos", "DoS Slowhttptest": "dos",
    "Infiltration": "lateral_movement", "PortScan": "reconnaissance",
    "FTP-Patator": "brute_force", "SSH-Patator": "brute_force",
    "Web Attack  Brute Force": "brute_force", "Web Attack  XSS": "web_attack",
    "Web Attack  Sql Injection": "web_attack", "Heartbleed": "exfiltration",
}

def load_optimized_data(data_dir):
    files = glob.glob(f"{data_dir}/*.csv")
    cleaned_chunks = []
    
    for f in files:
        logger.info(f"Processing {Path(f).name}...")
        df = pd.read_csv(f, low_memory=False)
        df.columns = df.columns.str.strip()
        df["label"] = df["Label"].map(LABEL_MAP).fillna("other")
        
        # Drop columns and fix numeric issues
        drop_cols = ["Label", "Flow ID", "Source IP", "Destination IP", "Timestamp", "Source Port", "Destination Port"]
        df = df.drop(columns=[c for c in drop_cols if c in df.columns])
        df = df.replace([np.inf, -np.inf], np.nan).fillna(0)
        
        # MEMORY FIX 1: Downsample benign to 1% (Very aggressive)
        benign = df[df["label"] == "benign"].sample(frac=0.01, random_state=42)
        attacks = df[df["label"] != "benign"]
        
        chunk = pd.concat([benign, attacks])
        
        # MEMORY FIX 2: Convert to 32-bit to save 50% RAM
        for col in chunk.select_dtypes(include=['float64']).columns:
            chunk[col] = chunk[col].astype('float32')
        for col in chunk.select_dtypes(include=['int64']).columns:
            chunk[col] = chunk[col].astype('int32')
            
        cleaned_chunks.append(chunk)
        del df
        
    combined = pd.concat(cleaned_chunks, ignore_index=True)
    X = combined.drop(columns=["label"])
    y = combined["label"]
    X = X.drop(columns=X.columns[X.var() == 0])
    return X, y

def main():
    logger.info("Starting optimized memory-safe preparation...")
    X, y = load_optimized_data(DATA_DIR)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    le = LabelEncoder()
    y_train_enc = le.fit_transform(y_train)
    y_test_enc = le.transform(y_test)
    
    # MEMORY FIX 3: ROS on smaller 32-bit data
    logger.info("Balancing classes...")
    ros = RandomOverSampler(random_state=42)
    X_train_bal, y_train_bal = ros.fit_resample(X_train, y_train_enc)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_bal)
    
    os.makedirs(MODEL_DIR, exist_ok=True)
    np.save(f"{MODEL_DIR}/X_train.npy", X_train_scaled.astype('float32'))
    np.save(f"{MODEL_DIR}/X_test.npy", scaler.transform(X_test).astype('float32'))
    np.save(f"{MODEL_DIR}/y_train.npy", y_train_bal.astype('int32'))
    np.save(f"{MODEL_DIR}/y_test.npy", y_test_enc.astype('int32'))
    joblib.dump(le, f"{MODEL_DIR}/label_encoder.joblib")
    
    logger.success("FIX APPLIED: Data generated successfully.")

if __name__ == "__main__":
    main()
