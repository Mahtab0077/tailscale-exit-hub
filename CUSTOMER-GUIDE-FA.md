# 🎉 راهنمای اتصال VLESS VPN

## 👋 خوش‌آمدید!

سلام **مشتری اول**،

شما با موفقیت به سیستم VLESS VPN اضافه شده‌اید. این فایل شامل تمام اطلاعاتی است که برای اتصال نیاز دارید.

---

## 📋 اطلاعات حساب شما

| موضوع | جزئیات |
|-------|--------|
| **نام** | مشتری اول |
| **ایمیل** | customer1@example.com |
| **شناسه (UUID)** | `7ee99000-d5f3-4e8c-9eb7-3ca8ba6f77fb` |
| **حجم ترافیک** | 100 GB |
| **وضعیت** | ✅ فعال |
| **تاریخ ایجاد** | 2026-09-17 |

---

## 🔗 لینک‌های اتصال

### ۱️⃣ برای تست (لوکال)
اگر از همان دستگاه سرور استفاده می‌کنید:

```
vless://7ee99000-d5f3-4e8c-9eb7-3ca8ba6f77fb@localhost:8443?type=ws&security=none&path=%2Fvless&sni=localhost#customer1%40example.com
```

### ۲️⃣ برای استفاده واقعی (Cloudflare Tunnel)
برای اتصال از دور:

```
vless://7ee99000-d5f3-4e8c-9eb7-3ca8ba6f77fb@your-tunnel.trycloudflare.com:443?type=ws&security=tls&path=%2Fvless&sni=your-tunnel.trycloudflare.com#customer1%40example.com
```

> **نکته:** `your-tunnel.trycloudflare.com` را با آدرس Cloudflare Tunnel واقعی‌تان جایگزین کنید.

---

## 📦 Subscription Links (Base64)

### لوکال:
```
dmxlc3M6Ly83ZWU5OTAwMC1kNWYzLTRlOGMtOWViNy1zY2E4YmE2Zjc3ZmJAbG9jYWxob3N0Ojg0NDM/dHlwZT13cyZzZWN1cml0eT1ub25lJnBhdGg9JTJGdmxlc3Mmc25pPWxvY2FsaG9zdCNjdXN0b21lcjElNDBleGFtcGxlLmNvbQ==
```

### Cloudflare:
```
dmxlc3M6Ly83ZWU5OTAwMC1kNWYzLTRlOGMtOWViNy1zY2E4YmE2Zjc3ZmJAeW91ci10dW5uZWwudHJ5Y2xvdWRmbGFyZS5jb206NDQzP3R5cGU9d3Mmc2VjdXJpdHk9dGxzJnBhdGg9JTJGdmxlc3Mmc25pPXlvdXItdHVubmVsLnRyeWNsb3VkZmxhcmUuY29tI2N1c3RvbWVyMSU0MGV4YW1wbGUuY29t
```

---

## 📱 مراحل اتصال

### ✅ برای Android (v2rayNG)

1. **نصب اپلیکیشن:**
   - Google Play: `v2rayNG` را جستجو کنید
   - یا APK را دانلود کنید

2. **اضافه کردن کانفیگ:**
   - دکمه `+` را بزنید
   - `Subscribe` را انتخاب کنید
   - Subscription Base64 را paste کنید

3. **متصل شدن:**
   - سرور را انتخاب کنید
   - دکمه `Connect` را بزنید
   - ✅ متصل!

### ✅ برای iOS (Shadowrocket)

1. **نصب اپلیکیشن:**
   - App Store: `Shadowrocket` را جستجو کنید
   - خریداری و نصب کنید

2. **اضافه کردن کانفیگ:**
   - علامت `+` را بزنید
   - `Subscribe URL` را انتخاب کنید
   - Subscription Base64 را paste کنید

3. **متصل شدن:**
   - سرور را انتخاب کنید
   - Toggle را فعال کنید
   - ✅ متصل!

### ✅ برای Windows (v2rayN)

1. **دانلود و نصب:**
   - GitHub: `2dust/v2rayN` را دنبال کنید
   - Releases را دانلود کنید

