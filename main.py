from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import pymysql

# ============================================================
# [주의] 아래 변수값들을 본인의 AWS RDS 정보에 맞게 수정해야 합니다.
# ============================================================
RDS_HOST = "your-rds-endpoint-here.rds.amazonaws.com"
RDS_USER = "admin"
RDS_PASSWORD = "your-password-here"
RDS_DB_NAME = "demo_db"

# 데이터베이스 연결 URL (MySQL + PyMySQL 엔진 사용)
DATABASE_URL = f"mysql+pymysql://{RDS_USER}:{RDS_PASSWORD}@{RDS_HOST}:3306/{RDS_DB_NAME}"

# SQLAlchemy 엔진 및 세션 설정
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============================================================
# [모델 정의] DB 테이블 구조 (users 테이블)
# ============================================================
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)

# 테이블 자동 생성 (서버 시작 시 실행)
Base.metadata.create_all(bind=engine)

# ============================================================
# [스키마 정의] Pydantic 모델 (입출력 데이터 검증)
# ============================================================
class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    
    class Config:
        from_attributes = True  # SQLAlchemy 모델 객체를 JSON으로 자동 변환

# ============================================================
# [FastAPI 앱 설정]
# ============================================================
app = FastAPI(title="AWS EC2 + RDS CRUD API", version="1.0.0")

# DB 세션 의존성 함수 (요청마다 세션 생성 후 반환)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. 홈 경로 (서버 상태 확인)
@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "AWS EC2 + RDS + FastAPI 서버가 정상적으로 연결되었습니다."
    }

# 2. [Create] 사용자 등록
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # 이메일 중복 확인
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="이미 등록된 이메일 주소입니다.")
    
    # 데이터 저장
    new_user = User(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# 3. [Read] 전체 사용자 조회
@app.get("/users/", response_model=list[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

# 4. [Read] 특정 사용자 상세 조회
@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return user

# 5. [Delete] 사용자 삭제
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="삭제할 사용자를 찾을 수 없습니다.")
    db.delete(user)
    db.commit()
    return {"message": f"User {user_id} deleted successfully."}
