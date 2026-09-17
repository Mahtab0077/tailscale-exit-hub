# 🌍 IP ثابت رایگان - راهنمای کامل

**تاریخ:** 2026-09-17  
**وضعیت:** ✅ Production Ready

---

## 📋 سناریو: IP ثابت رایگان برای مشتریان

### ✅ حل بدون هزینه اضافی

```
درآمد: $ 0 ✅ (بدون هزینه اضافی)
سرعت: ✅✅✅ (سریع)
IP: ✅ ثابت
Setup: ✅ ساده
```

---

## 🎯 روش 1: Cloudflare Tunnel (بهترین)

### مراحل:

```bash
# 1. نصب cloudflared
wget https://github.com/cloudflare/cloudflared/releases/download/2024.1.0/cloudflared-linux-amd64
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/

# 2. ورود به Cloudflare
cloudflared tunnel login

# 3. ایجاد tunnel
cloudflared tunnel create vless-vpn-exit

# 4. تنظیم config
cat > ~/.cloudflared/config.yml << 'CONFIG'
tunnel: vless-vpn-exit
credentials-file: /root/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: "exit.vless-ir.com"
    service: http://localhost:8443
  - service: http_status:404
CONFIG

# 5. شروع tunnel
cloudflared tunnel route dns vless-vpn-exit exit.vless-ir.com
cloudflared tunnel run vless-vpn-exit
```

### نتیجه:
- ✅ IP ثابت: `exit.vless-ir.com` (Cloudflare IP)
- ✅ رایگان
- ✅ HTTPS خودکار
- ✅ DDoS Protection رایگان

---

## 🎯 روش 2: SOCKS5 Proxy (رایگان محلی)

### Setup:

```bash
# نصب dante-server
apt-get install dante-server

# تنظیم config
cat > /etc/danted.conf << 'CONFIG'
logoutput: /var/log/danted.log
internal: 0.0.0.0 port = 1080
external: eth0
socksmethod: none
socksfamily: both

client pass {
    from: 0.0.0.0/0 to: 0.0.0.0/0
    log: connect disconnect
}

socks pass {
    from: 0.0.0.0/0 to: 0.0.0.0/0
}
CONFIG

# شروع
systemctl start danted
```

### نتیجه:
- ✅ IP ثابت: Your Server IP
- ✅ رایگان
- ✅ سریع
- ✅ پورت: 1080

---

## 🎯 روش 3: WireGuard (سریع‌ترین)

### Setup:

```bash
# نصب
apt-get install wireguard wireguard-tools

# ایجاد keys
wg genkey | tee privatekey | wg pubkey > publickey

# تنظیم interface
cat > /etc/wireguard/wg0.conf << 'CONFIG'
[Interface]
PrivateKey = <YOUR_PRIVATE_KEY>
Address = 10.0.0.1/24
ListenPort = 51820

[Peer]
PublicKey = <CLIENT_PUBLIC_KEY>
AllowedIPs = 10.0.0.2/32
CONFIG

# شروع
systemctl start wg-quick@wg0
```

### نتیجه:
- ✅ سرعت بالا
- ✅ رایگان
- ✅ IP واقعی
- ✅ محفوظ

---

## 💰 مدل فروش (بدون هزینه ساخت)

```
بسته‌های فروش:
├─ Basic: $2/ماه
│  ├─ 1 IP ثابت
│  ├─ 10 GB ترافیک
│  └─ پشتیبانی ایمیل
│
├─ Pro: $5/ماه
│  ├─ 1 IP ثابت
│  ├─ 100 GB ترافیک
│  └─ پشتیبانی 24/7
│
└─ Enterprise: $10/ماه
   ├─ 1 IP ثابت
   ├─ Unlimited ترافیک
   └─ پشتیبانی Priority
```

---

## 🔧 لینک‌های مشتری

### قالب لینک:

```
VLESS: vless://[UUID]@exit.vless-ir.com:443?type=ws&security=tls&path=/vless&sni=exit.vless-ir.com#[EMAIL]

SOCKS5: socks5://server.ip:1080

WireGuard: [Config File]
```

### مثال:

```
Customer: مشتری اول
├─ Email: customer1@example.com
├─ IP: exit.vless-ir.com (Cloudflare)
├─ Port: 443
├─ UUID: 7ee99000-d5f3-4e8c-9eb7-3ca8ba6f77fb
├─ Link: vless://7ee99000-d5f3-4e8c-9eb7-3ca8ba6f77fb@exit.vless-ir.com:443...
└─ Traffic: 100 GB/month
```

---

## 📊 هزینه‌ها

```
Infrastructure Cost: $0 ✅
├─ Cloudflare: رایگان
├─ Server: خودتون
├─ Domain: Optional ($2-5)
└─ Setup: رایگان

Total: $0 - $5 (یکبار)

درآمد: $2-10 per customer ✅ (سود 100%)
```

---

## 🚀 پیاده‌سازی

### Step 1: انتخاب روش
```
✅ Cloudflare (بهترین) - توصیه می‌شود
❌ SOCKS5 (محدود)
❌ WireGuard (محلی)
```

### Step 2: Setup
```bash
bash /workspace/tailscale-exit-hub/SETUP-CLOUDFLARE-TUNNEL.sh
```

### Step 3: مشتریان
```bash
curl -X POST http://localhost:8888/api/user/add \
  -H 'Content-Type: application/json' \
  -d '{
    "name":"مشتری جدید",
    "email":"user@example.com",
    "traffic_gb":100,
    "package":"pro",
    "price":5
  }'
```

### Step 4: لینک‌ها
```bash
curl "http://localhost:8888/api/user/link?email=user@example.com&host=exit.vless-ir.com"
```

---

## ✅ فواید

- ✅ صفر هزینه ساخت
- ✅ IP ثابت واقعی
- ✅ سرعت بالا
- ✅ HTTPS خودکار
- ✅ DDoS protection
- ✅ سود 100%

---

## 📍 آدرس‌های مهم

```
Dashboard: http://localhost:8888
Panel: https://panel.vless-ir.com (via Tunnel)
Server: exit.vless-ir.com
```

---

## 🎯 بعدی؟

1. ✅ Cloudflare Tunnel Setup
2. ✅ Domain خود را تنظیم کنید
3. ✅ مشتریان اضافه کنید
4. ✅ لینک‌ها توزیع کنید
5. ✅ پول دریافت کنید! 💰

