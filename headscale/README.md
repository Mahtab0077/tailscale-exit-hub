# Headscale Control Plane (روی گوشی / Termux)

این دایرکتوری نسخهٔ توسعه‌یافته‌شده روی محیط Termux این پروژه است.

## اجزا
- `config.yaml` — کانفیگ Headscale v0.26 (SQLite + ACL file + DERP عمومی)
- `acl.hujson` — سیاست دسترسی: ۱۰۰ کاربر، ایزوله‌سازی کامل، فقط دسترسی به Exit Node
- `create_users.py` — ساخت انبوه ۱۰۰ کاربر + PreAuthKey ۹۰ روزه + خروجی CSV
- `start-stack.sh` — بالا آمدن Headscale + Cloudflare Quick Tunnel (HTTP/2) و همگام‌سازی server_url

## اجرا
```sh
sh ~/headscale-lab/start-stack.sh
```

## اتصال کلاینت
```
tailscale up --login-server=$(grep server_url config.yaml | awk '{print $2}') --authkey=<کلید_از_CSV>
```
در اندروید/iOS: در صفحه ورود اپ Tailscale گزینهٔ «Use custom coordination/alternate server» را انتخاب و URL بالا را وارد کنید؛ سپس کلید auth را وارد کنید یا با `headscale nodes register --user userNNN --key mkey:...` نود را ثبت کنید.

## نکات
- فایل `users_*.csv` شامل کلیدهای یک‌بارمصرف است و هرگز کامیت نمی‌شود (`.gitignore`).
- URL تونل پس از هر ری‌استارت تغییر می‌کند (Quick Tunnel) — برای URL ثابت باید Named Tunnel روی دامنه Cloudflare خودتان بسازید.
- `policy check`/`serve` هنگام استارت سینتکس alias شگفت‌انگیز اجرا می‌شود و تست‌های ACL در `acl.hujson` لود می‌شوند.
