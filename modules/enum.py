"""
enum — post-compromise command reference
"""

from __future__ import annotations

DESCRIPTION = "post-compromise enumeration command reference"

import argparse

LINUX = [
    ("System", [
        "uname -a",
        "cat /etc/os-release",
        "hostname",
        "uptime",
        "id",
        "whoami",
        "w",
    ]),
    ("Users & Auth", [
        "cat /etc/passwd",
        "cat /etc/group",
        "cat /etc/shadow 2>/dev/null || echo no-shadow",
        "ls -la /home",
        "cat /etc/sudoers 2>/dev/null",
        "sudo -l 2>/dev/null",
    ]),
    ("Network", [
        "ip a || ifconfig",
        "ip r || route -n",
        "ss -tulnp || netstat -tulnp",
        "cat /etc/resolv.conf",
        "cat /etc/hosts",
    ]),
    ("Processes & Services", [
        "ps auxf",
        "systemctl list-units --type=service --state=running 2>/dev/null",
        "ls -la /etc/cron*",
        "crontab -l 2>/dev/null",
    ]),
    ("Interesting", [
        "find / -perm -4000 -type f 2>/dev/null | head -50",
        "find / -name '*.conf' -o -name '*.cfg' 2>/dev/null | head -30",
        "ls -la /var/www 2>/dev/null",
        "env",
        "history | tail -50",
    ]),
]

WINDOWS = [
    ("System", [
        "systeminfo",
        "hostname",
        "whoami /all",
        "echo %USERNAME%",
        "wmic os get caption,version,osarchitecture",
    ]),
    ("Users & Groups", [
        "net user",
        "net localgroup",
        "net localgroup administrators",
        "whoami /groups",
        "query user",
    ]),
    ("Network", [
        "ipconfig /all",
        "route print",
        "netstat -ano",
        "arp -a",
    ]),
    ("Processes & Services", [
        "tasklist /svc",
        "sc query",
        "wmic process list brief",
        "schtasks /query /fo LIST /v",
    ]),
    ("Interesting", [
        "dir C:\\Users",
        "reg query HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run",
        "reg query HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run",
        "type C:\\Windows\\System32\\drivers\\etc\\hosts",
    ]),
]


def section(title: str, cmds: list[str]) -> None:
    print(f"\n## {title}")
    print("-" * 40)
    for c in cmds:
        print(f"  {c}")


def run(argv: list[str]) -> None:
    p = argparse.ArgumentParser(prog="offkit enum", description=DESCRIPTION)
    p.add_argument("--os", choices=["linux", "windows", "all"], default="all")
    p.add_argument("--section", help="filter by section name")
    args = p.parse_args(argv)

    if args.os in ("linux", "all"):
        print("\n" + "=" * 50)
        print("  LINUX")
        print("=" * 50)
        for title, cmds in LINUX:
            if args.section and args.section.lower() not in title.lower():
                continue
            section(title, cmds)

    if args.os in ("windows", "all"):
        print("\n" + "=" * 50)
        print("  WINDOWS")
        print("=" * 50)
        for title, cmds in WINDOWS:
            if args.section and args.section.lower() not in title.lower():
                continue
            section(title, cmds)
