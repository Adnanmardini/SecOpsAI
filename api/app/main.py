# === api/app/main.py — Complete FastAPI Application With ML Integration ===

"""
SecOpsAI Detection API
Serves the XGBoost hardened model with JWT auth, RBAC,
rate limiting, Pydantic validation, and hash-chained audit log.
"""

import os
import time
import logging
from contextlib import asynccontextmanager
from typing import List

import numpy as np
import xgboost as xgb
import joblib
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator, model_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from api.app.auth import (
    get_current_user,
    require_role,
    create_access_token,
    verify_password,
    UserLogin,
    Token
)
from api.app.audit_logger import log_event

# ── Logging ───────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("secopsai.api")

# ── Rate limiter ──────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

# ── Global model state ────────────────────────────────────────────────────
# These are populated at startup and used for every prediction
MODEL_STATE = {
    "model":   None,   # xgb.XGBClassifier
    "scaler":  None,   # sklearn.preprocessing.StandardScaler
    "encoder": None,   # sklearn.preprocessing.LabelEncoder
    "loaded":  False,
    "n_features": 27,
    "classes": [],
}

# ── Model file paths ──────────────────────────────────────────────────────
MODEL_PATH   = os.getenv("MODEL_PATH",   "ml-engine/models/xgboost_hardened.json")
SCALER_PATH  = os.getenv("SCALER_PATH",  "ml-engine/models/scaler.joblib")
ENCODER_PATH = os.getenv("ENCODER_PATH", "ml-engine/models/label_encoder.joblib")


# ── Startup / shutdown lifecycle ──────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the ML model on startup, clean up on shutdown."""
    logger.info("Starting SecOpsAI Detection API...")

    try:
        # Load XGBoost hardened model
        model = xgb.XGBClassifier()
        model.load_model(MODEL_PATH)
        logger.info(f"Model loaded from: {MODEL_PATH}")

        # Load StandardScaler
        scaler = joblib.load(SCALER_PATH)
        logger.info(f"Scaler loaded from: {SCALER_PATH}")

        # Load LabelEncoder
        encoder = joblib.load(ENCODER_PATH)
        logger.info(f"Encoder loaded. Classes: {list(encoder.classes_)}")

        # Warm up the model with a dummy prediction
        dummy = np.zeros((1, model.n_features_in_), dtype=np.float32)
        model.predict(scaler.transform(dummy))
        logger.info("Model warm-up prediction successful")

        MODEL_STATE["model"]      = model
        MODEL_STATE["scaler"]     = scaler
        MODEL_STATE["encoder"]    = encoder
        MODEL_STATE["loaded"]     = True
        MODEL_STATE["n_features"] = model.n_features_in_
        MODEL_STATE["classes"]    = list(encoder.classes_)

        logger.info("✅ API startup complete — model ready for inference")

    except FileNotFoundError as e:
        logger.error(f"❌ Model file not found: {e}")
        logger.error("   Confirm Sub-Team 3 has saved the hardened model")
        MODEL_STATE["loaded"] = False

    except Exception as e:
        logger.error(f"❌ Model loading failed: {e}")
        MODEL_STATE["loaded"] = False

    yield  # API runs here

    # Shutdown
    logger.info("Shutting down SecOpsAI Detection API")
    MODEL_STATE["model"]  = None
    MODEL_STATE["loaded"] = False


