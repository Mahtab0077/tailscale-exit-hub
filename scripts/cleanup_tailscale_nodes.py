#!/usr/bin/env python3
import os
import sys
import urllib.request
import json
import base64

def get_env_or_prompt(name, prompt_text):
    val = os.environ.get(name)
    if not val:
        val = input(prompt_text).strip()
    return val

def main():
    api_key = os.environ.get("TAILSCALE_API_KEY")
    tailnet = os.environ.get("TAILSCALE_TAILNET", "-")
    
    if not api_key:
        print("🔑 Tailscale API Key (tskey-api-...) not found in environment.")
        print("You can generate one at: https://login.tailscale.com/admin/settings/keys")
        api_key = input("Enter your Tailscale API Key: ").strip()
        
    if not api_key:
        print("❌ API Key is required.")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Tailscale-Node-Cleaner/1.0"
    }

    url = f"https://api.tailscale.com/api/v2/tailnet/{tailnet}/devices"
    
    print(f"🔍 Fetching devices from Tailscale tailnet ({tailnet})...")
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"❌ Failed to fetch devices: {e}")
        sys.exit(1)

    devices = data.get("devices", [])
    print(f"📦 Found {len(devices)} total devices in tailnet.")

    offline_or_gh_nodes = []
    for d in devices:
        name = d.get("hostname", "unknown")
        device_id = d.get("id")
        os_type = d.get("os", "")
        last_seen = d.get("lastSeen", "")
        is_offline = False
        
        # Check if offline or github actions / test node
        # You can customize criteria here (e.g., offline or name matches gh-exit / test)
        if "gh-exit" in name or "test" in name or d.get("clientConnectivity") is None:
            is_offline = True

        print(f" - [{device_id}] {name} (OS: {os_type}, LastSeen: {last_seen}) -> {'🎯 Target for deletion' if is_offline else '🟢 Keep'}")
        if is_offline:
            offline_or_gh_nodes.append((device_id, name))

    if not offline_or_gh_nodes:
        print("✅ No offline or dead test/exit nodes found to delete.")
        return

    print(f"\n⚠️ Found {len(offline_or_gh_nodes)} nodes to remove:")
    for did, name in offline_or_gh_nodes:
        print(f"   - {name} (ID: {did})")

    confirm = os.environ.get("AUTO_CONFIRM", "yes").strip().lower()
    if confirm != 'y' and confirm != 'yes':
        print("❌ Operation cancelled.")
        return

    for did, name in offline_or_gh_nodes:
        del_url = f"https://api.tailscale.com/api/v2/device/{did}"
        del_req = urllib.request.Request(del_url, headers=headers, method="DELETE")
        try:
            with urllib.request.urlopen(del_req) as resp:
                if resp.status in (200, 204):
                    print(f"✅ Successfully deleted node: {name} ({did})")
                else:
                    print(f"⚠️ Failed to delete {name}, status: {resp.status}")
        except Exception as e:
            print(f"❌ Error deleting {name} ({did}): {e}")

    print("🎉 Cleanup completed!")

if __name__ == "__main__":
    main()
