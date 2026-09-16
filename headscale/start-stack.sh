#!/bin/sh
# start-stack.sh — راه‌اندازی Headscale + Cloudflare Tunnel (Quick Tunnel)
HS=~/go/bin/headscale
CFG=~/headscale-lab/config.yaml
LOG=~/headscale-lab

pkill -f "headscale serve" 2>/dev/null
pkill -f "cloudflared tunnel" 2>/dev/null
sleep 2

# ۱) بالا آوردن headscale با server_url فعلی
nohup $HS serve -c $CFG >> $LOG/headscale.log 2>&1 &
sleep 4

# ۲) بالا آوردن تونل
nohup cloudflared tunnel --no-autoupdate --protocol http2 --url http://127.0.0.1:8080 > $LOG/cf-tunnel.log 2>&1 &

# ۳) خواندن URL جدید تونل (تا ۶۰ ثانیه)
NEW_URL=""
for i in $(seq 1 30); do
  NEW_URL=$(grep -oE 'https://[a-zA-Z0-9.-]+\.trycloudflare\.com' $LOG/cf-tunnel.log | head -1)
  [ -n "$NEW_URL" ] && break
  sleep 2
done
[ -z "$NEW_URL" ] && { echo "ERROR: tunnel URL not found"; exit 1; }

# ۴) اگر URL عوض شد، کانفیگ را آپدیت و headscale را ری‌استارت کن
CUR=$(grep '^server_url:' $CFG | awk '{print $2}')
if [ "$NEW_URL" != "$CUR" ]; then
  sed -i "s|server_url: .*|server_url: $NEW_URL|" $CFG
  pkill -f "headscale serve"; sleep 2
  nohup $HS serve -c $CFG >> $LOG/headscale.log 2>&1 &
  sleep 4
  # به‌روزرسانی URL در اسکریپت ساخت کاربر (در صورت نیاز در آینده)
  sed -i "s|SERVER_URL = .*|SERVER_URL = \"$NEW_URL\"|" ~/headscale-lab/create_users.py
fi

# ۵) بررسی نهایی
for i in 1 2 3 4 5; do
  R=$(curl -s -m 15 "$NEW_URL/health")
  [ "$R" = '{"status":"pass"}' ] && { echo "STACK OK -> $NEW_URL"; exit 0; }
  sleep 8
done
echo "STACK FAILED — بررسی لاگ‌ها"; exit 1
