from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
import enum

SQLALCHEMY_DATABASE_URL = "sqlite:///./neuro.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class UserRole(str, enum.Enum):
    patient = "patient"
    family = "family"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.patient)

class NeuroSignal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"))
    value = Column(Float)
    status = Column(String)  # "normal", "abnormal", "seizure"
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    patient = relationship("User")

# Create tables
Base.metadata.create_all(bind=engine)
