# 🎯 Tailscale Exit Node Hub

مدیریت Exit Node با Tailscale برای گروه‌های دوستانه

## ✅ ویژگی‌ها

| ویژگی | توضیح |
|--------|--------|
| 💰 رایگان | GitHub Codespaces + Tailscale Free |
| 🎛️ کنترل | قطع/وصل کردن کاربران |
| 📱 اپ | استفاده از Tailscale app |
| 🔄 خودکار | بازسازی خودکار Exit Node |
| 👁️ مشاهده | مدیریت از پنل |

## 🚀 شروع سریع

```bash
# ۱. کلون کردن پروژه
git clone https://github.com/YOUR_USERNAME/tailscale-backup.git
cd tailscale-backup

# ۲. نصب Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# ۳. اتصال
tailscale up --authkey=YOUR_AUTH_KEY

# ۴. اجرای Exit Node
./scripts/start-exit-node.sh
```

## 📁 ساختار

```
tailscale-exit-hub/
├── scripts/
│   ├── start-exit-node.sh    # راه‌اندازی Exit Node
│   ├── manage-users.sh       # مدیریت کاربران
│   ├── auto-restart.sh       # بازسازی خودکار
│   └── dashboard.sh          # داشبورد وضعیت
├── web/
│   └── server.py             # پنل مدیریت
├── config/
│   └── settings.conf         # تنظیمات
├── users/
│   └── users.json            # لیست کاربران
└── logs/
```

## 👨‍💻 توسعه‌دهنده

**Abolfazl** - cafeabolfazl@gmail.com
