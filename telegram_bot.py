#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VLESS VPN Telegram Bot
فیلترشکن IP ثابت - مدیریت خودکار تلگرام
"""

import json
import requests
import uuid
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Configuration
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"  # از @BotFather بگیرید
PANEL_API = "http://localhost:8888"
ADMIN_ID = YOUR_ADMIN_ID  # صاحب ربات

# Pricing
PRICING = {
    "basic": {"price": 2, "traffic": 10, "name": "Basic"},
    "pro": {"price": 5, "traffic": 100, "name": "Pro"},
    "premium": {"price": 10, "traffic": 0, "name": "Premium (Unlimited)"},
}

class VLESSBot:
    def __init__(self):
        self.users = {}
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """شروع ربات"""
        user = update.effective_user
        text = f"""
🌍 خوش‌آمدید به Exit Hub VPN!

سلام {user.first_name} 👋

ما IP ثابت و فیلترشکن سریع ارائه می‌دیم:

✅ IP ثابت رایگان (Cloudflare)
✅ سرعت بالا
✅ پشتیبانی 24/7
✅ بدون محدودیت

برای شروع:
/packages - ببینید بسته‌ها
/buy - خرید کنید
/account - حساب‌تان
/support - پشتیبانی
        """
        await update.message.reply_text(text)
    
    async def packages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش بسته‌های قیمتی"""
        keyboard = []
        for pkg_id, pkg in PRICING.items():
            btn = InlineKeyboardButton(
                f"{pkg['name']} - ${pkg['price']}/month",
                callback_data=f"buy_{pkg_id}"
            )
            keyboard.append([btn])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "📦 بسته‌های ما:\n",
            reply_markup=reply_markup
        )
    
    async def buy_package(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """خریدن بسته"""
        query = update.callback_query
        await query.answer()
        
        package = query.data.split("_")[1]
        pkg = PRICING[package]
        
        text = f"""
📦 بسته: {pkg['name']}
💵 قیمت: ${pkg['price']}/month
📊 ترافیک: {pkg['traffic']} GB {'نامحدود' if pkg['traffic'] == 0 else ''}

✅ برای تأیید پرداخت:
/pay {package}

یا از طریق:
- Stripe: stripe.com/pay
- USDT: wallet address
- Bitcoin: bitcoin address
        """
        await query.edit_message_text(text)
    
    async def pay(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پرداخت و ایجاد حساب"""
        try:
            package = context.args[0] if context.args else "pro"
            user = update.effective_user
            
            # Generate UUID
            user_uuid = str(uuid.uuid4())
            email = f"user_{user.id}@exit-hub.com"
            traffic = PRICING[package]["traffic"]
            
            # Add to panel
            response = requests.post(
                f"{PANEL_API}/api/user/add",
                json={
                    "name": user.first_name,
                    "email": email,
                    "traffic_gb": traffic,
                    "package": package,
                    "price": PRICING[package]["price"],
                    "telegram_id": user.id
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                # Get link
                link_response = requests.get(
                    f"{PANEL_API}/api/user/link",
                    params={"email": email, "host": "exit.yourdomain.com"}
                )
                
                if link_response.status_code == 200:
                    link_data = link_response.json()
                    vless_link = link_data.get("link")
                    
                    text = f"""
✅ حساب شما ایجاد شد!

📦 بسته: {PRICING[package]['name']}
⏱️ مدت: 1 ماه
📊 ترافیک: {traffic} GB {'نامحدود' if traffic == 0 else ''}

🔗 لینک شما:
`{vless_link}`

📱 نرم‌افزار:
Android: v2rayNG
iOS: Shadowrocket
Windows: v2rayN

❓ سوال دارید؟
/support
                    """
                    await update.message.reply_text(text, parse_mode="Markdown")
                    
                    # نوتیفای ادمین
                    admin_msg = f"✅ مشتری جدید!\nنام: {user.first_name}\nبسته: {package}\nقیمت: ${PRICING[package]['price']}"
                    context.bot.send_message(ADMIN_ID, admin_msg)
            else:
                await update.message.reply_text("❌ خطا در ایجاد حساب")
        except Exception as e:
            await update.message.reply_text(f"❌ خطا: {str(e)}")
    
    async def account(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مشاهده حساب"""
        user = update.effective_user
        email = f"user_{user.id}@exit-hub.com"
        
        try:
            response = requests.get(
                f"{PANEL_API}/api/users"
            )
            users = response.json().get("users", [])
            user_info = next((u for u in users if u["email"] == email), None)
            
            if user_info:
                text = f"""
👤 حساب شما:

📧 ایمیل: {user_info['email']}
📊 ترافیک: {user_info['traffic_used_gb']}/{user_info['traffic_limit_gb']} GB
⏱️ وضعیت: {'✅ فعال' if user_info['status'] == 'active' else '❌ غیرفعال'}

/link - دریافت لینک
/renew - تمدید اشتراک
                """
            else:
                text = "❌ حسابی یافت نشد\n/packages برای شروع"
            
            await update.message.reply_text(text)
        except Exception as e:
            await update.message.reply_text(f"❌ خطا: {str(e)}")
    
    async def link(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دریافت لینک"""
        user = update.effective_user
        email = f"user_{user.id}@exit-hub.com"
        
        try:
            response = requests.get(
                f"{PANEL_API}/api/user/link",
                params={"email": email, "host": "exit.yourdomain.com"}
            )
            
            if response.status_code == 200:
                link_data = response.json()
                vless_link = link_data.get("link")
                
                text = f"""
🔗 لینک شما:

`{vless_link}`

📱 برای استفاده:
1. نرم‌افزار نصب کنید
2. (+) کلیک کنید
3. لینک رو paste کنید
4. متصل شوید ✅
                """
                await update.message.reply_text(text, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ خطا: {str(e)}")
    
    async def support(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پشتیبانی"""
        text = """
📞 پشتیبانی:

📧 ایمیل: support@exit-hub.com
💬 تلگرام: @exit_hub_support
⏰ زمان: 24/7

❓ سوالات متداول:
/faq

🆘 مشکل؟
/report
        """
        await update.message.reply_text(text)
    
    async def faq(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """سوالات متداول"""
        text = """
❓ سوالات متداول:

Q: آیا ایمن است؟
A: ✅ بله! از Cloudflare استفاده می‌کنیم

Q: تا چه حد سریع است؟
A: ✅ بسیار سریع! CDN Cloudflare

Q: آیا فیلتر را از بین می‌برد؟
A: ✅ بله! WebSocket + TLS

Q: اگر مشکل داشتم چی؟
A: /support بزنید

Q: چطور تمدید کنم؟
A: /renew بزنید
        """
        await update.message.reply_text(text)

async def main():
    """شروع ربات"""
    bot = VLESSBot()
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Commands
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("packages", bot.packages))
    application.add_handler(CommandHandler("account", bot.account))
    application.add_handler(CommandHandler("link", bot.link))
    application.add_handler(CommandHandler("support", bot.support))
    application.add_handler(CommandHandler("faq", bot.faq))
    application.add_handler(CommandHandler("pay", bot.pay))
    
    # Callbacks
    application.add_handler(CallbackQueryHandler(bot.buy_package, pattern="^buy_"))
    
    print("🤖 ربات شروع شد...")
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

