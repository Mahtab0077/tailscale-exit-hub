#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                   🌍 Cloudflare Tunnel Setup Script                       ║"
echo "║                   IP ثابت رایگان برای مشتریان                           ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "📥 Installing cloudflared..."
    
    # Download latest version
    if [[ $(uname -m) == "aarch64" ]]; then
        wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -O /usr/local/bin/cloudflared
    else
        wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /usr/local/bin/cloudflared
    fi
    
    chmod +x /usr/local/bin/cloudflared
    echo "✅ cloudflared installed"
fi

echo ""
echo "🔐 Cloudflare Tunnel Configuration"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Create tunnel
TUNNEL_NAME="vless-vpn-exit-hub"
echo "1️⃣ Creating tunnel: $TUNNEL_NAME"
cloudflared tunnel create $TUNNEL_NAME 2>/dev/null || echo "Tunnel already exists"

echo ""
echo "2️⃣ Getting tunnel ID..."
TUNNEL_ID=$(cloudflared tunnel list 2>/dev/null | grep $TUNNEL_NAME | awk '{print $1}')
echo "   Tunnel ID: $TUNNEL_ID"

echo ""
echo "3️⃣ Configuring tunnel..."

# Create config directory
mkdir -p ~/.cloudflared

# Create config file
cat > ~/.cloudflared/config.yml << 'CONFIG'
tunnel: vless-vpn-exit-hub
credentials-file: /root/.cloudflared/TUNNEL_ID.json

ingress:
  - hostname: "*.vless-exit.ir"
    service: http://localhost:8443
  - hostname: "panel.vless-exit.ir"
    service: http://localhost:8888
  - service: http_status:404
CONFIG

echo "✅ Config created"

echo ""
echo "4️⃣ Cloudflare Tunnel Information:"
echo "   Tunnel URL: https://<subdomain>.vless-exit.ir"
echo "   Dashboard: https://panel.vless-exit.ir"
echo "   VLESS Server: https://<customer-id>.vless-exit.ir:8443"

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "✅ Setup complete!"
echo ""
echo "💾 To start tunnel, run:"
echo "   cloudflared tunnel run vless-vpn-exit-hub"
echo ""

