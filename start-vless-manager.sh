#!/bin/bash
# VLESS Manager Startup Script

cd "$(dirname "$0")"

PORT=${PORT:-9090}

echo "🚀 Starting VLESS Manager..."
echo "📍 Dashboard: http://localhost:$PORT"
echo ""

# Kill existing process on port
fuser -k $PORT/tcp 2>/dev/null || true
sleep 1

# Start web panel
PORT=$PORT python3 web/vless_panel.py &
PANEL_PID=$!

echo "Panel PID: $PANEL_PID"
echo "Panel running on port $PORT. Press Ctrl+C to stop."
echo ""
echo "📋 Quick Commands:"
echo "  Add user:  curl -X POST http://localhost:$PORT/api/user/add -H 'Content-Type: application/json' -d '{\"name\":\"Test\",\"email\":\"test@test.com\"}'"
echo "  List:      curl http://localhost:$PORT/api/users"
echo "  Generate:  curl 'http://localhost:$PORT/api/subscription?host=your-tunnel.trycloudflare.com'"
echo ""

echo $PANEL_PID > vless-panel.pid

cleanup() {
    echo ""
    echo "🛑 Stopping VLESS Panel..."
    kill $PANEL_PID 2>/dev/null
    rm -f vless-panel.pid
    exit 0
}

trap cleanup INT TERM

wait $PANEL_PID
