# 🐧 도커로 정복하는 리눅스(Ubuntu) 명령어 8시간 완성 가이드

이 문서는 Docker 컨테이너(`ubuntu:latest`) 환경에서 리눅스 기초부터 쉘 스크립트 입문까지 8시간 안에 마스터할 수 있도록 구성된 학습 자료입니다.

**학습 전 준비:**
터미널(PowerShell/CMD)을 열고 아래 명령어로 학습용 컨테이너를 실행하세요.
```powershell
# 기존 컨테이너가 있다면 삭제 후 새로 시작 (깨끗한 환경)
docker run -it --name linux-study ubuntu bash
```

---

## 🕒 1교시: 환경 적응 및 탐색 (Navigation)
**목표:** 리눅스 파일 시스템 구조를 이해하고 자유자재로 이동한다.

### 📖 이론
- **Root (/):** 윈도우의 `C:\`와 같은 최상위 경로입니다.
- **Home (~):** 사용자의 개인 공간입니다. Root 사용자는 `/root`, 일반 사용자는 `/home/아이디`입니다.
- **절대 경로 vs 상대 경로:** `/`로 시작하면 절대 경로, 그렇지 않으면 현재 위치 기준입니다.

### ⌨️ 실습
1. **위치 확인:**
   ```bash
   pwd                  # 현재 경로 확인
   ```
2. **이동:**
   ```bash
   cd /etc              # 설정 파일들이 있는 곳으로 이동
   ls                   # 목록 확인
   cd ..                # 상위 폴더로 이동
   cd ~                 # 홈 디렉토리로 복귀
   ```
3. **숨김 파일 보기:**
   ```bash
   ls -a                # .으로 시작하는 숨김 파일까지 모두 보기
   ```

### 🚩 도전 과제
- `/var/log` 디렉토리로 이동하여 어떤 파일들이 있는지 확인하고, 다시 홈 디렉토리로 돌아오세요.

---

## 🕒 2교시: 파일과 디렉토리 조작 (File Operations)
**목표:** 파일과 폴더를 생성, 복사, 이동, 삭제한다.

### 📖 이론
- 리눅스는 확장자(.txt)가 필수는 아니지만, 편의상 사용합니다.
- `rm` 명령어는 휴지통 없이 바로 삭제되므로 주의해야 합니다.

### ⌨️ 실습
1. **생성:**
   ```bash
   mkdir workspace      # 작업 폴더 생성
   cd workspace
   touch file1.txt      # 빈 파일 생성
   touch file2.txt
   ```
2. **복사 및 이동:**
   ```bash
   cp file1.txt file1_backup.txt  # 복사
   mkdir backup
   mv file1_backup.txt backup/    # 이동
   ```
3. **삭제:**
   ```bash
   rm file2.txt                   # 파일 삭제
   cd ..
   rm -rf workspace               # 폴더 강제 삭제 (-r: 재귀, -f: 강제)
   ```

### 🚩 도전 과제
- `study` 폴더를 만들고 그 안에 `notes.txt`를 만드세요. `notes.txt`를 `study/backup/` 폴더로 복사한 뒤 원본은 지우세요.

---

## 🕒 3교시: 내용을 읽고 쓰는 법 (Viewing & Editing)
**목표:** 파일 내용을 확인하고 편집기(Nano)를 설치하여 수정한다.
*도커 이미지는 최소 설치라 편집기가 없습니다. 설치부터 배웁니다.*

### 📖 이론
- **cat:** 짧은 내용을 볼 때.
- **less:** 긴 내용을 끊어서 볼 때 (나갈 땐 `q`).
- **nano:** 초보자용 텍스트 에디터.

### ⌨️ 실습
1. **패키지 목록 업데이트 및 에디터 설치:**
   ```bash
   apt update           # 설치 가능한 프로그램 목록 갱신
   apt install nano -y  # nano 에디터 설치
   ```
2. **파일 작성 (Nano):**
   ```bash
   nano diary.txt
   ```
   - *내용 입력 후:* `Ctrl + O` (저장) -> `Enter` -> `Ctrl + X` (종료)
3. **내용 확인:**
   ```bash
   cat diary.txt
   head -n 2 /etc/passwd  # 시스템 파일의 앞 2줄만 보기
   ```

### 🚩 도전 과제
- `nano`를 이용해 `hello_linux.txt`를 만들고 자기소개를 3줄 작성한 뒤 저장하고 빠져나오세요.

---

## 🕒 4교시: 강력한 찾기 기능 (Grep & Find)
**목표:** 수많은 파일 중에서 원하는 파일이나 텍스트를 찾아낸다.

### 📖 이론
- **Grep:** 파일 *내용* 중에서 특정 단어를 찾습니다.
- **Find:** 파일 *이름*이나 속성으로 파일을 찾습니다.
- **Pipe (|):** 앞 명령어의 결과를 뒤 명령어에게 넘겨줍니다. (매우 중요)

### ⌨️ 실습
1. **준비 (실습용 데이터 생성):**
   ```bash
   echo "Linux is fun" > sample.txt
   echo "Docker is cool" >> sample.txt
   echo "Linux is powerful" >> sample.txt
   ```
2. **Grep 사용:**
   ```bash
   grep "Linux" sample.txt       # 'Linux'가 들어간 줄만 출력
   grep -i "linux" sample.txt    # 대소문자 구분 없이 찾기
   ```
3. **Pipe 활용:**
   ```bash
   cat /etc/passwd | grep root   # 시스템 사용자 중 root 찾기
   ```

### 🚩 도전 과제
- `/etc` 디렉토리 안에서 이름에 `conf`가 들어가는 모든 파일을 찾아보세요. (`find /etc -name "*conf*"`)

---

## 🕒 5교시: 권한과 소유권 (Permissions)
**목표:** `chmod`를 이해하고 파일의 읽기/쓰기/실행 권한을 제어한다.

### 📖 이론
- `r`(읽기:4), `w`(쓰기:2), `x`(실행:1)
- `777`: 누구나 다 할 수 있음 (위험). `755`: 주인만 쓰고 남들은 읽기/실행만.
- 도커 컨테이너는 기본적으로 `root` 계정이라 모든 권한이 있지만, 실제 서버 관리를 위해 꼭 알아야 합니다.

### ⌨️ 실습
1. **권한 확인:**
   ```bash
   ls -l sample.txt     # -rw-r--r-- 같은 형태 확인
   ```
2. **권한 변경:**
   ```bash
   chmod 777 sample.txt # 모든 권한 부여
   ls -l sample.txt     # -rwxrwxrwx 로 변경됨 확인
   chmod 400 sample.txt # 나만 읽을 수 있게 변경
   ```
3. **테스트:**
   ```bash
   echo "Test" >> sample.txt  # 쓰기 권한이 없어서 에러 발생! (Permission denied)
   ```

### 🚩 도전 과제
- `secret.sh` 파일을 만들고, 오직 소유자만 읽고 쓰고 실행할 수 있도록(`700`) 권한을 설정하세요.

---

## 🕒 6교시: 패키지 설치와 시스템 관리 (System)
**목표:** 프로그램을 설치하고(apt) 시스템 상태(top, df)를 점검한다.

### 📖 이론
- **apt (Advanced Package Tool):** 우분투의 앱 스토어 같은 존재입니다.
- **Process:** 실행 중인 프로그램.

### ⌨️ 실습
1. **유용한 도구 설치:**
   ```bash
   apt install htop curl iputils-ping -y
   ```
2. **프로세스 확인:**
   ```bash
   ps aux              # 현재 실행 중인 모든 프로세스 보기
   htop                # (설치했다면) 그래픽하게 프로세스 모니터링 (종료: q)
   ```
3. **디스크 용량 확인:**
   ```bash
   df -h               # 남은 용량 확인
   ```

### 🚩 도전 과제
- `curl` 명령어를 사용하여 구글 홈페이지의 HTML을 가져와 `google.html`로 저장해보세요. (`curl https://www.google.com > google.html`)

