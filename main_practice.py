from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import pymysql
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드 (설정되어 있다면 사용)
load_dotenv()

# ==========================================
# [설정 영역] RDS 정보 입력 (환경변수 또는 직접 입력)
# ==========================================
RDS_HOST = os.getenv("RDS_HOST", "여기에-RDS-엔드포인트를-붙여넣으세요")
RDS_USER = os.getenv("RDS_USER", "admin")
RDS_PASSWORD = os.getenv("RDS_PASSWORD", "여기에-비밀번호를-입력하세요")
RDS_DB_NAME = os.getenv("RDS_DB_NAME", "demo_db")

DATABASE_URL = f"mysql+pymysql://{RDS_USER}:{RDS_PASSWORD}@{RDS_HOST}:3306/{RDS_DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- [DB 모델] ---
class User(Base):
    __tablename__ = "practice_users" # 기존 테이블과 겹치지 않게 변경
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    role = Column(String(20), default="member")
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# --- [Pydantic 모델] ---
class UserCreate(BaseModel):
    name: str
    email: str
    role: str = "member"

class UserUpdate(BaseModel):
    name: str | None = None
    role: str | None = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    created_at: datetime
    class Config:
        from_attributes = True

# --- [FastAPI 앱] ---
app = FastAPI(title="AWS Practice API", description="CRUD 실습용 API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", summary="헬스 체크")
def read_root():
    return {"status": "ok", "mode": "practice", "time": datetime.now()}

# 1. 사용자 생성 (Create)
@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")
    new_user = User(name=user.name, email=user.email, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# 2. 사용자 목록 조회 (Read List)
@app.get("/users/", response_model=list[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()

# 3. 사용자 검색 (Search)
@app.get("/users/search/", response_model=list[UserResponse])
def search_users(name: str, db: Session = Depends(get_db)):
    return db.query(User).filter(User.name.contains(name)).all()

# 4. 사용자 정보 수정 (Update)
@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    if user_update.name:
        db_user.name = user_update.name
    if user_update.role:
        db_user.role = user_update.role
    
    db.commit()
    db.refresh(db_user)
    return db_user

# 5. 사용자 삭제 (Delete)
@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    db.delete(user)
    db.commit()
    return None
