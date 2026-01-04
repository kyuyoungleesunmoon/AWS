# AWS EC2 + RDS + FastAPI 실습 가이드 (완전판)

이 가이드는 `AWS_Beginner_Guide.md`를 통해 EC2와 RDS가 생성된 상태에서 시작합니다.
**"로컬 컴퓨터에서 먼저 개발하고, 완성되면 EC2로 배포"**하는 정석적인 개발 흐름을 따릅니다.

**목표**: 내 PC에서 RDS에 붙어서 코딩을 하고, 테스트가 끝나면 EC2 서버에 올려서 전 세계에 서비스한다.

---

## 1. 사전 준비: 보안 그룹 설정 (문 열기)
서버와 DB는 기본적으로 모든 문을 잠그고 시작합니다. 우리가 들어갈 문을 열어줘야 합니다.

### 1-1. EC2 보안 그룹 (웹 서버 포트 열기)
1.  **EC2 콘솔** -> **[보안 그룹]** -> `web-server-sg` 선택.
2.  **[인바운드 규칙 편집]** -> **[규칙 추가]**.
    *   **유형**: `사용자 지정 TCP` / **포트**: `8000` (FastAPI) / **소스**: `위치 무관 (0.0.0.0/0)`
3.  **[규칙 저장]**.

### 1-2. RDS 보안 그룹 (내 PC 접속 허용)
로컬에서 개발하려면 내 컴퓨터 IP가 DB에 접속할 수 있어야 합니다.
1.  **RDS 콘솔** -> **데이터베이스** -> `mydb` 클릭.
2.  **연결 및 보안** 탭 -> **[VPC 보안 그룹]** 링크 클릭 (예: `sg-xxxxx`).
3.  **[인바운드 규칙]** 탭 -> **[인바운드 규칙 편집]** -> **[규칙 추가]**.
    *   **유형**: `MYSQL/Aurora` (3306)
    *   **소스**: `내 IP` 선택 (자동으로 내 IP가 입력됨)
4.  **[규칙 저장]**.

---

## 2. Phase 1: 로컬 개발 환경 구축 (내 컴퓨터)
먼저 내 컴퓨터(Windows/Mac)에서 코드를 작성하고 실행해봅니다.

### 2-1. Python 및 라이브러리 설치
VS Code 터미널(또는 CMD)을 열고 프로젝트 폴더에서 실행하세요.

```bash
# 가상환경 생성 (선택사항이나 권장)
python -m venv venv
# 윈도우: venv\Scripts\activate
# 맥/리눅스: source venv/bin/activate

# 필수 라이브러리 설치
pip install fastapi uvicorn sqlalchemy pymysql pydantic cryptography
```

### 2-2. 소스 코드 작성 (`main.py`)
아래 코드는 **사용자 관리 기능(생성, 조회, 검색, 수정, 삭제)**을 모두 포함한 확장된 예제입니다.

```python
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import pymysql

# ==========================================
# [설정 영역] RDS 정보 입력
# ==========================================
RDS_HOST = "여기에-RDS-엔드포인트를-붙여넣으세요"
RDS_USER = "admin"
RDS_PASSWORD = "여기에-비밀번호를-입력하세요"
RDS_DB_NAME = "demo_db"

DATABASE_URL = f"mysql+pymysql://{RDS_USER}:{RDS_PASSWORD}@{RDS_HOST}:3306/{RDS_DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- [DB 모델] ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    role = Column(String(20), default="member") # 예: member, admin
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
app = FastAPI(title="AWS FastAPI Demo", description="EC2 + RDS 실습용 API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", summary="헬스 체크")
def read_root():
    return {"status": "ok", "env": "production", "time": datetime.now()}

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
    # 이름에 검색어가 포함된 사용자 찾기
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
```

### 2-3. 로컬 테스트
```bash
uvicorn main:app --reload
```
브라우저에서 `http://127.0.0.1:8000/docs` 접속. DB에 데이터가 잘 들어가는지 확인합니다.

---

## 3. Phase 2: EC2 배포 (실제 서버)
로컬 테스트가 완벽하다면, 이제 코드를 EC2로 옮깁니다.

### 3-1. EC2 접속 (Windows 사용자 필독)
SSH 키 권한 문제(`WARNING: UNPROTECTED PRIVATE KEY FILE!`)를 해결하기 위해 **PowerShell**에서 아래 명령어를 **딱 한 번** 실행하세요.

```powershell
# 1. 상속 권한 제거
icacls "C:\AWS\my-key-2026-2.pem" /inheritance:r
# 2. 현재 사용자에게만 읽기 권한 부여
icacls "C:\AWS\my-key-2026-2.pem" /grant:r "$($env:USERNAME):(R)"
```

이제 접속합니다:
```powershell
ssh -i "C:\AWS\my-key-2026-2.pem" ec2-user@<내-EC2-퍼블릭-IP>
```

### 3-2. 서버 환경 세팅 (한 번만 실행)
```bash
# 업데이트 및 DB 클라이언트 설치
sudo dnf update -y
sudo dnf install mariadb105 -y

# 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 라이브러리 설치
pip install fastapi uvicorn sqlalchemy pymysql pydantic cryptography
```

### 3-3. 코드 배포 (복사 붙여넣기)
가장 간단한 방법은 `nano` 에디터를 쓰는 것입니다.

1.  EC2 터미널에서 `nano main.py` 입력.
2.  로컬에서 작성한(그리고 RDS 정보가 입력된) `main.py` 내용을 전체 복사(Ctrl+A, Ctrl+C).
3.  터미널에 마우스 우클릭으로 붙여넣기.
4.  `Ctrl + O` (저장) -> `Enter` -> `Ctrl + X` (종료).

### 3-4. 서버 실행
```bash
# 백그라운드 실행 아님 (터미널 끄면 꺼짐)
uvicorn main:app --host 0.0.0.0 --port 8000
```
이제 `http://<EC2-IP>:8000/docs`에 접속하면 전 세계 어디서든 내 API를 사용할 수 있습니다!

---

### [Tip] 서버를 계속 켜두고 싶다면? (nohup)
터미널을 꺼도 서버가 죽지 않게 하려면:
```bash
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &
```
*   종료하려면: `pkill uvicorn`