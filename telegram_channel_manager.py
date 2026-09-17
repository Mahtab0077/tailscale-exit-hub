#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram Channel Manager - Exit Hub VPN
کانال تلگرام را مدیریت کنید و پست را خودکار کنید
"""

import json
import requests
from datetime import datetime, timedelta
import schedule
import time

# Configuration
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"  # از @BotFather بگیرید
CHANNEL_ID = "@YOUR_CHANNEL"  # کانال خود
PANEL_API = "http://localhost:8888"

# Marketing content templates
POSTS = {
    "welcome": """
🌍 خوش‌آمدید به Exit Hub VPN!

🚀 ما ارائه می‌دهیم:
✅ IP ثابت واقعی (Cloudflare)
✅ سرعت بالا (CDN)
✅ امنیت تمام (TLS 1.3)
✅ پشتیبانی 24/7
✅ قیمت ارزان: $5/month

🔗 شروع کنید: @exit_hub_bot
/packages

#فیلترشکن #VPN #IP_ثابت
    """,
    
    "features": """
⚡ ویژگی‌های Exit Hub VPN:

🔒 SECURITY:
   • TLS 1.3 encryption
   • WebSocket protocol
   • No logs policy
   • Zero knowledge

🚀 SPEED:
   • Cloudflare CDN
   • Unlimited bandwidth
   • Low latency
   • 99.9% uptime

💰 PRICE:
   • Basic: $2/month (10GB)
   • Pro: $5/month (100GB) ⭐
   • Premium: $10/month (Unlimited)

👤 SUPPORT:
   • 24/7 پشتیبانی
   • سریع پاسخ
   • راهنمای کامل

@exit_hub_bot /packages

#VPN_ایمن #فیلترشکن
    """,
    
    "howto": """
📱 چطور نصب کنم؟

🤖 ANDROID:
1. v2rayNG نصب کنید
2. لینک را paste کنید
3. متصل شوید! ✅

🍎 iOS:
1. Shadowrocket نصب کنید
2. لینک را اضافه کنید
3. متصل شوید! ✅

💻 WINDOWS:
1. v2rayN نصب کنید
2. Configuration paste کنید
3. متصل شوید! ✅

🎥 ویدیو تورتوریال:
[لینک]

@exit_hub_bot /link

#نصب_آسان #راهنما
    """,
    
    "promotion": """
🎉 SPECIAL OFFER!

🎁 اولین ماه: 50% تخفیف!

📦 Pro Plan:
❌ قیمت عادی: $5/month
✅ قیمت اول: $2.50!

🚀 Unlimited bandwidth
✅ 100GB/month
✅ Super fast
✅ پشتیبانی 24/7

⏰ محدود! تا ماه این ماه

@exit_hub_bot /pay pro

#تخفیف #فروش #Exit_Hub
    """,
    
    "testimonial": """
⭐ نظر مشتریان:

"بهترین VPN برای ایران!"
- محمد ✅

"سرعت عالی و ایمن!"
- فاطمه ✅

"پشتیبانی خیلی خوب!"
- علی ✅

"ارزش واقعی برای پول!"
- زهرا ✅

👉 شما بعدی باشید!

@exit_hub_bot /packages

#رضایت_مشتری #Exit_Hub
    """,
    
    "tip": """
💡 نکته امروز:

🌐 VPN چیست؟

VPN = Virtual Private Network

✅ ترافیک شما encrypted است
✅ IP شما پنهان است
✅ مکان شما مخفی است
✅ برای جلوگیری از tracking

📱 بهترین برای:
✅ آزادی اینترنتی
✅ امنیت شخصی
✅ رازداری
✅ دسترسی global

Exit Hub VPN: بهترین انتخاب!

@exit_hub_bot /start

#آموزش #امنیت
    """,
    
    "status": """
📊 وضعیت سیستم:

✅ Servers: ONLINE
✅ Speed: 100% 
✅ Security: ACTIVE
✅ Support: 24/7

🌍 Locations:
├─ Global IP
├─ Super fast
├─ Always stable
└─ 99.9% uptime

🔧 آخرین بروز‌رسانی:
└─ تمام سرورها بهتر شد

@exit_hub_bot /status

