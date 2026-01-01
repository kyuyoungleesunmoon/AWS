# AWS EC2 RAG 시스템 구축 가이드

이 가이드는 `AWS_FastAPI_Guide.md`를 통해 구축된 **EC2 + RDS + FastAPI** 환경에, **OpenAI**와 **ChromaDB**를 연동하여 **RAG(검색 증강 생성)** 기능을 추가하는 심화 단계입니다.

**목표**: PDF나 Word 문서를 업로드하면, AI가 그 내용을 읽고 질문에 답변해 주는 시스템을 만듭니다.

---

## 1. 사전 준비 (OpenAI API Key)
이 실습을 하려면 OpenAI의 유료 API Key가 필요합니다.
1.  [OpenAI Platform](https://platform.openai.com/)에 로그인합니다.
2.  Dashboard -> API keys 메뉴로 이동합니다.
3.  `Create new secret key`를 눌러 키를 생성하고(`sk-...`로 시작), 복사해 둡니다.

---

## 2. 서버 환경 업데이트 (라이브러리 추가)
기존 EC2 서버에 새로운 기능을 위한 라이브러리를 설치합니다.

### 2-1. 서버 접속 및 가상 환경 활성화
Windows PowerShell을 열고 EC2에 접속합니다.
```powershell
ssh -i "C:\AWS\my-ec2-key.pem" ec2-user@<EC2-퍼블릭-IP>
```
접속 후, 반드시 가상 환경을 켭니다.
```bash
source venv/bin/activate
```
*(프롬프트 앞에 `(venv)`가 떠야 합니다)*

### 2-2. requirements.txt 업데이트
AI 관련 라이브러리 목록을 업데이트합니다.
1.  `nano requirements.txt` 입력.
2.  기존 내용을 모두 지우고(`Ctrl+K`를 계속 누르면 한 줄씩 지워짐), 아래 내용을 복사해서 붙여넣습니다.

```text
fastapi
uvicorn
sqlalchemy
pymysql
pydantic
cryptography
python-dotenv
langchain-community
langchain-openai
langchain-text-splitters
chromadb
pypdf
docx2txt
tiktoken
pysqlite3-binary
python-multipart
```
3.  `Ctrl+O` -> `Enter` -> `Ctrl+X` 로 저장 및 종료.

### 2-3. 라이브러리 설치
새로 추가된 라이브러리들을 설치합니다. (시간이 조금 걸립니다)
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 3. 환경 변수 및 보안 설정 (.env)
API Key나 DB 비밀번호 같은 중요 정보는 코드에 직접 쓰지 않고 별도 파일(`.env`)로 관리하는 것이 보안 표준입니다.

1.  `.env` 파일 생성:
    ```bash
    nano .env
    ```
2.  아래 내용을 복사해서 붙여넣고, **[내용 수정]** 부분을 본인 정보로 바꿔주세요.
    ```ini
    # OpenAI API 키 (필수)
    OPENAI_API_KEY=sk-여기에_당신의_OPENAI_키를_붙여넣으세요

    # RDS 데이터베이스 정보 (필수)
    RDS_HOST=여기에_RDS_엔드포인트_주소
    RDS_USER=admin
    RDS_PASSWORD=여기에_DB_비밀번호
    RDS_DB_NAME=demo_db
    ```
3.  `Ctrl+O` -> `Enter` -> `Ctrl+X` 로 저장 및 종료.

---

## 4. 소스 코드 업데이트 (main.py)
기존 `main.py`를 RAG 기능이 포함된 새 코드로 교체합니다.

1.  파일 열기:
    ```bash
    nano main.py
    ```
2.  기존 내용 삭제: `Ctrl+K`를 계속 눌러서 내용을 싹 지웁니다.
3.  **새 코드 붙여넣기**:
    *   (이 가이드와 함께 제공된 `main.py` 파일의 전체 내용을 복사해서 붙여넣으세요.)
    *   *주의: 코드가 길어서 붙여넣는 데 몇 초 걸릴 수 있습니다.*
4.  `Ctrl+O` -> `Enter` -> `Ctrl+X` 로 저장 및 종료.

---

## 5. 서버 실행 및 RAG 테스트
이제 AI 서버를 가동합니다.

1.  **서버 실행**:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```
    *   에러 없이 `Application startup complete.`가 뜨면 성공입니다.

2.  **테스트 (Swagger UI 접속)**:
    *   내 PC 브라우저에서 `http://<EC2-퍼블릭-IP>:8000/docs` 접속.
    *   **AI RAG** 태그가 새로 생긴 것을 볼 수 있습니다.

3.  **[실습 1] 문서 학습시키기 (Upload)**:
    *   `POST /rag/upload` 클릭 -> **Try it out**.
    *   `file`: 가지고 있는 PDF나 DOCX(워드) 파일을 선택합니다. (예: 회사 규정집, 매뉴얼 등)
    *   **Execute** 클릭.
    *   `Code 200`과 함께 `"문서 학습이 완료되었습니다."` 메시지가 뜨면 성공!

4.  **[실습 2] 질문하기 (Ask)**:
    *   `POST /rag/ask` 클릭 -> **Try it out**.
    *   JSON 입력창의 `question` 부분에 업로드한 문서 내용과 관련된 질문을 입력합니다.
        ```json
        {
          "question": "이 문서의 핵심 요약해줘"
        }
        ```
    *   **Execute** 클릭.
    *   잠시 후(AI 생각 시간) `answer`에 답변이 달리는 것을 확인하세요!

---

### [Tip] 문제 해결
*   **`ModuleNotFoundError: No module named 'pysqlite3'` 에러**:
    *   `requirements.txt`에 `pysqlite3-binary`가 있는지 확인하고 다시 `pip install` 하세요.
*   **`OPENAI_API_KEY` 관련 에러**:
    *   `.env` 파일에 키 값이 정확히 들어갔는지 `cat .env` 명령어로 확인하세요. (공백 주의)
*   **답변이 이상하거나 엉뚱해요**:
    *   업로드한 문서 내용에 없는 질문을 하면 AI가 답변을 못하거나 환각(Hallucination) 증세를 보일 수 있습니다. 문서에 있는 내용을 질문해 보세요.