2. **اضافه کردن کانفیگ:**
   - `Ctrl + P` را فشار دهید
   - Subscription Base64 را paste کنید
   - `OK` را بزنید

3. **متصل شدن:**
   - سرور را انتخاب کنید
   - `Turn On System Proxy` را فعال کنید
   - ✅ متصل!

### ✅ برای Linux (v2rayA)

1. **نصب:**
   ```bash
   sudo apt install v2raya
   sudo systemctl start v2raya
   ```

2. **اضافه کردن کانفیگ:**
   - مرورگر: `http://localhost:2017` باز کنید
   - `Import` را کلیک کنید
   - Subscription Base64 را paste کنید

3. **متصل شدن:**
   - سرور را انتخاب کنید
   - `Connect` را کلیک کنید
   - ✅ متصل!

---

## ⚙️ تنظیمات اتصال

| تنظیم | مقدار |
|-------|-------|
| **Protocol** | VLESS |
| **Server** | localhost یا your-tunnel.cf.com |
| **Port** | 8443 (لوکال) یا 443 (Cloudflare) |
| **UUID** | 7ee99000-d5f3-4e8c-9eb7-3ca8ba6f77fb |
| **Network** | WebSocket (ws) |
| **Security** | none (لوکال) یا tls (Cloudflare) |
| **Path** | /vless |
| **SNI** | localhost یا your-tunnel.cf.com |

---

## ✅ تست اتصال

بعد از اتصال، می‌توانید اتصال را تست کنید:

```bash
# تست سرعت
ping google.com

# تست وب‌سایت
curl https://www.google.com
```

---

## 🆘 خطا‌یابی

### خطای "Connection Refused"
**حل:**
- مطمئن شوید سرور فعال است
- پورت 8443 در firewall باز شده‌است
- لینک درست است

### خطای "Invalid UUID"
**حل:**
- UUID را درست کپی کنید
- فاصله‌های اضافی را بررسی کنید

### اتصال آهسته
**حل:**
- Cloudflare Tunnel را استفاده کنید
- سرور را نزدیک‌تر انتخاب کنید
- ترافیک تنظیم کنید

### اپلیکیشن قطع می‌شود
**حل:**
- لوگ‌ها را بررسی کنید
- سرور را restart کنید
- کانفیگ را دوباره کپی کنید

---

## 📊 مانیتورینگ استفاده

برای بررسی استفاده‌ی ترافیک خود:

```
Dashboard: http://localhost:8888/api/users
```

---

## 🔐 نکات امنیتی

⚠️ **مهم:**
- UUID خود را با کسی شریک نکنید
- لینک را فقط در دستگاه‌های خود استفاده کنید
- اگر UUID افشا شد، آن را تغییر دهید

---

## 📞 پشتیبانی

اگر مشکلی دارید:

1. مستندات را بخوانید
2. لاگ‌ها را بررسی کنید
3. سرور را restart کنید
4. اپلیکیشن را reinstall کنید

---

## 🎁 ویژگی‌های سیستم

✅ **نامحدود:**
- سرعت بالا
- اتصالات پایدار
- WebSocket امن

✅ **کنترل شده:**
- حجم ترافیک: 100 GB
- مانیتورینگ مستمر
- آپدیت خودکار

---

## 📅 معلومات حساب

| موضوع | وضعیت |
|-------|--------|
| **ترافیک کل** | 100 GB |
| **ترافیک مصرف شده** | 0 GB |
| **تاریخ شروع** | 2026-09-17 |
| **تاریخ انقضا** | ----- |
| **وضعیت** | ✅ فعال |

---

## 🎉 شروع کنید!

حالا که همه چیز آماده است:

1. ✅ نرم‌افزار را نصب کنید
2. ✅ لینک را اضافه کنید
3. ✅ متصل شوید
4. ✅ لذت ببرید! 🚀

---

**بسیاری موفق!** 🌍✨

تاریخ ایجاد: 2026-09-17  
وضعیت: فعال ✅
