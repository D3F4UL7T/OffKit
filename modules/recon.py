"""
recon — DNS, HTTP headers, common-port banners
"""

from __future__ import annotations

DESCRIPTION = "DNS resolution, reverse lookup, HTTP headers, common-port banners"

import argparse
import socket
import ssl
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime


def resolve_host(target: str) -> list[str]:
    out: list[str] = []
    try:
        for info in socket.getaddrinfo(target, None):
            ip = info[4][0]
            if ip not in out:
                out.append(ip)
    except socket.gaierror as e:
        out.append(f"error: {e}")
    return out


def reverse_dns(ip: str) -> str:
    try:
        host, _, _ = socket.gethostbyaddr(ip)
        return host
    except Exception:
        return "-"


def http_headers(url: str, timeout: float = 5.0) -> dict:
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={"User-Agent": "OffKit/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return {
                "status": resp.status,
                "headers": dict(resp.headers),
                "url": resp.geturl(),
            }
    except Exception as e:
        return {"error": str(e)}


def banner_probe(host: str, ports: list[int], timeout: float = 1.5) -> dict[int, str]:
    found: dict[int, str] = {}

    def probe(port: int) -> None:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            if s.connect_ex((host, port)) == 0:
                try:
                    s.send(b"\r\n")
                    data = s.recv(256).decode("utf-8", errors="ignore").strip()
                except Exception:
                    data = ""
                found[port] = data or "open"
            s.close()
        except Exception:
            pass

    with ThreadPoolExecutor(max_workers=min(50, len(ports))) as pool:
        list(pool.map(probe, ports))
    return found


def run(argv: list[str]) -> None:
    p = argparse.ArgumentParser(prog="offkit recon", description=DESCRIPTION)
    p.add_argument("-t", "--target", required=True, help="hostname or IP")
    p.add_argument("--headers", action="store_true", help="fetch HTTP headers")
    p.add_argument("--ports", action="store_true", help="probe common ports + banners")
    p.add_argument("--timeout", type=float, default=2.0)
    args = p.parse_args(argv)

    target = args.target.strip()
    print(f"[*] target  {target}")
    print(f"[*] started {datetime.now().isoformat()}\n")

    print("[+] dns")
    ips = resolve_host(target)
    for ip in ips:
        ptr = reverse_dns(ip) if not str(ip).startswith("error") else "-"
        print(f"    {ip:40}  ptr {ptr}")

    if args.headers:
        print("\n[+] http headers")
        data = http_headers(target, timeout=args.timeout)
        if "error" in data:
            print(f"    {data['error']}")
        else:
            print(f"    status {data.get('status')}  url {data.get('url')}")
            for k, v in data.get("headers", {}).items():
                print(f"    {k}: {v}")

    if args.ports:
        common = [
            21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445,
            993, 995, 1433, 3306, 3389, 5432, 5900, 8080,
        ]
        print("\n[+] common ports")
        host = ips[0] if ips and not str(ips[0]).startswith("error") else target
        results = banner_probe(host, common, timeout=args.timeout)
        if not results:
            print("    none open / filtered")
        else:
            for port in sorted(results):
                print(f"    {port:5}  {results[port][:80]}")

    print(f"\n[*] done {datetime.now().isoformat()}")
