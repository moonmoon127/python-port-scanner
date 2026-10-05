# Python TCP Port Scanner
명지대학교 해킹동아리 MJSEC 4주차 네트워크 기초 과제로 구현한 파이썬 기반 TCP 포트 스캐너입니다.
## 1. 개요
* 파이썬 표준 라이브러리(`socket`, `concurrent.futures`, `argparse`)만을 활용하여 제작되었습니다.
* TCP 3-Way Handshake 메커니즘을 기반으로 특정 IP 대역의 포트 열림/닫힘 상태를 판별합니다.
## 2. 주요 기능
* **Level 1 (순차 스캐너)**: `socket.connect_ex()`를 이용한 TCP 연결 시도 및 타임아웃(1초) 제어
* **Level 2 (멀티스레딩 & 서비스 추정)**:
  * `ThreadPoolExecutor`를 활용해 1,000개 포트를 0.2초 대에 스캔하는 멀티스레딩 구현
  * `socket.getservbyport()`를 통한 포트별 서비스 이름 매핑 (HTTP, SSH 등)
  * `argparse` 기반의 CLI 실행 옵션 제공 (`--host`, `--ports`, `--threads`)
## 3. 구현 과정 및 실행 결과
* **1단계: 순차 스캐너 완성하기 (scanner.py)**
  * <img width="1006" height="620" alt="스크린샷 2026-10-05 162322" src="https://github.com/user-attachments/assets/8760f6a7-41e3-47cf-8dac-36faef6e1f59" />
  * <img width="216" height="65" alt="스크린샷 2026-10-05 162224" src="https://github.com/user-attachments/assets/9442aede-aeaa-4665-bf35-a36307223200" />

```python
import socket  # 파이썬 표준 네트워크 통신(TCP/IP 소켓) 모듈을 불러옵니다.
import time    # 스캔에 소요된 시간을 측정하기 위한 모듈을 불러옵니다.
def run_level1():
    # 1. 사용자로부터 타깃 IP 또는 도메인 주소를 입력받습니다.
    # strip() 함수를 사용해 입력값 앞뒤의 불필요한 공백을 제거합니다.
    target_host = input("타깃 IP 또는 도메인을 입력하세요 (예: 127.0.0.1): ").strip()
    
    # 사용자가 아무것도 입력하지 않고 엔터를 누르면 기본값으로 로컬호스트(127.0.0.1)를 설정합니다.
    if not target_host:
        target_host = "127.0.0.1"
    # 스캔을 시작할 포트 번호와 끝 포트 번호를 사용자에게 입력받습니다.
    # 입력이 없을 시 각각 기본값인 1과 100을 지정하도록 or 연산자를 활용합니다.
    start_port = int(input("시작 포트 (예: 1): ") or 1)
    end_port = int(input("끝 포트 (예: 100): ") or 100)
    # 스캔 대상 정보 및 포트 범위를 터미널에 안내합니다.
    print(f"\nTarget: {target_host}")
    print(f"Scanning ports {start_port}-{end_port}...\n")
    # 열린 포트의 개수를 세기 위한 카운터 변수를 0으로 초기화합니다.
    open_ports_count = 0
    
    # 전체 스캔 소요 시간을 측정하기 위해 현재 시작 시간을 기록합니다.
    start_time = time.time()
    # 2. 지정된 포트 범위(start_port ~ end_port)를 순차적으로 반복(for문)하며 스캔합니다.
    for port in range(start_port, end_port + 1):
        # socket.socket(): 새로운 소켓 객체를 생성합니다.
        # - socket.AF_INET: IPv4 주소체계를 사용하겠다고 지정합니다.
        # - socket.SOCK_STREAM: TCP(연결 지향형) 프로토콜을 사용하겠다고 지정합니다.
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # sock.settimeout(1.0): 네트워크 응답 대기 시간을 1초로 제한합니다.
        # 타임아웃을 설정하지 않으면 닫힌 포트에 응답을 기다리느라 프로그램이 무한정 대기하게 됩니다.
        sock.settimeout(1.0)
        # sock.connect_ex((host, port)): 지정한 IP와 포트로 TCP 3-Way Handshake 연결을 시도합니다.
        # - connect()와 달리 예외(Exception)를 발생시키지 않으며, 연결 성공 시 0을 반환하고 실패 시 에러 코드(숫자)를 반환합니다.
        result = sock.connect_ex((target_host, port))
        # 반환값이 0이면 해당 포트가 열려(OPEN)있는 상태입니다.
        if result == 0:
            print(f"Port {port}: OPEN")
            open_ports_count += 1
        else:
            # 0이 아니면 포트가 닫혀(CLOSED)있거나 차단된 상태입니다.
            print(f"Port {port}: CLOSED")
        # 사용이 끝난 소켓을 닫아 시스템 자원을 반환합니다.
        sock.close()
    # 전체 스캔이 끝난 후 소요된 시간을 계산합니다 (현재시간 - 시작시간).
    elapsed_time = time.time() - start_time
    
    # 최종 결과(발견된 열린 포트 수 및 총 소요시간)를 출력합니다.
    print(f"\nScan complete. {open_ports_count} open port(s) found. (소요시간: {elapsed_time:.2f}s)")
# 이 파일이 직접 실행될 때만 run_level1() 함수를 호출합니다.
if __name__ == "__main__":
    run_level1()
```
 * **동작 테스트 (nc로 확인하기)**
  * <img width="1282" height="406" alt="스크린샷 2026-10-05 164306" src="https://github.com/user-attachments/assets/885d00ea-3b98-4c3a-9028-ed067e47bc80" />
  * <img width="968" height="598" alt="스크린샷 2026-10-05 164055" src="https://github.com/user-attachments/assets/2dbdb0da-f3af-4416-9b58-6d774dd8028d" />
  * <img width="622" height="492" alt="스크린샷 2026-10-05 164242" src="https://github.com/user-attachments/assets/cede2b98-1e25-4ddb-a838-cc79827c4364" />
