# 🤖 Telegram Bot - راهنمای راه‌اندازی

**وضعیت:** ✅ آماده برای استفاده

---

## 📋 مراحل تنظیم

### مرحله 1: Bot Token دریافت کنید

```
1. تلگرام را باز کنید
2. @BotFather را جستجو کنید
3. /start بزنید
4. /newbot بزنید
5. نام را وارد کنید: Exit Hub VPN
6. Username را وارد کنید: exit_hub_bot (یا متفاوت)
7. Token را کپی کنید
```

### مرحله 2: نصب Dependencies

```bash
pip install python-telegram-bot requests
```

### مرحله 3: تنظیم ربات

ویرایش `telegram_bot.py`:

```python
# خط 18
TELEGRAM_TOKEN = "YOUR_TOKEN_HERE"  # توکن را جایگزین کنید

# خط 19
ADMIN_ID = 123456789  # ID خودتان (https://t.me/userinfobot)
```

### مرحله 4: شروع ربات

```bash
# پیشزمینه
nohup python3 telegram_bot.py > /var/log/bot.log 2>&1 &

# یا مستقیم
python3 telegram_bot.py
```

---

## 🎮 دستورات ربات

| دستور | عملکرد |
|-------|--------|
| `/start` | شروع |
| `/packages` | مشاهده بسته‌ها |
| `/buy [package]` | خرید بسته |
| `/account` | حساب‌تان |
| `/link` | دریافت لینک |
| `/support` | پشتیبانی |
| `/faq` | سوالات متداول |

---

## 💰 جریان خریدارانه

```
مشتری تلگرام:
   ↓
/start بزند
   ↓
/packages را کلیک کند
   ↓
بسته را انتخاب کند
   ↓
/pay [package] را اجرا کند
   ↓
سیستم خودکار:
   ├─ UUID تولید
   ├─ لینک VLESS ایجاد
   ├─ در پنل اضافه کند
   └─ لینک به مشتری ارسال کند
   ↓
مشتری لینک را دریافت می‌کند
   ↓
نرم‌افزار را نصب و متصل می‌کند ✅
```

---

## 🔧 Features

✅ خریدن بسته‌ها  
✅ مشاهده حساب  
✅ دریافت لینک  
✅ پشتیبانی 24/7  
✅ FAQ خودکار  
✅ نوتیفای ادمین  
✅ مدیریت خودکار مشتری  

---

## 📊 Admin Commands (ادمین)

```bash
# لیست مشتریان
curl http://localhost:8888/api/users

# مشتری جدید
curl -X POST http://localhost:8888/api/user/add ...

# حذف مشتری
curl -X POST http://localhost:8888/api/user/remove ...

# فعال/غیرفعال
curl -X POST http://localhost:8888/api/user/toggle ...
```

---

## 📱 نمونه تعاملات

### مشتری جدید:

```
User: /start
Bot: 🌍 خوش‌آمدید به Exit Hub VPN! ...

User: /packages
Bot: 📦 بسته‌های ما:
     [Basic - $2/month]
     [Pro - $5/month] ⭐
     [Premium - $10/month]

User: Pro رو کلیک می‌کند
Bot: 📦 بسته: Pro...
     /pay pro

User: /pay pro
Bot: ✅ حساب شما ایجاد شد!
     🔗 لینک شما: vless://...
     📱 نرم‌افزار: v2rayNG...
```

---

## 🐛 Troubleshooting

| مشکل | حل |
|------|-----|
| Bot نمی‌رود | Token را چک کنید |
| API خطا | Panel را restart کنید |
| Webhook error | Admin ID را چک کنید |
| لینک نیست | Database를 چک کنید |

---

## 🚀 بعدی؟

1. ✅ Bot راه‌اندازی کنید
2. ✅ Payment Gateway اضافه کنید
3. ✅ Admin Dashboard بسازید
4. ✅ Monitoring تنظیم کنید
5. ✅ Launch کنید! 🎉

