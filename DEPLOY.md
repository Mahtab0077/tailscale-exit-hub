# 🚀 راهنمای استقرار Tailscale Exit Node

## چرا Oracle Cloud Free Tier؟

| ویژگی | Oracle Cloud Free Tier |
|--------|------------------------|
| 💰 هزینه | **رایگان همیشگی** ✅ |
| ⏱️ محدودیت زمانی | **ندارد** ✅ |
| 🖥️ سرور | 4 هسته ARM + 24GB RAM |
| 🌐 پهنای باند | 10TB در ماه |
| 🔧 Tailscale | **پشتیبانی کامل** ✅ |

---

## مرحله ۱: ساخت اکانت Oracle Cloud

### ۱.۱. ثبت‌نام
1. برو به [cloud.oracle.com](https://cloud.oracle.com)
2. روی **Sign Up** کلیک کن
3. اطلاعات رو پر کن
4. **کارت اعتباری** وارد کن (فقط برای تأیید، پولی کم نمیشه)

### ۱.۲. فعال‌سازی
1. ایمیل تأیید رو باز کن
2. روی **Activate Your Account** کلیک کن
3. رمز عبور رو تنظیم کن

---

## مرحله ۲: ساخت Instance رایگان

### ۲.۱. ورود به کنسول
1. برو به [cloud.oracle.com/console](https://cloud.oracle.com/console)
2. با اکانتت وارد شو

### ۲.۲. ساخت Instance
1. منوی **amburger** (بالا سمت چپ) رو بزن
2. **Compute** → **Instances** رو انتخاب کن
3. روی **Create Instance** کلیک کن

### ۲.۳. تنظیمات Instance

| فیلد | مقدار |
|------|-------|
| **Name** | `tailscale-exit-node` |
| **Image** | `Ubuntu 22.04` |
| **Shape** | `VM.Standard.A1.Flex` (ARM) |
| **OCPU** | `4` |
| **RAM** | `24 GB` |
| **Boot Volume** | `50 GB` |

### ۲.۴. تنظیمات SSH
1. روی **Add SSH keys** کلیک کن
2. گزینه **Generate a key pair** رو انتخاب کن
3. دکمه **Save Private Key** رو بزن
4. فایل `.key` رو ذخیره کن

### ۲.۵. ساخت Instance
1. روی **Create** کلیک کن
2. ۲-۳ دقیقه صبر کن تا آماده بشه

---

## مرحله ۳: اتصال به سرور

### ۳.۱. IP سرور رو پیدا کن
1. به صفحه **Instances** برگرد
2. روی Instance کلیک کن
3. **Public IP** رو کپی کن

### ۳.۲. اتصال با SSH
```bash
# در Termux
ssh -i /path/to/private.key ubuntu@YOUR_SERVER_IP

# مثال
ssh -i ~/Downloads/key.key ubuntu@129.154.56.78
```

---

## مرحله ۴: نصب Tailscale

### ۴.۱. آپدیت سیستم
```bash
sudo apt update && sudo apt upgrade -y
```

### ۴.۲. نصب Tailscale
```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

### ۴.۳. اتصال به Tailscale
```bash
# از Tailscale admin console auth key بگیر
# https://login.tailscale.com/admin/settings/keys

sudo tailscale up \
    --authkey=YOUR_AUTH_KEY \
    --hostname=exit-node \
    --advertise-exit-node \
    --accept-routes
```

### ۴.۴. تأیید
```bash
tailscale status
tailscale ip -4
```

---

## مرحله ۵: فعال کردن Exit Node

### ۵.۱. از Tailscale Admin Console
1. برو به [login.tailscale.com/admin/machines](https://login.tailscale.com/admin/machines)
2. روی سرور جدید کلیک کن
3. گزینه **Use as exit node** رو فعال کن

### ۵.۲. یا با دستور
```bash
sudo tailscale set --advertise-exit-node
```

---

## مرحله ۶: اتصال دوستان

### ۶.۱. لینک دعوت
1. در Tailscale Admin Console
2. روی **Settings** → **Members** کلیک کن
3. روی **Generate invite link** کلیک کن
4. لینک رو برای دوستات بفرست

### ۶.۲. اتصال دوستان
دوستات باید:
1. اپ **Tailscale** رو نصب کنن (iOS/Android)
2. با لینک دعوت وارد بشن
3. از منوی اپ، **Exit Node** رو انتخاب کنن
4. سرور exit node شما رو انتخاب کنن

---

## مرحله ۷: مدیریت کاربران

### ۷.۱. اضافه کردن کاربر
1. در Tailscale Admin Console
2. روی **Members** کلیک کن
3. روی **Invite** کلیک کن
4. ایمیل کاربر رو وارد کن

### ۷.۲. حذف کاربر
1. در Tailscale Admin Console
2. روی کاربر کلیک کن
3. روی **Remove** کلیک کن

### ۷.۳. قطع کردن کاربر
1. در Tailscale Admin Console
2. روی کاربر کلیک کن
3. روی **Disable** کلیک کن

---

## مرحله ۸: بازسازی خودکار

### ۸.۱. نصب systemd service
```bash
sudo tee /etc/systemd/system/tailscale-exit.service << 'EOF'
[Unit]
Description=Tailscale Exit Node
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/tailscaled
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable tailscale-exit
sudo systemctl start tailscale-exit
```

### ۸.۲. Cron job برای بررسی خودکار
```bash
# هر ۵ دقیقه بررسی کن
*/5 * * * * /usr/bin/tailscale status || /usr/bin/tailscale up --authkey=YOUR_KEY --advertise-exit-node
```

---

## 🎉 تمام شد!

 حالا:
- ✅ Exit Node رایگان داری
- ✅ دوستات می‌تونن وصل بشن
- ✅ می‌تونی کنترلشون کنی
- ✅ خودکار بازسازی میشه

---

## ❓ سوالات متداول

### سوال: آیا پولی کم میشه؟
**جواب:** نه! Oracle Cloud Free Tier همیشه رایگانه.

### سوال: محدودیت پهنای باند چقدره؟
**جواب:** 10 ترابایت در ماه کافیه.

### سوال: اگه سرور قطع بشه چی؟
**جواب:** سیستم خودکار بازسازی میشه.

### سوال: چند نفر می‌تونن وصل بشن؟
**جواب:** تعداد نامحدود (بر اساس پهنای باند).