* **2단계: 완성 버전 (멀티스레딩 + CLI 인자 + 서비스 추정)**
 * <img width="1015" height="718" alt="스크린샷 2026-10-05 164839" src="https://github.com/user-attachments/assets/315f4ad7-460f-444e-8185-6486d7452824" />
```python
import socket   # TCP/IP 소켓 통신을 위한 표준 라이브러리
import argparse # 커맨드라인(CLI) 인자 처리(--host, --ports 등)를 위한 모듈
import time     # 전체 스캔 소요 시간을 측정하기 위한 모듈
from concurrent.futures import ThreadPoolExecutor # 멀티스레딩 병렬 처리를 위한 라이브러리
# ==============================================================================
# 1. 포트 번호 기반 서비스 이름 추정 함수
# ==============================================================================
def get_service_name(port):
    """
    포트 번호를 전달받아 알려진 TCP 서비스 이름(예: 80 -> http, 22 -> ssh)을 반환합니다.
    """
    try:
        # socket.getservbyport(): 파이썬 표준 시스템 데이터베이스에서 포트별 서비스명을 조회합니다.
        return socket.getservbyport(port, 'tcp')
    except OSError:
        # OS DB에 정의되지 않은 포트이거나 조회 실패 시 'unknown'으로 처리합니다.
        return 'unknown'
# ==============================================================================
# 2. 단일 포트 스캔 함수 (스레드 작업 단위)
# ==============================================================================
def scan_port(host, port):
    """
    특정 IP(host)와 포트(port)에 대해 TCP 3-Way Handshake 연결을 시도하여 상태를 확인합니다.
    """
    # IPv4(AF_INET), TCP(SOCK_STREAM) 방식의 소켓 생성
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1.0)  # 응답 대기 제한시간 1초 설정 (필수)
    
    # connect_ex(): 연결 성공 시 0 반환, 실패 시 에러 번호 반환
    result = sock.connect_ex((host, port))
    sock.close()  # 연결 시도 후 자원 해제를 위해 소켓 닫기
    if result == 0:
        # 포트가 열려있는 경우 서비스 이름을 조회하여 결과 반환
        service = get_service_name(port)
        return port, True, service
    
    # 포트가 닫혀있는 경우
    return port, False, None
# ==============================================================================
# 3. 메인 실행 함수 (CLI 파싱 및 멀티스레딩 스캔 제어)
# ==============================================================================
def main():
    # argparse를 이용한 CLI 명령줄 인자 정의 및 설명 작성
    parser = argparse.ArgumentParser(description="Python TCP Port Scanner")
    parser.add_argument("--host", default="127.0.0.1", help="Target IP or Domain (Default: 127.0.0.1)")
    parser.add_argument("--ports", default="1-1000", help="Port range e.g. 1-1000 (Default: 1-1000)")
    parser.add_argument("--threads", type=int, default=50, help="Number of threads (Default: 50)")
    args = parser.parse_args()
    # --ports "1-1000" 형태의 문자열을 시작 포트(1)와 끝 포트(1000) 숫자로 분리(parsing)
    try:
        start_port, end_port = map(int, args.ports.split("-"))
    except ValueError:
        print("포트 범위 형식이 올바르지 않습니다. 예: --ports 1-1000")
        return
    host = args.host
    thread_count = args.threads
    ports_to_scan = range(start_port, end_port + 1)
    print(f"Scanning {host} (ports {start_port}-{end_port}) with {thread_count} threads...")
    start_time = time.time()  # 스캔 시작 시간 기록
    open_ports = []
    closed_count = 0
    # ThreadPoolExecutor: 지정한 개수(thread_count)만큼의 워커 스레드를 미리 생성하여 병렬 처리
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        # executor.submit(): 각 포트에 대한 scan_port 작업(Task)을 스레드 풀에 등록
        futures = [executor.submit(scan_port, host, port) for port in ports_to_scan]
        # 작업 결과 수집 및 화면 출력
        for future in futures:
            port, is_open, service = future.result()
            if is_open:
                open_ports.append((port, service))
                print(f"Port {port} ({service}): OPEN")
            else:
                closed_count += 1
    # 전체 소요 시간 계산
    elapsed_time = time.time() - start_time
    print(f"\nScan finished in {elapsed_time:.2f}s (open: {len(open_ports)}, closed: {closed_count})")
# 직접 실행 시 main() 함수 호출
if __name__ == "__main__":
    main()
```
 * **동작 테스트 (nc로 확인하기)**
  * <img width="1242" height="378" alt="스크린샷 2026-10-05 165045" src="https://github.com/user-attachments/assets/299e0c45-681e-480a-9611-1628454f1694" />
  * <img width="1130" height="668" alt="스크린샷 2026-10-05 165051" src="https://github.com/user-attachments/assets/4358440b-ee33-4a77-8c50-430ad9d1ed20" />
  * <img width="688" height="87" alt="스크린샷 2026-10-05 165114" src="https://github.com/user-attachments/assets/64247514-78d0-47e4-9c78-c7a9c4c69dd5" />
