# 🎉 VLESS VPN System - راهنمای کامل

## ✅ سیستم فعال شد!

### 📊 وضعیت فعلی:
- ✅ **Xray VLESS Server** (پورت 8443)
- ✅ **VLESS Manager Panel** (پورت 8888)
- ✅ **مشتری اول** اضافه شده و فعال

---

## 🚀 شروع سریع

### شروع سیستم:
```bash
cd /workspace/tailscale-exit-hub
./start-complete-system.sh
```

---

## 📋 اطلاعات مشتری اول

| پارامتر | مقدار |
|---------|--------|
| **نام** | مشتری اول |
| **ایمیل** | customer1@example.com |
| **UUID** | 7ee99000-d5f3-4e8c-9eb7-3ca8ba6f77fb |
| **ترافیک** | 100 GB |
| **وضعیت** | فعال ✅ |

---

## 🔗 لینک‌های اتصال

### برای تست لوکال:
```
vless://7ee99000-d5f3-4e8c-9eb7-3ca8ba6f77fb@localhost:8443?type=ws&security=none&path=%2Fvless&sni=localhost#customer1%40example.com
```

### برای Cloudflare Tunnel:
```
vless://7ee99000-d5f3-4e8c-9eb7-3ca8ba6f77fb@your-tunnel.trycloudflare.com:443?type=ws&security=tls&path=%2Fvless&sni=your-tunnel.trycloudflare.com#customer1%40example.com
```

---

## 📦 Subscription Links (Base64)

### لوکال:
```
dmxlc3M6Ly83ZWU5OTAwMC1kNWYzLTRlOGMtOWViNy0zY2E4YmE2Zjc3ZmJAbG9jYWxob3N0Ojg0NDM/dHlwZT13cyZzZWN1cml0eT1ub25lJnBhdGg9JTJGdmxlc3Mmc25pPWxvY2FsaG9zdCNjdXN0b21lcjElNDBleGFtcGxlLmNvbQ==
```

### Cloudflare:
```
dmxlc3M6Ly83ZWU5OTAwMC1kNWYzLTRlOGMtOWViNy0zY2E4YmE2Zjc3ZmJAeW91ci10dW5uZWwudHJ5Y2xvdWRmbGFyZS5jb206NDQzP3R5cGU9d3Mmc2VjdXJpdHk9dGxzJnBhdGg9JTJGdmxlc3Mmc25pPXlvdXItdHVubmVsLnRyeWNsb3VkZmxhcmUuY29tI2N1c3RvbWVyMSU0MGV4YW1wbGUuY29t
```

---

## 🛠️ API Commands

### لیست کاربران:
```bash
curl http://localhost:8888/api/users
```

### اضافه کردن کاربر جدید:
```bash
curl -X POST http://localhost:8888/api/user/add \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "نام کاربر",
    "email": "user@example.com",
    "traffic_gb": 50
  }'
```

### تولید Subscription:
```bash
curl "http://localhost:8888/api/subscription?host=localhost:8443"
```

### حذف کاربر:
```bash
curl -X POST http://localhost:8888/api/user/remove \
  -H 'Content-Type: application/json' \
  -d '{"email": "user@example.com"}'
```

---

## 🌐 اتصال از طریق V2Ray Client

### اپلیکیشن‌های پشتیبان:
- **Android:** v2rayNG, NekoBox, Shadowrocket
- **iOS:** Shadowrocket, Quantumult X
- **Windows/Mac:** v2rayN, ClashX, Clash Verge
- **Linux:** v2rayA

### مراحل:
1. یکی از اپلیکیشن‌های بالا را نصب کنید
2. لینک VLESS را کپی کنید
3. دکمه **+** یا **Import** را بزنید
4. لینک را paste کنید
5. متصل شوید ✅

---

## 📁 ساختار پروژه

```
/workspace/tailscale-exit-hub/
├── web/
│   └── vless_panel.py          # VLESS Manager Panel
├── config.json                 # Xray config
├── subscriptions/
│   └── users.json              # User database
├── start-complete-system.sh    # Startup script
└── VLESS-SYSTEM.md            # This file
```

---

## 🔧 فایل‌های کنفیگ

### Xray Config (`/opt/xray/config.json`):
```json
{
  "inbounds": [{
    "port": 8443,
    "protocol": "vless",
    "settings": {
      "clients": [
        {
          "id": "UUID_HERE",
          "email": "email@example.com"
        }
      ]
    },
    "streamSettings": {
      "network": "ws",
      "wsSettings": {
        "path": "/vless"
      }
    }
  }]
}
```

---

## 📊 نظارت بر سیستم

### بررسی وضعیت:
```bash
ps aux | grep -E "xray|vless_panel"
```

### مشاهده لاگ‌ها:
```bash
# Xray logs
tail -f /opt/xray/xray.log

# Panel logs
tail -f /tmp/vless_panel.log
```

### بررسی پورت‌ها:
```bash
netstat -tuln | grep -E "8443|8888"
```

---

## 🚨 مشکل‌شناسی

### خطا: "Address in use"
```bash
# Kill existing processes
pkill -f xray
pkill -f vless_panel
sleep 2
./start-complete-system.sh
```

### خطا: "Connection refused"
- بررسی کنید سرویس‌ها فعال هستند
- پورت‌ها اشغال نشده‌اند
- Firewall مسدود نمی‌کند

### خطا: "Invalid UUID"
- UUID باید معتبر باشد (v4 format)
- امتحان کنید UUID جدید ایجاد کنید

---

## 🔐 امنیت

### نکات مهم:
- ✅ استفاده از WebSocket برای انتقال
- ✅ پشتیبانی TLS (با Cloudflare Tunnel)
- ✅ کاربران جداگانه با UUID منحصر
- ✅ محدودیت ترافیک برای هر کاربر

---

## 📈 آپگریڈ و توسعه

### اضافه کردن کاربران جدید:
```bash
curl -X POST http://localhost:8888/api/user/add \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "مشتری دوم",
    "email": "customer2@example.com",
    "traffic_gb": 100
  }'
```

### اتصال به Cloudflare Tunnel:
```bash
# در سرور خود
cloudflared tunnel run your-tunnel-name

# سپس استفاده کنید:
curl "http://localhost:8888/api/subscription?host=your-tunnel.trycloudflare.com"
```

---

## 📞 پشتیبانی

اگر مشکلی داشتید:
1. بررسی لاگ‌ها کنید
2. Xray و Panel را دوباره شروع کنید
3. UUID کاربر را تأیید کنید
4. میزبان/پورت درست باشد

---

**✨ سیستم آماده است! مشتری‌های خود را اضافه کنید و از سرویس لذت ببرید.**