#سیستم_فعال
    """
}

class ChannelManager:
    def __init__(self):
        self.token = TELEGRAM_TOKEN
        self.channel = CHANNEL_ID
        self.api_url = f"https://api.telegram.org/bot{self.token}"
    
    def send_message(self, text, parse_mode="HTML"):
        """پیام برای کانال ارسال کنید"""
        try:
            response = requests.post(
                f"{self.api_url}/sendMessage",
                json={
                    "chat_id": self.channel,
                    "text": text,
                    "parse_mode": parse_mode
                }
            )
            if response.status_code == 200:
                print(f"✅ پیام ارسال شد: {text[:50]}...")
                return True
            else:
                print(f"❌ خطا: {response.text}")
                return False
        except Exception as e:
            print(f"❌ خطا در ارسال: {str(e)}")
            return False
    
    def send_photo(self, photo_url, caption):
        """عکس به کانال ارسال کنید"""
        try:
            response = requests.post(
                f"{self.api_url}/sendPhoto",
                json={
                    "chat_id": self.channel,
                    "photo": photo_url,
                    "caption": caption,
                    "parse_mode": "HTML"
                }
            )
            if response.status_code == 200:
                print(f"✅ عکس ارسال شد")
                return True
        except Exception as e:
            print(f"❌ خطا: {str(e)}")
            return False
    
    def send_scheduled_posts(self):
        """پست‌های برنامه‌ریزی شده"""
        current_hour = datetime.now().hour
        
        # صبح: خوشامد
        if current_hour == 8:
            self.send_message(POSTS["welcome"])
        
        # ظهر: ویژگی‌ها
        elif current_hour == 12:
            self.send_message(POSTS["features"])
        
        # بعدازظهر: راهنما
        elif current_hour == 16:
            self.send_message(POSTS["howto"])
        
        # شب: نکته
        elif current_hour == 20:
            self.send_message(POSTS["tip"])
        
        # دوشنبه: نظرات
        if datetime.now().weekday() == 0 and current_hour == 10:
            self.send_message(POSTS["testimonial"])
        
        # جمعه: وضعیت
        if datetime.now().weekday() == 4 and current_hour == 18:
            self.send_message(POSTS["status"])
    
    def get_channel_stats(self):
        """آمار کانال"""
        try:
            response = requests.post(
                f"{self.api_url}/getChat",
                json={"chat_id": self.channel}
            )
            if response.status_code == 200:
                data = response.json()["result"]
                return {
                    "title": data.get("title"),
                    "description": data.get("description"),
                    "members_count": data.get("members_count", 0)
                }
        except Exception as e:
            print(f"❌ خطا: {str(e)}")
        return None
    
    def set_channel_info(self, title, description):
        """تنظیم عنوان و توضیح کانال"""
        try:
            requests.post(
                f"{self.api_url}/setChatTitle",
                json={"chat_id": self.channel, "title": title}
            )
            requests.post(
                f"{self.api_url}/setChatDescription",
                json={"chat_id": self.channel, "description": description}
            )
            print("✅ اطلاعات کانال بروز شد")
            return True
        except Exception as e:
            print(f"❌ خطا: {str(e)}")
            return False
    
    def schedule_daily_posts(self):
        """برنامه‌ریزی پست‌های روزانه"""
        schedule.every().day.at("08:00").do(lambda: self.send_message(POSTS["welcome"]))
        schedule.every().day.at("12:00").do(lambda: self.send_message(POSTS["features"]))
        schedule.every().day.at("16:00").do(lambda: self.send_message(POSTS["howto"]))
        schedule.every().day.at("20:00").do(lambda: self.send_message(POSTS["tip"]))
        
        schedule.every().monday.at("10:00").do(lambda: self.send_message(POSTS["testimonial"]))
        schedule.every().friday.at("18:00").do(lambda: self.send_message(POSTS["status"]))
        
        print("📅 پست‌های روزانه برنامه‌ریزی شدند")
        
        while True:
            schedule.run_pending()
            time.sleep(60)

def main():
    """شروع مدیریت کانال"""
    manager = ChannelManager()
    
    print("🚀 Channel Manager شروع شد...")
    
    # تنظیم اطلاعات کانال
    manager.set_channel_info(
        "Exit Hub VPN 🌍",
        "IP ثابت • سرعت بالا • امنیت تمام\n@exit_hub_bot برای خرید"
    )
    
    # آمار
    stats = manager.get_channel_stats()
    if stats:
        print(f"📊 اطلاعات کانال:")
        print(f"   عنوان: {stats['title']}")
        print(f"   اعضا: {stats['members_count']}")
    
    # پیام اول
    manager.send_message(POSTS["welcome"])
    
    # برنامه‌ریزی
    manager.schedule_daily_posts()

if __name__ == "__main__":
    main()

