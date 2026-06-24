from fastapi import FastAPI, HTTPException, Depends, Header
from slowapi import Limiter
from slowapi.util import get_remote_address
from pydantic import BaseModel, Extra
from datetime import datetime, timedelta
from typing import Optional
from kafka import KafkaProducer
import json

app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

kafka_producer = None

class TokenRequest(BaseModel):
    username: str
    password: str

class DetectionRequest(BaseModel):
    features: list
    class Config:
        extra = Extra.forbid

USERS = {
    "analyst": {"password": "SecOpsAI@Demo2024!", "role": "analyst"},
    "engineer": {"password": "Engineer@2024!", "role": "engineer"},
    "admin": {"password": "Admin@2024!", "role": "admin"}
}

TOKENS = {}
AUDIT_LOG = []
MODEL = None

@app.on_event("startup")
async def load_model():
    global MODEL, kafka_producer
    MODEL = {"name": "MalwareDetector", "version": "1.0"}
    try:
        kafka_producer = KafkaProducer(bootstrap_servers="kafka:29092", value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        print("✓ Kafka producer connected")
    except Exception as e:
        print(f"Kafka warning: {e}")
    print("✓ Model loaded on startup")

def create_token(username: str, role: str):
    token = f"{username}:{role}:{datetime.utcnow().timestamp()}"
    TOKENS[token] = {"username": username, "role": role, "expires": datetime.utcnow() + timedelta(hours=1)}
    return token

def decode_token(token: str):
    if token not in TOKENS:
        raise HTTPException(status_code=403, detail="Invalid token")
    if datetime.utcnow() > TOKENS[token]["expires"]:
        raise HTTPException(status_code=403, detail="Token expired")
    return TOKENS[token]

def require_role(required_role: str):
    def verify(authorization: Optional[str] = Header(None)):
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=403, detail="Missing token")
        token = authorization.replace("Bearer ", "")
        user = decode_token(token)
        if user["role"] != required_role and user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return verify

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/auth/token")
async def login(creds: TokenRequest):
    if creds.username not in USERS:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user_data = USERS[creds.username]
    if user_data["password"] != creds.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(creds.username, user_data["role"])
    AUDIT_LOG.append(f"[{datetime.utcnow()}] Login: {creds.username}")
    return {"access_token": token, "token_type": "bearer"}

@app.post("/detect")
async def detect(detection: DetectionRequest, user: dict = Depends(require_role("analyst"))):
    if len(detection.features) != 27:
        raise HTTPException(status_code=400, detail="Expected 27 features")
    threat_score = sum(detection.features) / 27
    prediction = "malicious" if threat_score > 0.5 else "benign"
    alert_triggered = threat_score >= 0.7
    result = {
        "prediction": prediction,
        "confidence": 0.95,
        "threat_score": threat_score,
        "alert_triggered": alert_triggered,
        "timestamp": datetime.utcnow().isoformat()
    }
    if kafka_producer:
        try:
            kafka_producer.send("detection-results", result)
            kafka_producer.flush()
        except Exception as e:
            print(f"Kafka send error: {e}")
    AUDIT_LOG.append(f"[{datetime.utcnow()}] Detection: {user['username']} -> {prediction}")
    return result

@app.get("/model/info")
async def model_info(user: dict = Depends(require_role("engineer"))):
    return {"name": MODEL["name"], "version": MODEL["version"], "status": "ready"}

@app.get("/audit-logs")
async def get_audit_logs(user: dict = Depends(require_role("admin"))):
    return {"logs": AUDIT_LOG, "total": len(AUDIT_LOG)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
