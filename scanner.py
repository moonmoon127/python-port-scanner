import socket
import argparse
import time
from concurrent.futures import ThreadPoolExecutor

# 서비스 이름 매핑 함수
def get_service_name(port):
    try:
        # 파이썬 표준 라이브러리로 포트의 서비스명(http, ssh 등) 추정
        return socket.getservbyport(port, 'tcp')
    except OSError:
        # 알려지지 않은 포트인 경우
        return 'unknown'

# 단일 포트 스캔 함수
def scan_port(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1.0)  # 타임아웃 1초
    result = sock.connect_ex((host, port))
    sock.close()

    if result == 0:
        service = get_service_name(port)
        return port, True, service
    return port, False, None

def main():
    # CLI 인자 처리 (argparse)
    parser = argparse.ArgumentParser(description="Python TCP Port Scanner")
    parser.add_argument("--host", default="127.0.0.1", help="Target IP or Domain (Default: 127.0.0.1)")
    parser.add_argument("--ports", default="1-1000", help="Port range e.g. 1-1000 (Default: 1-1000)")
    parser.add_argument("--threads", type=int, default=50, help="Number of threads (Default: 50)")

    args = parser.parse_args()

    # 포트 범위 파싱 ("1-1000" -> start=1, end=1000)
    try:
        start_port, end_port = map(int, args.ports.split("-"))
    except ValueError:
        print("포트 범위 형식이 올바르지 않습니다. 예: --ports 1-1000")
        return

    host = args.host
    thread_count = args.threads
    ports_to_scan = range(start_port, end_port + 1)

    print(f"Scanning {host} (ports {start_port}-{end_port}) with {thread_count} threads...")

    start_time = time.time()
    open_ports = []
    closed_count = 0

    # ThreadPoolExecutor를 이용한 멀티스레딩 동시 스캔
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = [executor.submit(scan_port, host, port) for port in ports_to_scan]

        for future in futures:
            port, is_open, service = future.result()
            if is_open:
                open_ports.append((port, service))
                print(f"Port {port} ({service}): OPEN")
            else:
                closed_count += 1

    elapsed_time = time.time() - start_time
    print(f"\nScan finished in {elapsed_time:.2f}s (open: {len(open_ports)}, closed: {closed_count})")

if __name__ == "__main__":
    main()