# ── FastAPI app ────────────────────────────────────────────────────────────
app = FastAPI(
    title="SecOpsAI Detection API",
    description="AI-powered behavioral threat detection — XGBoost + IBM ART hardened",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


# ── Pydantic models ───────────────────────────────────────────────────────
class DetectionRequest(BaseModel):
    """
    27 network flow features for threat classification.
    All values must be numeric and bounded to [-100, 100]
    after StandardScaler normalization.
    extra='forbid' blocks any undeclared fields (OWASP API3 mitigation).
    """
    features: List[float] = Field(
        ...,
        min_length=27,
        max_length=27,
        description="Exactly 27 normalized network flow features"
    )

    @field_validator('features')
    @classmethod
    def validate_feature_range(cls, v):
        for i, val in enumerate(v):
            if not (-100.0 <= val <= 100.0):
                raise ValueError(
                    f"Feature[{i}] = {val} out of bounds [-100, 100]. "
                    f"Ensure features are StandardScaler normalized."
                )
            if val != val:  # NaN check
                raise ValueError(f"Feature[{i}] is NaN — not permitted")
        return v

    model_config = {"extra": "forbid"}  # OWASP API3: reject unknown fields


class DetectionResponse(BaseModel):
    """Response from the /detect endpoint."""
    threat_class:         str
    threat_score:         float
    confidence_scores:    dict
    alert_triggered:      bool
    alert_threshold:      float
    inference_latency_ms: float
    model_version:        str


class HealthResponse(BaseModel):
    """Response from the /health endpoint."""
    status:         str
    model_loaded:   bool
    model_version:  str
    n_classes:      int
    classes:        list
    api_version:    str


# ── Alert threshold ───────────────────────────────────────────────────────
ALERT_THRESHOLD = float(os.getenv("ALERT_THRESHOLD", "0.70"))
MODEL_VERSION   = os.getenv("MODEL_VERSION", "xgboost-hardened-v1.0")


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Public health check endpoint.
    Returns model load status — critical for demo verification.
    No authentication required.
    """
    return HealthResponse(
        status       = "healthy" if MODEL_STATE["loaded"] else "degraded",
        model_loaded = MODEL_STATE["loaded"],
        model_version= MODEL_VERSION,
        n_classes    = len(MODEL_STATE["classes"]),
        classes      = MODEL_STATE["classes"],
        api_version  = "1.0.0",
    )


@app.post("/auth/token", response_model=Token, tags=["Authentication"])
@limiter.limit("10/minute")  # Brute force protection
async def login(request: Request, credentials: UserLogin):
    """
    Authenticate and receive a JWT bearer token.
    Rate limited to 10 requests/minute per IP.
    """
    # In production this queries the users table in PostgreSQL
    # For demo: hardcoded credentials per role
    DEMO_USERS = {
        "analyst":  {"password": "SecOpsAI@Demo2024!", "role": "analyst"},
        "engineer": {"password": "SecOpsAI@Demo2024!", "role": "engineer"},
        "admin":    {"password": "SecOpsAI@Demo2024!", "role": "admin"},
    }

    user = DEMO_USERS.get(credentials.username)
    if not user or not verify_password(credentials.password, user["password"]):
        log_event(
            endpoint="/auth/token",
            method="POST",
            user_id=credentials.username,
            response_code=401,
            detail="Invalid credentials"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        data={"sub": credentials.username, "role": user["role"]}
    )

    log_event(
        endpoint="/auth/token",
        method="POST",
        user_id=credentials.username,
        response_code=200,
        detail=f"Login successful — role: {user['role']}"
    )

    return Token(access_token=token, token_type="bearer")


@app.post("/detect", response_model=DetectionResponse, tags=["Detection"])
@limiter.limit("100/minute")  # STRIDE T04: rate exhaustion protection
async def detect(
    request: Request,
    body: DetectionRequest,
    current_user: dict = Depends(require_role(["analyst", "engineer", "admin"]))
):
    """
    Run ML inference on 27 network flow features.
    Returns threat classification, confidence scores, and alert status.
    Requires: analyst, engineer, or admin role JWT.
    Rate limited: 100 requests/minute per IP.
    """
    # Guard: model must be loaded
    if not MODEL_STATE["loaded"] or MODEL_STATE["model"] is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded — check startup logs"
        )

    start_time = time.perf_counter()

    try:
        # Step 1: Convert features to numpy array
        raw_features = np.array(body.features, dtype=np.float32).reshape(1, -1)

        # Step 2: Apply the same StandardScaler used during training
        # This is critical — the model was trained on scaled features
        scaled_features = MODEL_STATE["scaler"].transform(raw_features)

        # Step 3: Run XGBoost prediction
        pred_class  = int(MODEL_STATE["model"].predict(scaled_features)[0])
        pred_proba  = MODEL_STATE["model"].predict_proba(scaled_features)[0]

        # Step 4: Decode class index to threat category name
        threat_class = MODEL_STATE["encoder"].classes_[pred_class]
        threat_score = float(pred_proba.max())

        # Step 5: Build confidence scores dict (all classes)
        confidence_scores = {
            str(cls): round(float(prob), 4)
            for cls, prob in zip(MODEL_STATE["encoder"].classes_, pred_proba)
        }

        # Step 6: Determine if alert should fire
        alert_triggered = (
            threat_score >= ALERT_THRESHOLD and
            threat_class.lower() != "benign"
        )

        # Step 7: Calculate inference latency
        latency_ms = (time.perf_counter() - start_time) * 1000

        # Step 8: Log to audit trail (STRIDE T06 mitigation)
        log_event(
            endpoint="/detect",
            method="POST",
            user_id=current_user["sub"],
            response_code=200,
            detail=(
                f"threat_class={threat_class} "
                f"score={threat_score:.4f} "
                f"alert={alert_triggered} "
                f"latency={latency_ms:.2f}ms"
            )
        )

        return DetectionResponse(
            threat_class         = threat_class,
            threat_score         = round(threat_score, 4),
            confidence_scores    = confidence_scores,
            alert_triggered      = alert_triggered,
            alert_threshold      = ALERT_THRESHOLD,
            inference_latency_ms = round(latency_ms, 2),
            model_version        = MODEL_VERSION,
        )

    except Exception as e:
        logger.error(f"Inference error: {e}")
        log_event(
            endpoint="/detect",
            method="POST",
            user_id=current_user.get("sub", "unknown"),
            response_code=500,
            detail=f"Inference error: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Inference failed — check model state"
        )


@app.get("/model/info", tags=["Model"])
@limiter.limit("30/minute")
async def model_info(
    request: Request,
    current_user: dict = Depends(require_role(["engineer", "admin"]))
):
    """
    Return model metadata and feature information.
    Requires: engineer or admin role JWT.
    """
    if not MODEL_STATE["loaded"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )

    log_event(
        endpoint="/model/info",
        method="GET",
        user_id=current_user["sub"],
        response_code=200,
        detail="Model info accessed"
    )

    return {
        "model_version":  MODEL_VERSION,
        "model_type":     "XGBoost (hardened)",
        "hardening":      "FGSM adversarial training via PyTorch surrogate",
        "n_features":     MODEL_STATE["n_features"],
        "n_classes":      len(MODEL_STATE["classes"]),
        "classes":        MODEL_STATE["classes"],
        "alert_threshold": ALERT_THRESHOLD,
        "feature_groups": {
            "A_basic_flow":       "indices 0-7  (duration, bytes, packets, protocol)",
            "B_behavioral_timing":"indices 8-12 (IAT mean, std, CV — beaconing)",
            "C_dns_tunnel_proxy": "indices 13-17 (packet sizes — DNS tunneling)",
            "D_comm_patterns":    "indices 18-23 (TCP flags — lateral movement)",
            "E_volume_rate":      "indices 24-26 (bytes/s, down/up ratio — exfil)",
        }
    }


@app.get("/audit-logs", tags=["Compliance"])
@limiter.limit("10/minute")
async def get_audit_logs(
    request: Request,
    limit: int = 50,
    current_user: dict = Depends(require_role(["admin"]))
):
    """
    Return recent audit log entries.
    Requires: admin role JWT only.
    Rate limited: 10 requests/minute.
    """
    from api.app.audit_logger import get_recent_events

    log_event(
        endpoint="/audit-logs",
        method="GET",
        user_id=current_user["sub"],
        response_code=200,
        detail=f"Audit log accessed — limit={limit}"
    )

    entries = get_recent_events(limit=min(limit, 100))
    return {
        "total_returned": len(entries),
        "entries": entries
    }
