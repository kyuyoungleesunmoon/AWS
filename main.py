# ============================================================
# [EC2 호환성 패치] ChromaDB를 위한 SQLite3 버전 강제 교체
# (이 코드는 반드시 다른 import보다 가장 위에 있어야 합니다)
# ============================================================
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules['pysqlite3']

import os
import shutil
from typing import List

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import pymysql
from dotenv import load_dotenv

# RAG 관련 라이브러리
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA

# ============================================================
# 1. 환경 설정 및 보안 (API Key 로드)
# ============================================================
# .env 파일에서 환경 변수 로드
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
RDS_HOST = os.getenv("RDS_HOST")
RDS_USER = os.getenv("RDS_USER")
RDS_PASSWORD = os.getenv("RDS_PASSWORD")
RDS_DB_NAME = os.getenv("RDS_DB_NAME", "demo_db")

# 필수 정보 누락 확인
if not OPENAI_API_KEY:
    print("[경고] OPENAI_API_KEY가 설정되지 않았습니다. RAG 기능이 작동하지 않을 수 있습니다.")

# ============================================================
# 2. 데이터베이스 설정 (RDS MySQL)
# ============================================================
DATABASE_URL = f"mysql+pymysql://{RDS_USER}:{RDS_PASSWORD}@{RDS_HOST}:3306/{RDS_DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)

Base.metadata.create_all(bind=engine)

# ============================================================
# 3. RAG(AI) 설정 (ChromaDB + OpenAI)
# ============================================================
# 벡터 데이터 저장 경로 (EC2 내부 폴더)
PERSIST_DIRECTORY = "./chroma_db"

# 임베딩 모델 (텍스트 -> 숫자 변환)
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# 벡터 저장소 초기화
vector_store = Chroma(
    persist_directory=PERSIST_DIRECTORY,
    embedding_function=embeddings
)

# LLM 모델 설정 (gpt-3.5-turbo)
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0, # 사실 기반 답변을 위해 창의성 낮춤
    openai_api_key=OPENAI_API_KEY
)

# ============================================================
# 4. Pydantic 스키마 & FastAPI 앱
# ============================================================
class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    class Config:
        from_attributes = True

class RagQuery(BaseModel):
    question: str

class RagResponse(BaseModel):
    answer: str
    source_documents: List[str]

app = FastAPI(title="AWS EC2: CRUD + RAG AI System")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================
# 5. API 엔드포인트
# ============================================================

@app.get("/")
def read_root():
    return {"status": "online", "message": "AWS RAG System Ready"}

# --- [Part 1] 기존 CRUD API ---
@app.post("/users/", response_model=UserResponse, tags=["Users"])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")
    new_user = User(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/", response_model=list[UserResponse], tags=["Users"])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()

# --- [Part 2] RAG (문서 검색 AI) API ---

@app.post("/rag/upload", tags=["AI RAG"])
async def upload_document(file: UploadFile = File(...)):
    """
    [문서 학습] PDF 또는 DOCX 파일을 업로드하여 AI에게 학습시킵니다.
    """
    # 1. 파일 임시 저장
    temp_dir = "temp_files"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. 파일 로드 (확장자에 따른 분기)
    try:
        if file.filename.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif file.filename.endswith(".docx"):
            loader = Docx2txtLoader(file_path)
        else:
            raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다. (PDF, DOCX만 가능)")
        
        documents = loader.load()
        
        # 3. 텍스트 분할 (Chunking)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(documents)
        
        # 4. 벡터 저장소에 추가 (학습)
        vector_store.add_documents(chunks)
        
        return {
            "message": "문서 학습이 완료되었습니다.",
            "filename": file.filename,
            "chunks": len(chunks)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"처리 중 오류 발생: {str(e)}")
        
    finally:
        # 5. 임시 파일 삭제 (Clean up)
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/rag/ask", response_model=RagResponse, tags=["AI RAG"])
def ask_question(query: RagQuery):
    """
    [질문하기] 학습된 문서를 바탕으로 질문에 답변합니다.
    """
    try:
        # RetrievalQA 체인 생성
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever(search_kwargs={"k": 3}), # 가장 유사한 문서 3개 참조
            return_source_documents=True
        )
        
        # 질의 실행
        result = qa_chain.invoke({"query": query.question})
        
        # 출처 문서 정리
        sources = [doc.metadata.get('source', 'Unknown') for doc in result.get("source_documents", [])]
        
        return RagResponse(
            answer=result["result"],
            source_documents=list(set(sources)) # 중복 제거
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"답변 생성 실패: {str(e)}")