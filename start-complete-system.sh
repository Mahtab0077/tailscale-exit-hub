#!/bin/bash
# Complete VLESS System Startup Script

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
XRAY_DIR="/opt/xray"
PANEL_PORT=${PANEL_PORT:-9090}
XRAY_PORT=${XRAY_PORT:-8443}

echo "🚀 Starting Complete VLESS System..."
echo ""

# Check Xray
if [ ! -f "$XRAY_DIR/xray" ]; then
    echo "❌ Xray not found at $XRAY_DIR/xray"
    echo "📥 Installing Xray..."
    mkdir -p $XRAY_DIR
    cd $XRAY_DIR
    XRAY_URL=$(curl -s https://api.github.com/repos/XTLS/Xray-core/releases/latest | jq -r '.assets[] | select(.name | contains("linux-arm64")) | .browser_download_url' | head -1)
    wget -q "$XRAY_URL" -O xray.zip
    unzip -q xray.zip
    chmod +x xray
fi

# Start Xray
echo "🔌 Starting Xray VLESS Server on port $XRAY_PORT..."
cd $XRAY_DIR
pkill -f "xray -c config.json" || true
sleep 1
./xray -c config.json > $XRAY_DIR/xray.log 2>&1 &
XRAY_PID=$!
sleep 2

if ps -p $XRAY_PID > /dev/null; then
    echo "   ✅ Xray started (PID: $XRAY_PID)"
else
    echo "   ❌ Xray failed to start"
    cat $XRAY_DIR/xray.log
    exit 1
fi

# Start Panel
echo "🌐 Starting VLESS Manager Panel on port $PANEL_PORT..."
cd $PROJECT_DIR
pkill -f "python3 web/vless_panel.py" || true
sleep 1
PORT=$PANEL_PORT python3 web/vless_panel.py > /tmp/vless_panel.log 2>&1 &
PANEL_PID=$!
sleep 2

if ps -p $PANEL_PID > /dev/null; then
    echo "   ✅ Panel started (PID: $PANEL_PID)"
else
    echo "   ❌ Panel failed to start"
    cat /tmp/vless_panel.log
    exit 1
fi

echo ""
echo "=== ✅ سیستم فعال شد ==="
echo ""
echo "📊 Dashboard:"
echo "   🌐 http://localhost:$PANEL_PORT"
echo ""
echo "🔌 Xray Server:"
echo "   📍 Port: $XRAY_PORT"
echo "   🔗 WebSocket Path: /vless"
echo ""
echo "📋 Quick Commands:"
echo "   List users:  curl http://localhost:$PANEL_PORT/api/users"
echo "   Add user:    curl -X POST http://localhost:$PANEL_PORT/api/user/add -H 'Content-Type: application/json' -d '{\"name\":\"User\",\"email\":\"user@example.com\",\"traffic_gb\":50}'"
echo "   Get sub:     curl \"http://localhost:$PANEL_PORT/api/subscription?host=localhost:$XRAY_PORT\""
echo ""
echo "📁 Logs:"
echo "   Xray:  tail -f $XRAY_DIR/xray.log"
echo "   Panel: tail -f /tmp/vless_panel.log"
echo ""
echo "🛑 Stop:"
echo "   kill $XRAY_PID $PANEL_PID"
echo ""
