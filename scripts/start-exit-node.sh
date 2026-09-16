#!/bin/bash
# ============================================
# Tailscale Exit Node - شروع سریع
# ============================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$PROJECT_DIR/config"
LOG_DIR="$PROJECT_DIR/logs"

# لاگ
log() {
    echo -e "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG_DIR/exit-node.log"
}

# بررسی Tailscale
check_tailscale() {
    if ! command -v tailscale &> /dev/null; then
        log "${RED}❌ Tailscale نصب نیست!${NC}"
        echo -e "${YELLOW}نصب کن: curl -fsSL https://tailscale.com/install.sh | sh${NC}"
        exit 1
    fi
    log "${GREEN}✅ Tailscale نصب است${NC}"
}

# اتصال به Tailscale
connect_tailscale() {
    AUTH_KEY="${1:-}"
    
    if [ -z "$AUTH_KEY" ]; then
        if [ -f "$CONFIG_DIR/auth.key" ]; then
            AUTH_KEY=$(cat "$CONFIG_DIR/auth.key")
        else
            log "${RED}❌ Auth Key وارد نشد!${NC}"
            echo -e "${YELLOW}استفاده: $0 --authkey=tskey-auth-xxxxx${NC}"
            exit 1
        fi
    fi
    
    log "${YELLOW}🔗 در حال اتصال...${NC}"
    
    # ذخیره Auth Key
    echo "$AUTH_KEY" > "$CONFIG_DIR/auth.key"
    
    # اتصال
    tailscale up \
        --authkey="$AUTH_KEY" \
        --hostname="exit-node-$(hostname)" \
        --accept-routes \
        --accept-dns=false 2>&1 | tee -a "$LOG_DIR/exit-node.log"
    
    if tailscale status &> /dev/null; then
        log "${GREEN}✅ اتصال برقرار شد!${NC}"
        tailscale status | tee -a "$LOG_DIR/exit-node.log"
    else
        log "${RED}❌ خطا در اتصال${NC}"
        exit 1
    fi
}

# فعال کردن Exit Node
enable_exit_node() {
    log "${YELLOW}🚪 در حال فعال‌سازی Exit Node...${NC}"
    
    tailscale set --advertise-exit-node 2>&1 | tee -a "$LOG_DIR/exit-node.log"
    
    log "${GREEN}✅ Exit Node فعال شد!${NC}"
    echo ""
    echo -e "${BLUE}📍 IP Tailscale: $(tailscale ip -4)${NC}"
    echo -e "${BLUE}🔗 برای اتصال دوستان:${NC}"
    echo -e "   ${YELLOW}از Tailscale app استفاده کنید و این نود رو به عنوان Exit Node انتخاب کنید${NC}"
}

# نمایش وضعیت
show_status() {
    echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     Tailscale Exit Node Status           ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
    echo ""
    tailscale status 2>/dev/null || echo "Tailscale متصل نیست"
    echo ""
    echo -e "${BLUE}📍 IP: $(tailscale ip -4 2>/dev/null || echo 'N/A')${NC}"
}

# منوی اصلی
show_menu() {
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     Tailscale Exit Node Manager          ║${NC}"
    echo -e "${BLUE}╠══════════════════════════════════════════╣${NC}"
    echo -e "${BLUE}║  1) اتصال و راه‌اندازی                    ║${NC}"
    echo -e "${BLUE}║  2) نمایش وضعیت                          ║${NC}"
    echo -e "${BLUE}║  3) فعال کردن Exit Node                  ║${NC}"
    echo -e "${BLUE}║  4) غیرفعال کردن Exit Node               ║${NC}"
    echo -e "${BLUE}║  5) خروج                                 ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
    echo ""
}

# اجرای اصلی
main() {
    mkdir -p "$LOG_DIR" "$CONFIG_DIR"
    
    check_tailscale
    
    case "${1:-}" in
        --authkey=*)
            AUTH_KEY="${1#--authkey=}"
            connect_tailscale "$AUTH_KEY"
            enable_exit_node
            ;;
        --status)
            show_status
            ;;
        --enable)
            enable_exit_node
            ;;
        --disable)
            tailscale set --exit-node= 2>&1
            log "${GREEN}✅ Exit Node غیرفعال شد${NC}"
            ;;
        *)
            show_menu
            read -p "انتخاب: " choice
            case $choice in
                1)
                    read -p "Auth Key: " auth_key
                    connect_tailscale "$auth_key"
                    enable_exit_node
                    ;;
                2) show_status ;;
                3) enable_exit_node ;;
                4)
                    tailscale set --exit-node= 2>&1
                    log "${GREEN}✅ Exit Node غیرفعال شد${NC}"
                    ;;
                5) exit 0 ;;
                *) echo -e "${RED}انتخاب نامعتبر!${NC}" ;;
            esac
            ;;
    esac
}

main "$@"
