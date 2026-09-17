# 💰 راهنمای فروش بدون هزینه ساخت

**هدف:** فروش IP ثابت به مشتریان با درآمد خالص

---

## 📊 مدل بیزنس

```
هزینه‌ها:
├─ Cloudflare Tunnel: $0 ✅
├─ Panel & System: $0 ✅ (خودتون ساخته)
├─ Server (خودتون): $0 ✅
└─ Total: $0 ✅

درآمد:
├─ Customer 1: $5/month
├─ Customer 2: $5/month
├─ Customer 3: $5/month
└─ Total per month: $15+ 💰

سود: 100% ✅
```

---

## 🎯 بسته‌های فروش (توصیه شده)

```
📦 بسته Basic
├─ قیمت: $2/month یا $20/year
├─ ترافیک: 10 GB/month
├─ IP: ثابت (Cloudflare)
├─ پشتیبانی: Email
└─ Setup: آنی

📦 بسته Pro (محبوب‌ترین)
├─ قیمت: $5/month یا $50/year
├─ ترافیک: 100 GB/month
├─ IP: ثابت + تخصیص
├─ پشتیبانی: 24/7 Telegram
└─ Setup: Priority

📦 بسته Premium
├─ قیمت: $10/month یا $100/year
├─ ترافیک: Unlimited
├─ IP: ثابت + اضافی
├─ پشتیبانی: Premium
└─ Setup: Instant + Assistance

📦 بسته Enterprise
├─ قیمت: Custom
├─ ترافیک: Unlimited
├─ IP: Multiple
├─ پشتیبانی: Dedicated
└─ SLA: 99.9%
```

---

## 🚀 راه‌اندازی

### مرحله 1: تنظیم Cloudflare

```bash
# 1. ورود به Cloudflare
cloudflared tunnel login

# 2. ایجاد tunnel
cloudflared tunnel create exit-hub

# 3. مسیریابی Domain
cloudflared tunnel route dns exit-hub exit.example.com

# 4. شروع tunnel
cloudflared tunnel run exit-hub

# پس‌زمینه
nohup cloudflared tunnel run exit-hub > /var/log/tunnel.log 2>&1 &
```

### مرحله 2: بروزرسانی لینک‌های مشتری

```bash
# Customer 1
curl -X POST http://localhost:8888/api/user/add \
  -H 'Content-Type: application/json' \
  -d '{
    "name":"مشتری اول",
    "email":"customer1@example.com",
    "traffic_gb":100,
    "package":"pro",
    "price":5,
    "host":"exit.example.com"
  }'
```

### مرحله 3: دریافت لینک

```bash
# لینک کامل
curl "http://localhost:8888/api/user/link?email=customer1@example.com&host=exit.example.com"

# نتیجه:
# vless://[UUID]@exit.example.com:443?type=ws&security=tls&path=/vless&sni=exit.example.com#customer1
```

---

## 💳 روش‌های دریافت پول

```
✅ Stripe (بهترین)
   └─ 2.9% + $0.30 per transaction

✅ PayPal
   └─ 2.9% + $0.30 per transaction

✅ Crypto (Tether/Bitcoin)
   └─ 1% + Network fees

✅ Local (Telegram Bot)
   └─ 0% + Manual verification

✅ USDT/USDC
   └─ 1% + Blockchain
```

---

## 📱 Customer Panel (آینده)

```
Feature Checklist:
☐ Dashboard: ترافیک، IP، Status
☐ Change IP: تغییر IP رایگان
☐ Support: Ticket system
☐ Billing: Invoice و History
☐ Download: Config & QR Code
```

---

## 🔄 روند فروش

```
1️⃣ مشتری ثبت‌نام می‌کند
   ↓
2️⃣ بسته را انتخاب می‌کند
   ↓
3️⃣ پول را پرداخت می‌کند (Stripe/Crypto)
   ↓
4️⃣ سیستم خودکار:
   └─ UUID تولید
   └─ لینک VLESS ایجاد
   └─ Email ارسال
   ↓
5️⃣ مشتری متصل می‌شود
   ↓
6️⃣ شما درآمد دریافت می‌کنید! 💰
```