---

## 🕒 7교시: 입출력 재지향 (Redirection)
**목표:** 명령어의 결과를 화면이 아닌 파일로 저장하거나, 파일의 내용을 명령어에 넣는다.

### 📖 이론
- `>` : 덮어쓰기 (기존 내용 삭제됨)
- `>>` : 이어쓰기 (기존 내용 뒤에 추가됨)

### ⌨️ 실습
1. **출력 저장:**
   ```bash
   ls -al > filelist.txt        # 파일 목록을 텍스트 파일로 저장
   cat filelist.txt
   ```
2. **이어 쓰기:**
   ```bash
   echo "This is the end" >> filelist.txt
   tail filelist.txt
   ```
3. **에러 처리 (고급):**
   ```bash
   ls 존재하지않는파일 2> error.log  # 에러 메시지만 따로 저장
   cat error.log
   ```

### 🚩 도전 과제
- `history` 명령어를 실행하여 내가 지금까지 입력한 모든 명령어를 `my_history.txt`에 저장하세요.

---

## 🕒 8교시: 쉘 스크립트 맛보기 (Shell Scripting)
**목표:** 여러 명령어를 하나의 파일로 만들어 자동화한다.

### 📖 이론
- `#!/bin/bash`: 이 파일이 bash 스크립트임을 알리는 첫 줄(Shebang).
- 변수, 반복문, 조건문을 사용할 수 있습니다.

### ⌨️ 실습
1. **스크립트 파일 작성:**
   ```bash
   nano backup.sh
   ```
2. **내용 입력:**
   ```bash
   #!/bin/bash
   echo "백업을 시작합니다..."
   mkdir -p ./backup
   cp *.txt ./backup/
   echo "모든 텍스트 파일이 backup 폴더로 복사되었습니다."
   ls ./backup
   ```
3. **실행 권한 부여 및 실행:**
   ```bash
   chmod +x backup.sh
   ./backup.sh
   ```

### 🚩 졸업 과제 (Final Project)
- **"시스템 점검 스크립트 만들기"**
- 파일명: `check_system.sh`
- 기능:
    1. 현재 날짜 출력 (`date`)
    2. 디스크 사용량 출력 (`df -h`)
    3. 현재 경로의 파일 목록 출력 (`ls -l`)
    4. 위 모든 내용을 `system_report.txt` 파일 하나에 저장되도록 만드세요.

---
**축하합니다!** 🎉
이 과정을 모두 마쳤다면 리눅스의 기본기를 탄탄하게 갖추게 되었습니다. 이제 `exit`를 입력해 도커 컨테이너를 종료하세요.

```