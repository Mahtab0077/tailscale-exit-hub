#!/usr/bin/env python3
"""ساخت انبوه کاربران Headscale (نسخه Termux/CLI) + خروجی CSV"""
import csv, json, subprocess, sys, os
from datetime import datetime

HS_BIN   = os.path.expanduser("~/go/bin/headscale")
CONFIG   = os.path.expanduser("~/headscale-lab/config.yaml")
SERVER_URL = "https://graduate-targets-rpg-aus.trycloudflare.com"
COUNT      = 100
NAMESPACE  = "user"
DOMAIN     = "hs.local"
KEY_EXPIRY = "90d"
OUTPUT_CSV = os.path.expanduser(f"~/headscale-lab/users_{datetime.now():%Y%m%d_%H%M}.csv")

def hs(*args):
    r = subprocess.run([HS_BIN, "-c", CONFIG, "-o", "json", *args],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("ERROR:", " ".join(args), "->", r.stderr.strip()[:300], file=sys.stderr)
        sys.exit(1)
    return json.loads(r.stdout) if r.stdout.strip() else {}

def user_map():
    data = hs("users", "list")
    if data is None:
        return {}
    users = data if isinstance(data, list) else (data.get("users") or [])
    return {u["name"]: u["id"] for u in users}

def main():
    m = user_map()
    rows = []
    for i in range(1, COUNT + 1):
        name = f"{NAMESPACE}{i:03d}"
        if name not in m:
            hs("users", "create", name)
            m = user_map()
            print(f"+ created {name}")
        uid = m.get(name)
        if uid is None:
            print(f"!! could not resolve id for {name}", file=sys.stderr); sys.exit(1)
        key = hs("preauthkeys", "create", "--user", str(uid),
                 "--expiration", KEY_EXPIRY)
        k = key.get("key") if isinstance(key, dict) else key[0].get("key")
        rows.append({
            "username": name,
            "email": f"{name}@{DOMAIN}",
            "preauth_key": k,
            "expires_in": KEY_EXPIRY,
            "login_server": SERVER_URL,
            "join_command": f"tailscale up --login-server={SERVER_URL} --authkey={k}",
        })
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"DONE {len(rows)} users -> {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
