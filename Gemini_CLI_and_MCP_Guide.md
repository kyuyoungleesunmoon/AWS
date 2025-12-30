# Gemini CLI 설치 및 MCP(Model Context Protocol) 활용 가이드 (2025 최신판)

이 문서는 개발자를 위해 Gemini를 커맨드라인에서 사용하는 방법과, 최신 AI 기술 트렌드인 MCP(Model Context Protocol)에 대해 소개합니다.

## 1. Gemini CLI 설치 및 설정
Gemini를 터미널에서 활용하는 가장 표준적인 방법은 Google의 공식 SDK 또는 커뮤니티 CLI 도구를 사용하는 것입니다.

### 방법 A: 공식 Node.js CLI (권장)
Google AI SDK를 기반으로 한 커뮤니티 CLI 도구를 사용하는 것이 가장 간편합니다. Node.js 18 이상이 필요합니다.

1.  **설치:**
    ```bash
    npm install -g @google/gemini-cli
    ```
    * `npm` 명령어가 없다면 [Node.js 공식 홈페이지](https://nodejs.org/)에서 설치하세요.

2.  **실행 및 초기 설정:**
    ```bash
    gemini chat
    ```
    * 처음 실행 시 Google API Key가 필요합니다. [Google AI Studio](https://aistudio.google.com/)에서 키를 발급받아 입력하세요.

### 방법 B: Python SDK 활용 (개발자용)
직접 스크립트를 짜서 제어하고 싶다면 Python SDK가 강력합니다.

1.  **설치:**
    ```bash
    pip install -q -U google-generativeai
    ```
2.  **간단한 사용 예시 (`test_gemini.py`):**
    ```python
    import google.generativeai as genai
    import os

    genai.configure(api_key="YOUR_API_KEY")
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello Gemini!")
    print(response.text)
    ```

---

## 2. MCP (Model Context Protocol) 소개 및 사용법
**MCP**는 2024년 말 Anthropic이 발표한 오픈 표준으로, **AI 모델이 외부 데이터(파일, DB, API 등)와 안전하게 통신하는 방식**을 정의합니다. "AI를 위한 USB 포트"라고 불립니다.

### 왜 MCP인가요?
기존에는 AI에게 내 컴퓨터의 파일을 읽히거나 데이터베이스를 조회하게 하려면 복잡한 코드를 직접 짜야 했습니다. MCP를 사용하면 표준화된 '서버'만 연결하면 됩니다.

### 가장 인기 있는 MCP 서버
1.  **FileSystem MCP:** 내 컴퓨터의 로컬 파일과 폴더를 AI가 직접 읽고 쓸 수 있게 합니다. (코딩 보조에 필수)
2.  **GitHub MCP:** 저장소(Repo) 검색, 이슈 확인, 파일 내용을 AI가 직접 조회합니다.
3.  **Postgres/SQLite MCP:** 데이터베이스에 접속해 AI가 쿼리를 날리고 데이터를 분석합니다.

### MCP 사용법 (예시: FileSystem 연결)
MCP를 사용하려면 **MCP Client**(예: Claude Desktop, Cursor 등 지원되는 에디터)와 **MCP Server** 설정이 필요합니다.

**설정 예시 (`claude_desktop_config.json`):**
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:\\Users\\User\\Project"
      ]
    }
  }
}
```
* 위와 같이 설정하면 AI가 `C:\Users\User\Project` 폴더 내의 파일을 자유롭게 읽고 분석할 수 있게 됩니다.

---

## 3. CLI 터미널 종료 및 재실행 가이드
터미널 작업 중 안전하게 종료하고 다시 시작하는 방법입니다.

### 터미널 종료하기
1.  **명령어 취소/중단:** 실행 중인 작업을 멈추려면 `Ctrl + C`를 누르세요.
2.  **쉘 종료:** 현재 열린 터미널 창이나 세션을 닫으려면:
    ```bash
    exit
    ```
    또는 `Ctrl + D`를 입력합니다.

### 터미널 다시 실행하기 (Windows)
1.  **PowerShell:** `Win + R`을 누르고 `powershell` 입력 후 엔터.
2.  **CMD:** `Win + R`을 누르고 `cmd` 입력 후 엔터.
3.  **VS Code:** `Ctrl + `` (백틱) 키를 눌러 통합 터미널을 다시 엽니다.
4.  **작업 디렉토리 복귀:** 터미널을 다시 열면 보통 홈 폴더에서 시작합니다. 작업하던 폴더로 이동하는 것을 잊지 마세요.
    ```bash
    cd C:\Gemini
    ```