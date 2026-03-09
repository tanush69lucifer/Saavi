from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel
import datetime
import json

import database
import logging

# Set up logging to file
logging.basicConfig(
    filename='e:/Neuro/backend/api_debug.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = FastAPI(title="NeuroBand Backend API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- WebSockets Connection Manager ---
class ConnectionManager:
    def __init__(self):
        # Maps user_id to active WebSocket
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def broadcast_anomaly(self, message: dict):
        # Broadcast the alert to all connected dashboards (Family members)
        for connection in self.active_connections.values():
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                pass

manager = ConnectionManager()

# --- WebSockets Endpoint ---
@app.websocket("/ws/dashboard/{user_id}")
async def websocket_dashboard(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive, listen for messages if needed
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)


# --- Pydantic Schemas ---
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: Optional[database.UserRole] = database.UserRole.patient

class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: database.UserRole
    
    class Config:
        from_attributes = True

class SignalCreate(BaseModel):
    value: float
    status: str
    timestamp: Optional[datetime.datetime] = None
    patient_id: int

class SignalResponse(BaseModel):
    id: int
    value: float
    status: str
    timestamp: datetime.datetime
    patient_id: int
    
    class Config:
        from_attributes = True

# --- Auth Routes ---
@app.post("/api/auth/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    logging.info(f"REGISTRATION ATTEMPT: {user.email}")
    db_user = db.query(database.User).filter(database.User.email == user.email).first()
    if db_user:
        logging.warning(f"REGISTRATION FAILED: Email {user.email} already exists")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Simple plain-text password for prototyping (USE HASHING IN PROD!)
    new_user = database.User(
        name=user.name,
        email=user.email,
        hashed_password=user.password, # Replace with bcrypt
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logging.info(f"REGISTRATION SUCCESS: {user.email} (ID: {new_user.id})")
    return new_user


@app.post("/api/auth/login", response_model=UserResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    logging.info(f"LOGIN ATTEMPT: {user.email}")
    # Very basic login (no JWT yet for simplicity)
    db_user = db.query(database.User).filter(database.User.email == user.email).first()
    if not db_user:
        logging.warning(f"LOGIN FAILED: User {user.email} not found in database")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if db_user.hashed_password != user.password:
        logging.warning(f"LOGIN FAILED: Password mismatch for {user.email}. Expected: {db_user.hashed_password[:3]}..., Got: {user.password[:3]}...")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    logging.info(f"LOGIN SUCCESS: {user.email}")
    return db_user


# --- Signal Routes ---
@app.post("/api/signals", response_model=SignalResponse)
async def upload_signal(signal: SignalCreate, db: Session = Depends(get_db)):
    db_signal = database.NeuroSignal(
        patient_id=signal.patient_id,
        value=signal.value,
        status=signal.status,
        timestamp=signal.timestamp or datetime.datetime.utcnow()
    )
    db.add(db_signal)
    db.commit()
    db.refresh(db_signal)

    # Trigger Broadcast if it's an anomaly
    if signal.status.lower() != "normal":
        alert_payload = {
            "type": "anomaly_alert",
            "value": signal.value,
            "status": signal.status,
            "patient_id": signal.patient_id,
            "timestamp": db_signal.timestamp.isoformat()
        }
        await manager.broadcast_anomaly(alert_payload)

    return db_signal

@app.get("/api/signals/{patient_id}", response_model=List[SignalResponse])
def get_signals(patient_id: int, limit: int = 100, db: Session = Depends(get_db)):
    signals = db.query(database.NeuroSignal)\
        .filter(database.NeuroSignal.patient_id == patient_id)\
        .order_by(database.NeuroSignal.timestamp.desc())\
        .limit(limit).all()
    return signals

@app.get("/")
def health_check():
    return {"status": "ok", "message": "NeuroBand Backend Sync is Running!"}
