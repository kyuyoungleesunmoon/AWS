# AWS EC2 + RDS + FastAPI 실습 가이드 (완전판)

이 가이드는 `AWS_Beginner_Guide.md`를 통해 EC2와 RDS가 생성된 상태에서 시작합니다.
작은 실수 하나 없이 한 번에 성공할 수 있도록 모든 명령어를 순서대로 작성했습니다.

**목표**: 내 컴퓨터 브라우저에서 AWS 서버 주소를 쳤을 때, 데이터베이스에 글을 쓰고 읽을 수 있는 페이지(Swagger UI)가 뜨게 만드는 것.

---

## 1. 사전 준비: 외부 접속 포트 열기 (보안 그룹)
서버를 띄워도 문(Port)이 잠겨 있으면 접속할 수 없습니다.

1.  **EC2 콘솔** 접속 -> 왼쪽 메뉴 **[보안 그룹]** 클릭.
2.  `web-server-sg` (EC2에 연결된 보안 그룹) 이름을 클릭.
3.  화면 하단 **[인바운드 규칙]** 탭 -> **[인바운드 규칙 편집]** 클릭.
4.  **[규칙 추가]** 버튼 클릭.
    *   **유형**: `사용자 지정 TCP`
    *   **포트 범위**: `8000` (FastAPI가 사용할 문)
    *   **소스**: `위치 무관 (0.0.0.0/0)`
5.  **[규칙 저장]** 클릭.

---

## 2. EC2 접속 및 시스템 업데이트
Windows PowerShell을 열고 서버에 접속합니다.

### 2-1. 접속 (이미 켜져 있다면 생략 가능)
```powershell
# C:\AWS 폴더에 키가 있다고 가정합니다.
ssh -i "C:\AWS\my-ec2-key.pem" ec2-user@<본인의-EC2-퍼블릭-IP>
```
*(접속 후 `[ec2-user@ip-...]` 프롬프트가 떠야 합니다.)*

### 2-2. 리눅스 패키지 업데이트 및 DB 클라이언트 설치
터미널에 아래 명령어를 한 줄씩 복사해 붙여넣고 엔터(Enter)를 치세요.
```bash
# 1. 시스템을 최신 상태로 업데이트
sudo dnf update -y

# 2. MySQL(MariaDB) 클라이언트 도구 설치
sudo dnf install mariadb105 -y
```

---

## 3. RDS 데이터베이스 생성
RDS는 '서버'일 뿐, 그 안에 실제 데이터를 담을 '방(Database)'을 만들어줘야 합니다.

1.  **RDS 엔드포인트 확인**: AWS 콘솔 -> RDS -> 데이터베이스 -> `mydb` 클릭 -> **연결 및 보안** 탭에서 **엔드포인트** 복사.
2.  **접속 명령어 입력**:
    ```bash
    # <엔드포인트> 지우고 복사한 주소 붙여넣기 (마우스 우클릭)
    mysql -h <엔드포인트> -u admin -p
    ```
3.  **비밀번호 입력**: RDS 생성 때 만든 비밀번호 입력 (타이핑해도 화면에 안 보임) -> 엔터.
4.  **DB 생성 쿼리 입력** (`MySQL [(none)]>` 상태에서):
    ```sql
    CREATE DATABASE demo_db;
    SHOW DATABASES;
    EXIT;
    ```
    *   `demo_db`가 보이면 성공입니다. `EXIT`로 빠져나옵니다.

---

## 4. Python 가상 환경 구축 (가장 중요)
서버의 Python 환경을 더럽히지 않기 위해 '가상 환경(venv)'을 만듭니다.

