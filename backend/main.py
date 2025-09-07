from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
import jwt

# =========================
# CONFIG
# =========================
MYSQL_USER = "root"
MYSQL_PASSWORD = "6304962908%40Sss"
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_DB = "hospital_db1"

DATABASE_URL_ROOT = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/"
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

SECRET_KEY = "please_change_this_secret_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# =========================
# DB INIT (create DB if not exists, then connect)
# =========================
_engine_root = create_engine(
    DATABASE_URL_ROOT, pool_pre_ping=True, future=True
)

with _engine_root.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB}"))
    conn.commit()

engine = create_engine(
    DATABASE_URL, pool_pre_ping=True, future=True
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

# =========================
# SECURITY
# =========================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/hospital/login")

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# =========================
# MODELS (SQLAlchemy)
# =========================
class Hospital(Base):
    __tablename__ = "hospitals"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=False)

    doctors = relationship("Doctor", back_populates="hospital", cascade="all, delete-orphan")

class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    specialty = Column(String(255), nullable=False)
    contact = Column(String(255), nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False)

    hospital = relationship("Hospital", back_populates="doctors")

Base.metadata.create_all(bind=engine)

# =========================
# SCHEMAS (Pydantic)
# =========================
class HospitalCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class HospitalLogin(BaseModel):
    email: EmailStr
    password: str

class HospitalResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    class Config:
        orm_mode = True

class DoctorCreate(BaseModel):
    name: str
    specialty: str
    contact: str

class DoctorUpdate(BaseModel):
    name: Optional[str] = None
    specialty: Optional[str] = None
    contact: Optional[str] = None

class DoctorResponse(BaseModel):
    id: int
    name: str
    specialty: str
    contact: str
    hospital_id: int
    class Config:
        orm_mode = True

# =========================
# APP
# =========================
app = FastAPI(title="Hospital & Doctor Management API (FastAPI + MySQL)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# DB DEP
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# AUTH HELPERS
# =========================
def get_current_hospital(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Hospital:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        hospital_id_str = payload.get("sub")
        if hospital_id_str is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        hospital_id = int(hospital_id_str)
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    hospital = db.get(Hospital, hospital_id)
    if not hospital:
        raise HTTPException(status_code=401, detail="Hospital not found")
    
    return hospital

# =========================
# CONTROLLERS / ROUTES
# =========================

# ---- Hospital Authentication ----
@app.post("/hospital/register", response_model=HospitalResponse)
def register_hospital(payload: HospitalCreate, db: Session = Depends(get_db)):
    exists = db.query(Hospital).filter(Hospital.email == payload.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")

    hospital = Hospital(
        name=payload.name,
        email=payload.email,
        password=hash_password(payload.password)
    )
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    return hospital

@app.post("/hospital/login")
def hospital_login(payload: HospitalLogin, db: Session = Depends(get_db)):
    hospital: Hospital = db.query(Hospital).filter(Hospital.email == payload.email).first()
    if not hospital:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(payload.password, hospital.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(hospital.id)})
    return {
        "access_token": token,
        "token_type": "bearer",
        "hospital": {"id": hospital.id, "name": hospital.name, "email": hospital.email},
    }

# ---- Protected Doctor Management ----
@app.post("/doctors", response_model=DoctorResponse)
def add_doctor(doc: DoctorCreate, current_hospital: Hospital = Depends(get_current_hospital), db: Session = Depends(get_db)):
    new_doc = Doctor(
        name=doc.name,
        specialty=doc.specialty,
        contact=doc.contact,
        hospital_id=current_hospital.id
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc

@app.get("/doctors", response_model=List[DoctorResponse])
def list_doctors(current_hospital: Hospital = Depends(get_current_hospital), db: Session = Depends(get_db)):
    doctors = db.query(Doctor).filter(Doctor.hospital_id == current_hospital.id).all()
    return doctors

@app.put("/doctors/{doctor_id}", response_model=DoctorResponse)
def update_doctor(doctor_id: int, doc: DoctorUpdate, current_hospital: Hospital = Depends(get_current_hospital), db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id, Doctor.hospital_id == current_hospital.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    if doc.name is not None:
        doctor.name = doc.name
    if doc.specialty is not None:
        doctor.specialty = doc.specialty
    if doc.contact is not None:
        doctor.contact = doc.contact

    db.commit()
    db.refresh(doctor)
    return doctor

@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int, current_hospital: Hospital = Depends(get_current_hospital), db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id, Doctor.hospital_id == current_hospital.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    db.delete(doctor)
    db.commit()
    return {"message": "Doctor deleted successfully"}

# =========================
# DEBUG ENDPOINTS
# =========================
@app.get("/debug/test-token")
def debug_test_token():
    test_payload = {"sub": "999", "test": "debug"}
    test_token = create_access_token(test_payload)
    
    try:
        decoded = jwt.decode(test_token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "token_created": test_token,
            "token_decoded": decoded,
            "secret_key": SECRET_KEY,
            "status": "success"
        }
    except Exception as e:
        return {
            "token_created": test_token,
            "error": str(e),
            "secret_key": SECRET_KEY,
            "status": "failed"
        }

@app.get("/debug/check-db")
def debug_check_db(db: Session = Depends(get_db)):
    try:
        hospital_count = db.query(Hospital).count()
        doctor_count = db.query(Doctor).count()
        return {
            "db_connection": "success",
            "hospital_count": hospital_count,
            "doctor_count": doctor_count
        }
    except Exception as e:
        return {"db_connection": "failed", "error": str(e)}

@app.get("/debug/check-token")
def debug_check_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"token_valid": True, "payload": payload}
    except jwt.ExpiredSignatureError:
        return {"token_valid": False, "error": "Token expired"}
    except jwt.InvalidTokenError:
        return {"token_valid": False, "error": "Invalid token"}
    except Exception as e:
        return {"token_valid": False, "error": str(e)}

@app.get("/debug/hospitals")
def debug_list_hospitals(db: Session = Depends(get_db)):
    hospitals = db.query(Hospital).all()
    return [{"id": h.id, "name": h.name, "email": h.email} for h in hospitals]

@app.get("/")
def root():
    return {"status": "ok", "name": "Hospital & Doctor Management API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)