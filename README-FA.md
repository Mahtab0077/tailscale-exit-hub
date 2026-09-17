# 🎉 سیستم VLESS VPN کامل

## 📊 خلاصه پروژه

سیستم فیلترشکن VLESS کامل با:
- **Xray VLESS Server** - سرور VLESS پرقدرت
- **VLESS Manager Panel** - داشبورد مدیریت کاربران
- **Tailscale Integration** - اتصال امن شبکات
- **Cloudflare Tunnel** - نشانی‌گذاری عمومی

---

## 🚀 شروع سریع

### 1️⃣ شروع سیستم:
```bash
cd /workspace/tailscale-exit-hub
./start-complete-system.sh
```

### 2️⃣ دسترسی به داشبورد:
```
http://localhost:9090
```

### 3️⃣ اضافه کردن کاربر:
```bash
curl -X POST http://localhost:9090/api/user/add \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "کاربر جدید",
    "email": "user@example.com",
    "traffic_gb": 50
  }'
```

---

## 📋 اطلاعات مشتری نمونه

**نام:** مشتری اول  
**ایمیل:** customer1@example.com  
**UUID:** 7ee99000-d5f3-4e8c-9eb7-3ca8ba6f77fb  
**ترافیک:** 100 GB  
**وضعیت:** ✅ فعال

---

## 🔗 لینک اتصال

### برای تست:
```
vless://7ee99000-d5f3-4e8c-9eb7-3ca8ba6f77fb@localhost:8443?type=ws&security=none&path=%2Fvless&sni=localhost#customer1%40example.com
```

### برای استفاده واقعی (Cloudflare):
```
vless://7ee99000-d5f3-4e8c-9eb7-3ca8ba6f77fb@your-tunnel.trycloudflare.com:443?type=ws&security=tls&path=%2Fvless&sni=your-tunnel.trycloudflare.com#customer1%40example.com
```

---

## 🛠️ API Endpoints

| دستور | توضیح |
|-------|--------|
| `GET /api/users` | لیست کاربران |
| `POST /api/user/add` | اضافه کاربر |
| `POST /api/user/remove` | حذف کاربر |
| `GET /api/subscription?host=X` | دریافت subscription |
| `GET /api/user/link?email=X&host=Y` | دریافت لینک VLESS |

---

## 📱 اتصال از موبایل/کامپیوتر

### نرم‌افزار‌های پشتیبان:
- **Android:** v2rayNG, NekoBox
- **iOS:** Shadowrocket, Quantumult X
- **Windows:** v2rayN
- **Linux:** v2rayA

### مراحل:
1. نرم‌افزار را نصب کنید
2. لینک VLESS را کپی کنید
3. در نرم‌افزار وارد کنید
4. متصل شوید ✅

---

## 📁 ساختار فایل‌ها

```
tailscale-exit-hub/
├── web/vless_panel.py          # داشبورد مدیریت
├── config/settings.conf         # تنظیمات
├── subscriptions/users.json     # پایگاه داده کاربران
├── scripts/                     # اسکریپت‌های اضافی
├── start-complete-system.sh    # شروع سیستم
├── start-vless-manager.sh      # شروع پنل
└── VLESS-SYSTEM.md             # راهنمای کامل
```

---

## 🔍 مانیتورینگ

```bash
# وضعیت سرویس‌ها
ps aux | grep -E "xray|vless_panel"

# مشاهده لاگ‌ها
tail -f /opt/xray/xray.log
tail -f /tmp/vless_panel.log

# بررسی پورت‌ها
netstat -tuln | grep -E "8443|9090"
```

---

## ⚙️ تنظیمات پیشرفته

### تغییر پورت:
```bash
PANEL_PORT=9091 XRAY_PORT=8444 ./start-complete-system.sh
```

### اضافه کردن کاربرهای بیشتر:
تمام UUID‌های جدید به‌طور خودکار کار می‌کنند:
```bash
curl -X POST http://localhost:9090/api/user/add \
  -H 'Content-Type: application/json' \
  -d '{"name":"User2","email":"user2@example.com","traffic_gb":100}'
```

---

## 🌐 اتصال به Cloudflare Tunnel

```bash
# در سرور
cloudflared tunnel run your-tunnel-name

# سپس در API استفاده کنید
curl "http://localhost:9090/api/subscription?host=your-tunnel.trycloudflare.com"
```

---

## 🎓 مزایا

✅ **رایگان** - بدون هزینه سرویس  
✅ **سریع** - WebSocket برای بانویت بالا  
✅ **امن** - TLS + UUID احراز‌سازی  
✅ **متعدد** - پشتیبانی از کاربران بی‌شمار  
✅ **کنترل شده** - محدودیت ترافیک برای هر کاربر  

---

## 🚨 خطا‌یابی

| مشکل | حل |
|------|-----|
| Address in use | `pkill xray; pkill python3` |
| Connection refused | بررسی firewall و پورت‌ها |
| Invalid UUID | UUID جدید ایجاد کنید |
| Panel not responding | چک `tail -f /tmp/vless_panel.log` |

---

## 📞 پشتیبانی

برای پشتیبانی کامل، مستندات مفصل را بخوانید:
- `VLESS-SYSTEM.md` - راهنمای کامل
- `DEPLOY.md` - راهنمای نصب
- `VLESS-QUICKSTART.md` - شروع سریع

---

**🎯 سیستم آماده است! امروز شروع کنید!**

Repository: https://github.com/Rezzzz77/tailscale-backup
