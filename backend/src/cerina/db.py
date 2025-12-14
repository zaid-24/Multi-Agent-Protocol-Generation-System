from sqlalchemy import create_engine, Column, String, DateTime, Text, Float, Integer, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import json

Base = declarative_base()
DB_URL = "sqlite:///cerina_graph.db"

class RunSession(Base):
    __tablename__ = "run_sessions"
    id = Column(String, primary_key=True)  # can reuse session_id or uuid
    session_id = Column(String, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    status = Column(String)

class AgentRun(Base):
    __tablename__ = "agent_runs"
    id = Column(String, primary_key=True)
    session_id = Column(String, index=True)
    agent_name = Column(String)
    input_snapshot = Column(JSON)
    output_snapshot = Column(JSON)
    duration_ms = Column(Float)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Event(Base):
    __tablename__ = "events"
    id = Column(String, primary_key=True)
    session_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String)
    payload_json = Column(JSON)

def get_engine():
    return create_engine(DB_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())

def init_db():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
