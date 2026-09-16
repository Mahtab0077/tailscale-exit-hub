# VLESS Free VPN - راهنمای شروع سریع

## 🎯 برای ۲۰ کاربر اول (رایگان)

### مرحله ۱: راه‌اندازی پنل مدیریت

```bash
cd /workspace/tailscale-exit-hub
./start-vless-manager.sh
```

**پنل در:** http://localhost:9090

### مرحله ۲: اضافه کردن ۲۰ کاربر

در پنل وب (http://localhost:9090):
1. روی تب "➕ اضافه کردن" کلیک کن
2. نام و ایمیل هر کاربر رو وارد کن
3. سقف ترافیک رو تنظیم کن (پیش‌فرض: ۱۰۰GB)
4. دکمه "✅ اضافه کردن" رو بزن

**یا با curl:**

```bash
for i in {1..20}; do
    curl -X POST http://localhost:9090/api/user/add \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"User$i\",\"email\":\"user$i@example.com\",\"traffic_gb\":100}"
done
```

### مرحله ۳: راه‌اندازی VLESS روی GitHub Actions

**روی GitHub:**

1. برو: https://github.com/Rezzzz77/tailscale-backup/actions
2. Workflow "Tailscale Exit Node" رو انتخاب کن
3. "Run workflow" رو کلیک کن
4. Duration: 350 (حداکثر رایگان)
5. Chain: true
6. "Run workflow" رو کلیک کن

**نکته:** هر run جدید → Cloudflare Tunnel جدید → Link جدید

### مرحله ۴: دریافت Cloudflare Tunnel

بعد از Run شدن workflow:
- در لاگ "Start Cloudflare Tunnel" → آدرس tunnel رو پیدا کن
- شکل: `xxxxx.trycloudflare.com`

### مرحله ۵: ساخت Subscription

**در پنل مدیریت:**
1. تب "🔗 سابسکرایبشن" رو باز کن
2. Cloudflare Host رو وارد کن (مثلا: `entertaining-males-assured-strip.trycloudflare.com`)
3. "🔨 ساخت سابسکرایبشن" رو کلیک کن
4. لینک Base64 رو کپی کن

### مرحله ۶: ارسال برای کاربران

**برای هر کاربر:**

```bash
# لینک VLESS کاربر خاص
./scripts/generate-vless-subscription.sh show user@example.com entertaining-males-assured-strip.trycloudflare.com

# یا لیست همه
./scripts/generate-vless-subscription.sh list
```

**یا از پنل وب:**
- روی "📋 لینک" کنار هر کاربر کلیک کن
- لینک رو کپی کن و برای کاربر بفرست

---

## 📱 راهنمای کلاینت برای کاربران

### Android (V2RayNG):
1. [V2RayNG](https://github.com/2dust/v2rayNG/releases) رو دانلود کن
2. روی + → "Import from Clipboard" کلیک کن (لینک VLESS کپی شده)
3. کانفیگ رو انتخاب کن → Connect

### iPhone (Shadowrocket):
1. [Shadowrocket](https://apps.apple.com/app/shadowrocket/id932747118) (نیاز به پول)
2. یا [V2Box](https://github.com/V2Box-Android/V2Box) (رایگان)
3. Import from clipboard → Connect

### Windows (v2rayN):
1. [v2rayN](https://github.com/2dust/v2rayN/releases) دانلود کن
2. روی آیکون → Import from clipboard
3. کانفیگ رو فعال کن → System proxy → Set system proxy

---

## ⚠️ محدودیت‌های GitHub Actions VLESS

| محدودیت | توضیح |
|----------|-------|
| **مدت زمان هر Run** | حداکثر ۶ ساعت |
| **IP** | با هر run تغییر می‌کنه |
| **Tunnel نیاز به راه‌اندازی مجدد** | بعد از هر run |
| **Rate limit GitHub** | ۱۰۰۰ دقیقه/ماه برای هر workflow |

---

## 🔄 برای تداوم ۲۴/۷ (Auto-chain)

در workflow، `chain=true` بزن تا بعد از پایان، خودش run بعدی رو trigger کنه.

**نکته:** با این کار، IP هر ۶ ساعت عوض میشه → Subscription update میشن → کاربران باید resubscribe کنن

---

## 🚀 برای مقیاس به ۱۰۰ کاربر

**بعد از first 20:**
1. **CloudCone VPS SC2** ($1.65/ماه) → Tailscale Exit Node
2. Dashboard اصلی → مدیریت کاربران + مانیتورینگ
3. برای ۱۰۰ کاربر → ۲-۳ VPS + Load Balancer

---

## 🔧 Commands سریع

```bash
# شروع پنل
./start-vless-manager.sh

# اضافه کردن کاربر
./scripts/generate-vless-subscription.sh add "نام" "email@test.com"

# ساخت subscription
./scripts/generate-vless-subscription.sh build tunnel-host.trycloudflare.com

# نمایش لینک کاربر
./scripts/generate-vless-subscription.sh show user@test.com tunnel-host.trycloudflare.com

# لیست کاربران
./scripts/generate-vless-subscription.sh list
```
