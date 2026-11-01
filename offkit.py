#!/usr/bin/env python3
"""
OffKit — modular offensive toolkit
D3F4UL7T

Lab / authorized testing only.
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

VERSION = "1.0.0"

BANNER = r"""
   ______ _               _   __ ___ __
  / ____/(_)___  _________| | / //_/ /_/ |
 / / __ / / __ \/ ___/ ___/ __ \> / / __/
/ /_/ // / /_/ (__  ) /__/ / / / / / /_
\____//_/\____/____/\___/_/ /_/_/ /\__/
                               /_/
  modular offensive toolkit  |  D3F4UL7T
"""

MODULES = {
    "recon": "modules.recon",
    "scan": "modules.scan",
    "shell": "modules.shell",
    "payload": "modules.payload",
    "persist": "modules.persist",
    "enum": "modules.enum",
    "listener": "modules.listener",
}


def print_banner() -> None:
    print(BANNER)
    print(f"[*] OffKit {VERSION}\n")


def list_modules() -> None:
    print("[*] modules\n")
    for name, path in MODULES.items():
        try:
            mod = __import__(path, fromlist=["DESCRIPTION"])
            desc = getattr(mod, "DESCRIPTION", "")
        except Exception:
            desc = "load failed"
        print(f"  {name:12}  {desc}")
    print()


def run_module(name: str, args: list[str]) -> None:
    if name not in MODULES:
        print(f"[!] unknown module: {name}")
        print(f"[*] available: {', '.join(MODULES)}")
        sys.exit(1)

    try:
        mod = __import__(MODULES[name], fromlist=["run"])
    except ImportError as e:
        print(f"[!] import failed ({name}): {e}")
        sys.exit(1)

    if not hasattr(mod, "run"):
        print(f"[!] module '{name}' has no run()")
        sys.exit(1)

    try:
        mod.run(args)
    except SystemExit:
        raise
    except Exception as e:
        print(f"[!] {name}: {e}")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="offkit",
        description="OffKit — modular offensive toolkit (D3F4UL7T)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  offkit list
  offkit recon -t example.com --headers --ports
  offkit scan  -t 192.168.1.10 -p 1-1000
  offkit shell -t reverse -H 10.10.14.5 -p 4444 --lang bash
  offkit payload --list
  offkit persist --list
  offkit enum --os linux
  offkit listener -p 4444
        """,
    )
    parser.add_argument("module", nargs="?", help="module name or 'list'")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="module arguments")

    ns = parser.parse_args()

    if not ns.module or ns.module in ("-h", "--help"):
        print_banner()
        parser.print_help()
        print()
        list_modules()
        return

    if ns.module == "list":
        print_banner()
        list_modules()
        return

    print_banner()
    run_module(ns.module, ns.args)


if __name__ == "__main__":
    main()