## 4. 체크포인트 질문 및 답변
 * Q1. 이 스캐너가 포트 하나를 확인할 때, 3-Way Handshake의 어느 단계까지 실제로 일어날까요?
  * 답변: 3단계 (SYN -> SYN-ACK -> ACK) 전체 과정이 모두 일어납니다.
  * socket.connect_ex()는 OS 소켓 레벨에서 Full Connect 방식을 사용합니다.
  * 클라이언트가 SYN 패킷을 전송하고, 서버의 SYN-ACK 응답을 받으면 OS가 자동으로 ACK 패킷을 되돌려보내 연결을 완결지은 후 곧바로 소켓을 닫습니다.
 * Q2. connect_ex와 connect의 차이는 무엇이고 왜 스캐너에는 connect_ex가 더 적합할까요?
  * 답변: connect()는 연결 실패 시 예외(Exception)를 발생시키므로 try-except 예외 처리가 필수적입니다.
  * connect_ex()는 연결 실패 시 에러 예외 대신 C 언어 수준의 에러 번호(숫자)를 직접 반환합니다 (성공 시 0).
  * 수많은 닫힌 포트를 빠르게 순회해야 하는 포트 스캐너 특성상, 예외 처리 오버헤드를 없애고 if result == 0 구조로 깔끔하게 처리할 수 있는 connect_ex가 훨씬 적합합니다.
 * Q3. 스레드를 너무 많이 띄우면 (예: 1000개 동시에) 어떤 문제가 생길 수 있을까요?
  * 답변:
  * 1. 운영체제 시스템 자원 고갈 (File Descriptor Limit): 한 번에 너무 많은 소켓을 생성하면 OS의 프로세스당 열 수 있는 파일/소켓 개수 제한(ulimit)을 초과하여 Too many open files 에러가 발생할 수 있습니다.
  * 2. 대상 서버의 보안 장비에 의한 IP 차단: 단시간 내에 수많은 동시 패킷 요청이 들어오면 서버측 방화벽이나 IDS/IPS에 의해 SYN Flood 공격으로 감지되어 IP가 차단될 수 있습니다.