---

## 💻 Automation Scripts

### Script 1: Add Customer & Send Email

```bash
#!/bin/bash
EMAIL=$1
PACKAGE=$2
TRAFFIC=$([ "$PACKAGE" = "pro" ] && echo "100" || echo "10")
PRICE=$([ "$PACKAGE" = "pro" ] && echo "5" || echo "2")

# Add user
RESPONSE=$(curl -s -X POST http://localhost:8888/api/user/add \
  -H 'Content-Type: application/json' \
  -d "{
    \"name\":\"$EMAIL\",
    \"email\":\"$EMAIL\",
    \"traffic_gb\":$TRAFFIC,
    \"package\":\"$PACKAGE\",
    \"price\":$PRICE
  }")

UUID=$(echo $RESPONSE | grep -o '"uuid":"[^"]*"' | cut -d'"' -f4)

# Get link
LINK=$(curl -s "http://localhost:8888/api/user/link?email=$EMAIL&host=exit.example.com" | grep -o '"link":"[^"]*"' | cut -d'"' -f4)

# Send email
echo "Your VLESS Link: $LINK" | mail -s "Welcome to Exit Hub" $EMAIL

echo "✅ Customer added: $EMAIL"
```

### Script 2: Monitor Subscriptions

```bash
#!/bin/bash
# Check expiring subscriptions
curl -s http://localhost:8888/api/users | python3 -c "
import sys, json
data = json.load(sys.stdin)
for user in data['users']:
    print(f\"{user['email']}: {user['traffic_limit_gb']}GB\")
"
```

---

## 📊 Analytics Dashboard

```
Daily Stats:
├─ Active Users: 2
├─ Total Traffic: 200 GB
├─ Revenue Today: $15
├─ Monthly Revenue: $450

Monthly Projection:
├─ Customers: 10-50
├─ Revenue: $50-250/month
├─ Growth: 10-20% per month
```

---

## 🔒 Terms & Conditions (نمونه)

```
توافق‌نامه خدمات:

1. سرویس Exit Hub یک خدمات VPN است
2. مشتری مسئول استفاده قانونی است
3. محدودیت ترافیک روزی 3GB
4. IP شامل تغییر ماهانه
5. هیچ refund بدون دلیل معقول
6. حق ترمینیشن برای خرق شرایط
```

---

## 🎯 Marketing (بدون هزینه)

```
✅ Telegram Channel
   └─ اعلانات رایگان

✅ Twitter/X
   └─ توئیت روزی

✅ Reddit
   └─ Post در r/vpn

✅ Product Hunt
   └─ Launch

✅ Word of Mouth
   └─ Referral Program: 20% commission
```

---

## 💰 درآمد متوقع

### ماه 1:
```
Customers: 5
Price/month: $5 (pro)
Revenue: $25/month
Cost: $0
Profit: $25
```

### ماه 3:
```
Customers: 20
Price/month: $5 (pro)
Revenue: $100/month
Cost: $0
Profit: $100
```

### ماه 6:
```
Customers: 50
Price/month: $5 (pro)
Revenue: $250/month
Cost: $0
Profit: $250
```

### سال 1:
```
Customers: 100+
Revenue: $500+/month
Cost: $0
Profit: $6000+/year
```

---

## ✅ Checklist

- [ ] Cloudflare Tunnel Setup
- [ ] Domain Configuration
- [ ] Panel Customization
- [ ] Payment Gateway Integration
- [ ] Email Automation
- [ ] Telegram Bot Support
- [ ] Terms & Conditions
- [ ] Customer Documentation
- [ ] Support System
- [ ] Analytics Dashboard
- [ ] Marketing Campaign
- [ ] Launch & Promote

---

## 🎉 نتیجه

**شما می‌تونید:**
- ✅ بدون هزینه، IP ثابت فروختن
- ✅ 100% سود خالص
- ✅ ماهانه 250$+ درآمد
- ✅ مشتریان راضی
- ✅ سیستم خودکار

**بدون هیچ تلاش اضافی!** 🚀

