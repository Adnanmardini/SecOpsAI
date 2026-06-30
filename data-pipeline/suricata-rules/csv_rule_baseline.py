"""
Rule-Based Detection Baseline
Applies Suricata-equivalent rule logic to CICIDS CSV files.
"""
import pandas as pd
import numpy as np
import json
import glob
import os
from sklearn.metrics import confusion_matrix, f1_score
from loguru import logger

DATA_DIR = "datasets/cicids2017"
OUTPUT_FILE = "docs/reports/rule_baseline_metrics.json"

def apply_c2_beaconing_rule(df):
    unusual_ports = df["Destination Port"].isin([4444, 6666, 8888, 31337, 1337])
    small_payload = df["Total Length of Fwd Packets"] < 500
    return (unusual_ports & small_payload)

def apply_dns_tunnel_rule(df):
    is_dns_port = df["Destination Port"] == 53
    long_duration = df["Flow Duration"] > 1000000 
    high_packet_count = (df["Total Fwd Packets"] + df["Total Backward Packets"]) > 20
    return (is_dns_port & long_duration & high_packet_count)

def apply_lateral_movement_rule(df):
    return df["Destination Port"].isin([445, 3389, 135, 139])

def apply_exfiltration_rule(df):
    return df["Total Length of Fwd Packets"] > 100000

def process_files_one_by_one(data_dir):
    files = glob.glob(f"{data_dir}/*.csv")
    if not files:
        logger.error("No CSV files found!")
        return None

    # Global counters
    total_tp, total_fp, total_tn, total_fn = 0, 0, 0, 0

    for f in files:
        logger.info(f"Processing {os.path.basename(f)}...")
        # Load only ONE file
        df = pd.read_csv(f, low_memory=False)
        df.columns = df.columns.str.strip()
        
        # Ground Truth
        y_true = (df["Label"] != "BENIGN").astype(int)

        # Apply Rules
        pred = (apply_c2_beaconing_rule(df) | 
                apply_dns_tunnel_rule(df) | 
                apply_lateral_movement_rule(df) | 
                apply_exfiltration_rule(df)).astype(int)

        # Calculate confusion matrix for THIS file
        tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[0,1]).ravel()
        
        # Add to global totals
        total_tp += tp
        total_fp += fp
        total_tn += tn
        total_fn += fn
        
        # Free memory
        del df

    # Final Overall Calculations
    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return {
        "baseline_type": "suricata_rule_equivalent",
        "overall": {
            "f1": round(f1, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "true_positives": int(total_tp),
            "false_positives": int(total_fp),
            "true_negatives": int(total_tn),
            "false_negatives": int(total_fn)
        },
        "ml_target": {
            "minimum_f1_required": round(f1 + 0.15, 4)
        }
    }

if __name__ == "__main__":
    os.makedirs("docs/reports", exist_ok=True)
    results = process_files_one_by_one(DATA_DIR)
    
    if results:
        with open(OUTPUT_FILE, "w") as f:
            json.dump(results, f, indent=2)
        
        logger.success("=== FINAL RULE BASELINE ===")
        logger.info(f"Overall F1: {results['overall']['f1']}")
        logger.info(f"ML Model Goal: {results['ml_target']['minimum_f1_required']}")
