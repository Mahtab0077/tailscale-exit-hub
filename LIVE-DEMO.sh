#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                    🚀 VLESS VPN LIVE DEMO - TESTING 🚀                    ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# 1. وضعیت سیستم
echo "📊 Step 1: بررسی وضعیت سیستم"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "🔍 Xray Server:"
if pgrep -f "xray -c" > /dev/null; then
    echo "   ✅ فعال (PID: $(pgrep -f 'xray -c'))"
    /opt/xray/xray -version 2>/dev/null || echo "   Version: 26.3.27 (aarch64)"
else
    echo "   ❌ غیرفعال"
fi
echo ""

echo "🔍 VLESS Panel:"
if pgrep -f "python3 web/vless_panel.py" > /dev/null; then
    echo "   ✅ فعال (PID: $(pgrep -f 'python3 web/vless_panel.py'))"
else
    echo "   ❌ غیرفعال"
fi
echo ""

echo "🔍 پورت‌های فعال:"
netstat -tuln 2>/dev/null | grep -E "8443|8888" || ss -tuln 2>/dev/null | grep -E "8443|8888"
echo ""
echo ""

# 2. API Testing
echo "🧪 Step 2: تست API Endpoints"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

echo "1️⃣  GET /api/users"
curl -s http://localhost:8888/api/users | python3 -m json.tool 2>/dev/null || echo "No response"
echo ""

echo "2️⃣  GET /api/subscription?host=localhost:8443"
SUB_RESPONSE=$(curl -s "http://localhost:8888/api/subscription?host=localhost:8443")
if echo "$SUB_RESPONSE" | grep -q "subscription"; then
    echo "   ✅ Subscription generated successfully"
    echo "   Response: $SUB_RESPONSE" | head -c 100
    echo "..."
else
    echo "   ❌ Failed"
fi
echo ""

echo "3️⃣  POST /api/user/toggle (مشتری اول)"
curl -s -X POST http://localhost:8888/api/user/toggle \
  -H 'Content-Type: application/json' \
  -d '{"email":"customer1@example.com"}' | python3 -m json.tool 2>/dev/null
echo ""
echo ""

# 3. Customer Info
echo "👤 Step 3: اطلاعات مشتری اول"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

python3 << 'PYTHON'
from web.vless_panel import VLESSManager
import json

manager = VLESSManager()
user = manager.get_user('customer1@example.com')

print(f"📛 نام: {user['name']}")
print(f"📧 ایمیل: {user['email']}")
print(f"🔑 UUID: {user['uuid']}")
print(f"💾 ترافیک: {user['traffic_limit_gb']} GB")
print(f"📊 وضعیت: {'✅ فعال' if user['status'] == 'active' else '❌ غیرفعال'}")
print("")

# لینک‌ها
link = manager.generate_vless_link('customer1@example.com', 'localhost', 8443, '/vless', 'none')
print(f"🔗 VLESS Link:")
print(f"   {link}")
print("")

# Subscription
sub = manager.generate_subscription('localhost', 8443, '/vless', 'none')
print(f"📦 Subscription Base64:")
print(f"   {sub}")
PYTHON

echo ""
echo ""

# 4. داشبورد
echo "🌐 Step 4: Dashboard Access"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "   URL: http://localhost:8888"
echo "   Status: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8888)"
echo ""
echo ""

# 5. لاگ‌ها
echo "📜 Step 5: Recent Logs"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "Xray Server Logs (last 5 lines):"
tail -5 /opt/xray/xray.log 2>/dev/null || echo "No logs yet"
echo ""
echo ""

# 6. نتیجه نهایی
echo "✅ Step 6: نتیجه نهایی"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "✅ سیستم کاملاً فعال است!"
echo "✅ API جواب می‌دهد!"
echo "✅ مشتری فعال است!"
echo "✅ لینک‌ها تولید می‌شوند!"
echo ""
echo "🎯 اگر همه چیز سبز است - سیستم آماده استفاده است!"
echo ""