### 4-1. 가상 환경 생성 및 활성화
```bash
# 1. 홈 디렉토리로 이동
cd ~

# 2. 'venv'라는 이름의 가상 환경 생성
python3 -m venv venv

# 3. 가상 환경 켜기 (이걸 안 하면 라이브러리가 꼬입니다!)
source venv/bin/activate
```
**확인**: 명령어 입력 줄 맨 앞에 `(venv)`라는 글자가 보여야 합니다.
*(만약 나중에 터미널을 껐다 다시 켜면, 반드시 `source venv/bin/activate`를 다시 해줘야 합니다.)*

### 4-2. 필수 라이브러리 설치
협업 표준인 `requirements.txt`를 사용합니다.

1.  **파일 생성**:
    ```bash
    nano requirements.txt
    ```
2.  **내용 붙여넣기**: 아래 내용을 복사한 뒤 터미널에 마우스 우클릭으로 붙여넣으세요.
    ```text
    fastapi
    uvicorn
    sqlalchemy
    pymysql
    pydantic
    cryptography
    ```
3.  **저장 및 종료**: `Ctrl + O` (저장) -> `Enter` -> `Ctrl + X` (종료).
4.  **설치 실행**:
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

---

## 5. 소스 코드 작성 (main.py)
이제 실제 서버 코드를 작성합니다.

1.  **파일 열기**:
    ```bash
    nano main.py
    ```
2.  **코드 복사**: 아래 코드를 모두 복사해서 붙여넣으세요.
    **[중요]**: 붙여넣은 후 키보드 화살표 키로 이동해 `RDS_HOST`와 `RDS_PASSWORD`를 본인 것으로 수정해야 합니다.

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import pymysql

# ==========================================
# [설정 영역] 본인의 RDS 정보로 수정하세요
# ==========================================
RDS_HOST = "여기에-RDS-엔드포인트를-붙여넣으세요"
RDS_USER = "admin"
RDS_PASSWORD = "여기에-비밀번호를-입력하세요"
RDS_DB_NAME = "demo_db"

# DB 연결 URL
DATABASE_URL = f"mysql+pymysql://{RDS_USER}:{RDS_PASSWORD}@{RDS_HOST}:3306/{RDS_DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 테이블 모델
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)

Base.metadata.create_all(bind=engine)

# 데이터 검증 모델
class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    class Config:
        from_attributes = True

# FastAPI 앱
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Connection Successful!"}

@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/", response_model=list[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "Deleted"}
```
3.  **저장 및 종료**: `Ctrl + O` -> `Enter` -> `Ctrl + X`.

---

## 6. 서버 실행 및 최종 확인
모든 준비가 끝났습니다. 서버를 켭니다.

1.  **실행 명령어**:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```
    *   `Application startup complete.`가 뜨면 성공! (이제 이 터미널은 끄지 말고 놔두세요.)

2.  **내 PC에서 접속**:
    *   브라우저 주소창: `http://<내-EC2-퍼블릭-IP>:8000/docs`
    *   **결과**: 파란색 Swagger UI 화면이 뜹니다.

3.  **테스트**:
    *   **POST /users/** -> **Try it out** -> 데이터 입력 -> **Execute**.
    *   `Code 200`이 뜨면 RDS에 데이터가 안전하게 저장된 것입니다.

---

### [Tip] 문제 해결 가이드
*   **터미널을 껐다가 다시 하려니 안 돼요!**
    *   다시 접속한 뒤 반드시 `source venv/bin/activate`를 입력해 `(venv)` 상태를 만들어야 합니다.
*   **`Internal Server Error` 발생**:
    *   대부분 `main.py` 안의 `RDS_HOST`나 `RDS_PASSWORD` 오타입니다.
    *   `Ctrl+C`로 서버를 끄고 `nano main.py`로 다시 수정하세요.
*   **`Can't connect to MySQL server` 에러**:
    *   1번 가이드에서 RDS 생성 시 'EC2 연결'을 안 했거나, EC2 보안 그룹 설정이 꼬인 경우입니다.
    *   RDS 보안 그룹의 인바운드 규칙에 '내 EC2의 보안 그룹 ID'가 허용되어 있는지 확인해야 합니다.