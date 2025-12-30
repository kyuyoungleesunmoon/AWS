# Docker를 이용한 리눅스(Ubuntu) 설치 및 실행 가이드

Windows 환경에서 Docker를 이용해 리눅스 환경을 구축하는 단계별 방법입니다. 설치 과정에서 발생하는 일반적인 연결 오류 해결 방법이 포함되어 있습니다.

## 1단계: WSL 2 설치 및 설정
Docker Desktop은 WSL 2(Windows Subsystem for Linux 2) 기반에서 가장 잘 작동합니다.

1. **PowerShell 관리자 권한 실행**
2. 아래 명령어 입력:
   ```powershell
   wsl --install
   ```
3. 설치 완료 후 **컴퓨터 재부팅**

## 2단계: Docker Desktop 설치
1. [Docker 공식 홈페이지](https://www.docker.com/products/docker-desktop/)에서 **Download for Windows** 클릭.
2. 설치 파일 실행 및 설치 진행.
   - **"Use WSL 2 instead of Hyper-V"** 옵션 체크 확인.
3. 설치 완료 후 Docker Desktop 서비스 약관 동의.

## 3단계: 실행 및 트러블슈팅 (중요)
설치 직후 바로 터미널 명령어를 사용하면 에러가 발생할 수 있습니다. 먼저 Docker 엔진을 켜야 합니다.

### 🔴 흔히 발생하는 에러
PowerShell에서 `docker info` 실행 시 다음과 같은 에러가 뜬다면:
```text
Server:
failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine; ...
open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

### ✅ 해결 방법
이 에러는 **Docker Desktop 애플리케이션이 실행되지 않아 백그라운드 데몬이 꺼져있을 때** 발생합니다.

1. **Docker Desktop 실행:**
   - Windows 시작 메뉴에서 **"Docker Desktop"**을 찾아 실행합니다.
   - 또는 PowerShell에서 다음 명령어로 실행할 수 있습니다:
     ```powershell
     Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
     ```
2. **대기:** 작업 표시줄 우측 하단(시스템 트레이)의 고래 아이콘이 움직임을 멈추고 안정화될 때까지 잠시 기다립니다.
3. **재확인:** 다시 `docker info`를 입력하여 서버 정보가 정상 출력되는지 확인합니다.

## 4단계: 리눅스(Ubuntu) 컨테이너 실행
Docker가 정상 작동하면 Ubuntu 컨테이너를 실행합니다.

1. **컨테이너 실행 명령어:**
   ```powershell
   docker run -it ubuntu bash
   ```
   - 명령어를 입력하면 자동으로 최신 이미지(`ubuntu:latest`)를 다운로드합니다.
   - 다운로드 후 컨테이너 내부 쉘로 진입합니다.

2. **리눅스 버전 확인:**
   컨테이너 내부 프롬프트(`root@...:/#`)에서 다음 명령을 입력하여 버전을 확인합니다.
   (2025년 기준, Ubuntu 24.04 LTS Noble Numbat 등이 실행됩니다)
   ```bash
   cat /etc/os-release
   ```

3. **종료:**
   `exit`를 입력하여 컨테이너에서 빠져나옵니다.

## 5단계: 리눅스 기초 명령어 실습 (입문편)
Ubuntu 컨테이너 내부에 접속한 상태(`root@...:/#`)에서 다음 명령어들을 차례로 실습해 보세요.

### 1. 디렉토리 이동 및 위치 확인
- `pwd`: 현재 위치한 디렉토리의 경로를 출력합니다.
- `ls`: 현재 디렉토리의 파일과 폴더 목록을 보여줍니다.
- `ls -al`: 숨겨진 파일을 포함하여 상세 정보를 출력합니다.
- `cd /`: 최상위(root) 디렉토리로 이동합니다.
- `cd ~`: 현재 사용자의 홈 디렉토리로 이동합니다.

### 2. 파일 및 디렉토리 관리
- `mkdir my_folder`: 'my_folder'라는 이름의 새 디렉토리를 만듭니다.
- `touch hello.txt`: 내용이 비어있는 'hello.txt' 파일을 생성합니다.
- `echo "Hello Linux" > hello.txt`: 파일에 텍스트를 입력합니다.
- `cat hello.txt`: 파일의 내용을 터미널에 출력합니다.
- `cp hello.txt copy.txt`: 파일을 복사합니다.
- `mv copy.txt my_folder/`: 파일을 폴더 안으로 이동시킵니다.
- `rm hello.txt`: 파일을 삭제합니다.
- `rm -rf my_folder`: 디렉토리와 그 안의 내용을 모두 강제로 삭제합니다.

## 6단계: 리눅스 필수 명령어 마스터하기 (실전편)
2024-2025년 개발자들이 가장 많이 사용하는 필수 명령어들을 실습해봅니다.

### 1. 텍스트 검색 및 필터링 (`grep`, `find`)
원하는 파일이나 내용을 빠르게 찾을 때 사용합니다.
- **준비:** 실습용 파일을 만듭니다.
  ```bash
  echo -e "apple\nbanana\ncherry\ndate" > fruits.txt
  ```
- `grep "ana" fruits.txt`: 'fruits.txt'에서 "ana"가 포함된 줄(banana)을 찾아 출력합니다.
- `find /etc -name "*.conf"`: `/etc` 폴더 안에서 이름이 `.conf`로 끝나는 설정 파일들을 찾습니다. (출력이 많으므로 `Ctrl + C`로 중단 가능)

### 2. 파일 내용 확인 (`head`, `tail`)
파일 전체를 열지 않고 일부분만 확인할 때 유용합니다.
- `head -n 2 fruits.txt`: 파일의 앞 2줄만 출력합니다.
- `tail -n 1 fruits.txt`: 파일의 마지막 1줄만 출력합니다.

### 3. 권한 및 소유권 관리 (`chmod`)
파일의 읽기/쓰기/실행 권한을 변경합니다.
- `ls -l fruits.txt`: 현재 권한을 확인합니다 (예: `-rw-r--r--`).
- `chmod 777 fruits.txt`: 모든 사용자에게 모든 권한(읽기/쓰기/실행)을 부여합니다.
- `ls -l fruits.txt`: 변경된 권한(`-rwxrwxrwx`)을 확인합니다.

### 4. 시스템 모니터링 (`top`, `df`)
서버 상태를 점검할 때 필수적입니다.
- `top`: 실행 중인 프로세스와 CPU/메모리 점유율을 실시간으로 봅니다. (종료는 `q`)
- `df -h`: 디스크 여유 공간을 사람이 읽기 쉬운 단위(GB, MB)로 확인합니다.

### 5. 파일 압축 및 해제 (`tar`)
리눅스에서 가장 많이 쓰이는 압축 명령어입니다.
- `tar -cvf archive.tar fruits.txt`: `fruits.txt` 파일을 `archive.tar`로 묶습니다.
- `rm fruits.txt`: 원본 파일을 삭제합니다.
- `tar -xvf archive.tar`: 압축을 풀어 파일을 복구합니다.

### 6. 패키지 설치 (`apt`)
필요한 프로그램을 설치합니다.
- `apt update`: 설치 가능한 패키지 목록을 최신화합니다.
- `apt install vim curl -y`: 텍스트 에디터 `vim`과 통신 도구 `curl`을 설치합니다.
- `curl https://www.google.com`: 구글 홈페이지의 HTML 코드를 가져와 터미널에 출력해봅니다.

---

💡 **팁:** 명령어를 입력하다가 `Tab` 키를 누르면 파일 이름이나 명령어가 자동 완성됩니다.



## 7단계: 안전하게 종료 및 관리하기

실습을 마친 후 컨테이너를 종료하고, 터미널에서 상태를 확인하는 방법입니다.



### 1. 컨테이너 내부에서 종료 (정상 종료)

- `exit`: 컨테이너 내부 쉘에서 입력하면 작업을 마치고 안전하게 빠져나옵니다. 컨테이너가 중지됩니다.

- `Ctrl + D`: `exit`와 동일한 기능을 하는 단축키입니다.



### 2. 터미널에서 상태 확인 (Windows PowerShell/CMD)

컨테이너 밖(Windows)에서 현재 실행 중인 리눅스 환경을 확인하고 싶을 때 사용합니다.

- `docker ps`: 현재 **실행 중인** 컨테이너 목록과 'CONTAINER ID'를 확인합니다.

- `docker ps -a`: 종료된 컨테이너를 포함하여 **모든** 컨테이너 목록을 확인합니다.



### 3. 터미널에서 강제 종료 및 삭제

컨테이너가 멈췄거나 응답하지 않을 때 사용합니다.

- `docker stop [CONTAINER_ID]`: 실행 중인 컨테이너를 안전하게 중지시킵니다.

- `docker kill [CONTAINER_ID]`: 컨테이너를 즉시 강제 종료합니다.

- `docker rm [CONTAINER_ID]`: 중지된 컨테이너 기록을 완전히 삭제합니다. (이미지가 삭제되는 것은 아닙니다)



### 4. 사용하지 않는 리소스 정리

실습 후 용량을 확보하고 싶을 때 사용합니다.

- `docker system prune`: 중지된 모든 컨테이너, 사용하지 않는 네트워크 및 이미지를 한꺼번에 정리합니다. (주의: 삭제 후에는 복구할 수 없습니다)
