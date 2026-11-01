"""
scan — multi-threaded TCP port scanner
"""

from __future__ import annotations

DESCRIPTION = "multi-threaded TCP port scanner"

import argparse
import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

COMMON = {
    21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 53: "dns",
    80: "http", 110: "pop3", 111: "rpc", 135: "msrpc", 139: "netbios",
    143: "imap", 443: "https", 445: "smb", 993: "imaps", 995: "pop3s",
    1433: "mssql", 1521: "oracle", 3306: "mysql", 3389: "rdp",
    5432: "postgres", 5900: "vnc", 6379: "redis", 8080: "http-proxy",
    8443: "https-alt", 27017: "mongodb",
}


def parse_ports(spec: str) -> list[int]:
    ports: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            lo, hi = int(a), int(b)
            if lo > hi:
                lo, hi = hi, lo
            ports.update(range(lo, hi + 1))
        else:
            ports.add(int(part))
    return sorted(p for p in ports if 1 <= p <= 65535)


def probe(host: str, port: int, timeout: float) -> tuple[int, bool]:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        ok = s.connect_ex((host, port)) == 0
        s.close()
        return port, ok
    except Exception:
        return port, False


def run(argv: list[str]) -> None:
    p = argparse.ArgumentParser(prog="offkit scan", description=DESCRIPTION)
    p.add_argument("-t", "--target", required=True)
    p.add_argument("-p", "--ports", default="1-1024", help="e.g. 80,443 or 1-1000")
    p.add_argument("-T", "--threads", type=int, default=100)
    p.add_argument("--timeout", type=float, default=1.0)
    args = p.parse_args(argv)

    target = args.target.strip()
    ports = parse_ports(args.ports)
    if not ports:
        print("[!] no valid ports")
        sys.exit(1)

    print(f"[*] target  {target}")
    print(f"[*] ports   {len(ports)}")
    print(f"[*] threads {args.threads}")
    print(f"[*] started {datetime.now().isoformat()}\n")

    open_ports: list[int] = []
    with ThreadPoolExecutor(max_workers=args.threads) as pool:
        futs = {pool.submit(probe, target, port, args.timeout): port for port in ports}
        for fut in as_completed(futs):
            port, is_open = fut.result()
            if is_open:
                open_ports.append(port)
                svc = COMMON.get(port, "")
                print(f"  [+] {port:5} open  {svc}")

    print(f"\n[*] {len(open_ports)} open / {len(ports)} scanned")
    print(f"[*] finished {datetime.now().isoformat()}")
    if open_ports:
        print(f"[*] open  {', '.join(map(str, sorted(open_ports)))}")
