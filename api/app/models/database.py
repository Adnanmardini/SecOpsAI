from sqlalchemy import create_engine, Column, String, Float, Boolean 
from sqlalchemy import Integer, BigInteger, DateTime, Text, ForeignKey 
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB 
from sqlalchemy.orm import declarative_base, sessionmaker 
from sqlalchemy.sql import func 
import uuid 
import os 
 
DATABASE_URL = ( 
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}" 
    f"@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}" 
    f"/{os.getenv('POSTGRES_DB')}" 
) 
 
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20) 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 
Base = declarative_base() 
 
 
def get_db(): 
    """FastAPI dependency — yields a DB session and closes it after use.""" 
    db = SessionLocal() 
    try: 
        yield db 
    finally: 
        db.close() 
 
 
class User(Base): 
    __tablename__ = "users" 
    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) 
    username      = Column(String(64), unique=True, nullable=False) 
    email         = Column(String(256), unique=True, nullable=False) 
    password_hash = Column(String(256), nullable=False) 
    role          = Column(String(32), nullable=False, default='analyst') 
    is_active     = Column(Boolean, nullable=False, default=True) 
    created_at    = Column(DateTime(timezone=True), server_default=func.now()) 
 
 
class NetworkFlow(Base): 
    __tablename__ = "network_flows" 
    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) 
    flow_uid       = Column(String(64)) 
    timestamp      = Column(DateTime(timezone=True), nullable=False) 
    src_ip         = Column(INET) 
    dst_ip         = Column(INET) 
    src_port       = Column(Integer) 
    dst_port       = Column(Integer) 
    protocol       = Column(String(16)) 
    duration       = Column(Float) 
    total_bytes    = Column(BigInteger) 
    feature_vector = Column(JSONB) 
    record_hash    = Column(String(64), nullable=False) 
    ingested_at    = Column(DateTime(timezone=True), server_default=func.now()) 
 
 
class DetectionResult(Base): 
    __tablename__ = "detection_results" 
    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) 
    flow_id         = Column(UUID(as_uuid=True), ForeignKey("network_flows.id")) 
    timestamp       = Column(DateTime(timezone=True), server_default=func.now()) 
    threat_score    = Column(Float, nullable=False) 
    threat_class    = Column(String(64)) 
    confidence      = Column(Float) 
    model_version   = Column(String(32)) 
    rule_fired      = Column(Boolean, default=False) 
    rule_name       = Column(String(128)) 
    is_true_positive = Column(Boolean) 
 
 
class SecurityAlert(Base): 
    __tablename__ = "security_alerts" 
    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) 
    detection_id        = Column(UUID(as_uuid=True), ForeignKey("detection_results.id")) 
    timestamp           = Column(DateTime(timezone=True), server_default=func.now()) 
    severity            = Column(String(16), nullable=False) 
    status              = Column(String(32), nullable=False, default='open') 
    vt_malicious_count  = Column(Integer) 
    shodan_ports        = Column(JSONB) 
    shodan_country      = Column(String(64)) 
    containment_action  = Column(String(128)) 
    email_notified      = Column(Boolean, default=False) 
    alert_hash          = Column(String(64), nullable=False) 
 
 
class AuditLog(Base): 
    __tablename__ = "audit_log" 
    id                   = Column(BigInteger, primary_key=True, autoincrement=True) 
    log_id               = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False) 
    timestamp            = Column(DateTime(timezone=True), server_default=func.now()) 
    user_id              = Column(UUID(as_uuid=True)) 
    endpoint             = Column(String(256)) 
    http_method          = Column(String(16)) 
    source_ip            = Column(INET) 
    request_hash         = Column(String(64)) 
    response_code        = Column(Integer) 
    inference_latency_ms = Column(Float) 
    threat_score         = Column(Float) 
    entry_hash           = Column(String(64), nullable=False) 
    prev_entry_hash      = Column(String(64), nullable=False)


class ModelVersion(Base): 
    __tablename__ = "model_versions" 
    version_id      = Column(String(50), primary_key=True) 
    model_name      = Column(String(100), nullable=False) 
    framework       = Column(String(50), nullable=False) 
    hyperparameters = Column(JSONB, nullable=False) 
    metrics         = Column(JSONB, nullable=False) 
    status          = Column(String(20), nullable=False, default='staged') 
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    
