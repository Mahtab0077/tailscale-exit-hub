#!/bin/bash
# ============================================
# Tailscale Exit Node - داشبورد وضعیت
# ============================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
PID_FILE="$PROJECT_DIR/exit-node.pid"

# نمایش هدر
show_header() {
    clear
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║           Tailscale Exit Node Dashboard                  ║${NC}"
    echo -e "${CYAN}║                  $(date '+%Y-%m-%d %H:%M:%S')                      ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# نمایش وضعیت Tailscale
show_tailscale_status() {
    echo -e "${BLUE}📡 وضعیت Tailscale:${NC}"
    echo -e "${BLUE}─────────────────────────────────────${NC}"
    
    if command -v tailscale &> /dev/null; then
        if tailscale status &> /dev/null; then
            echo -e "${GREEN}✅ وضعیت: متصل${NC}"
            echo -e "${BLUE}📍 IP: $(tailscale ip -4 2>/dev/null || echo 'N/A')${NC}"
            echo -e "${BLUE}🔗 Status: $(tailscale status 2>/dev/null | head -1)${NC}"
        else
            echo -e "${RED}❌ وضعیت: قطع${NC}"
        fi
    else
        echo -e "${RED}❌ Tailscale نصب نیست${NC}"
    fi
    echo ""
}

# نمایش وضعیت Exit Node
show_exit_node_status() {
    echo -e "${BLUE}🚪 وضعیت Exit Node:${NC}"
    echo -e "${BLUE}─────────────────────────────────────${NC}"
    
    if tailscale status &> /dev/null; then
        local exit_status=$(tailscale status --json 2>/dev/null | jq -r '.Self.ExitNodeStatus.BriefExitNode // "none"' 2>/dev/null)
        
        if [ -n "$exit_status" ] && [ "$exit_status" != "none" ]; then
            echo -e "${GREEN}✅ وضعیت: فعال${NC}"
            echo -e "${BLUE}🎯 Exit Node: $exit_status${NC}"
        else
            echo -e "${YELLOW}⚠️ وضعیت: غیرفعال${NC}"
        fi
    else
        echo -e "${RED}❌ Tailscale متصل نیست${NC}"
    fi
    echo ""
}

# نمایش کاربران متصل
show_connected_users() {
    echo -e "${BLUE}👥 کاربران متصل:${NC}"
    echo -e "${BLUE}─────────────────────────────────────${NC}"
    
    if tailscale status &> /dev/null; then
        tailscale status 2>/dev/null | tail -n +2 | head -10 || echo "کاربری متصل نیست"
    else
        echo -e "${RED}❌ Tailscale متصل نیست${NC}"
    fi
    echo ""
}

# نمایش وضعیت مانیتورینگ
show_monitoring_status() {
    echo -e "${BLUE}🔄 وضعیت مانیتورینگ:${NC}"
    echo -e "${BLUE}─────────────────────────────────────${NC}"
    
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${GREEN}✅ مانیتورینگ فعال (PID: $pid)${NC}"
        else
            echo -e "${RED}❌ مانیتورینگ غیرفعال${NC}"
            rm -f "$PID_FILE"
        fi
    else
        echo -e "${RED}❌ مانیتورینگ غیرفعال${NC}"
    fi
    echo ""
}

# نمایش لاگ‌های اخیر
show_recent_logs() {
    echo -e "${BLUE}📋 لاگ‌های اخیر:${NC}"
    echo -e "${BLUE}─────────────────────────────────────${NC}"
    
    if [ -f "$LOG_DIR/auto-restart.log" ]; then
        tail -5 "$LOG_DIR/auto-restart.log" 2>/dev/null || echo "لاگی موجود نیست"
    else
        echo "لاگی موجود نیست"
    fi
    echo ""
}

# نمایش آمار
show_statistics() {
    echo -e "${BLUE}📊 آمار:${NC}"
    echo -e "${BLUE}─────────────────────────────────────${NC}"
    
    echo -e "${BLUE}📁 حجم لاگ‌ها: $(du -sh "$LOG_DIR" 2>/dev/null | cut -f1 || echo 'N/A')${NC}"
    echo -e "${BLUE}⏱️ Uptime: $(uptime -p 2>/dev/null || echo 'N/A')${NC}"
    echo -e "${BLUE}💾 RAM: $(free -h 2>/dev/null | grep Mem | awk '{print $3"/"$2}' || echo 'N/A')${NC}"
    echo ""
}

# نمایش کامل
show_full_dashboard() {
    show_header
    show_tailscale_status
    show_exit_node_status
    show_connected_users
    show_monitoring_status
    show_statistics
    show_recent_logs
}

# نمایش سریع
show_quick_status() {
    echo -e "${CYAN}═══════════════════════════════════════${NC}"
    echo -e "${CYAN}     Tailscale Exit Node - Quick Status${NC}"
    echo -e "${CYAN}═══════════════════════════════════════${NC}"
    echo ""
    
    # وضعیت اتصال
    if tailscale status &> /dev/null; then
        echo -e "${GREEN}✅ Tailscale: متصل${NC}"
    else
        echo -e "${RED}❌ Tailscale: قطع${NC}"
    fi
    
    # وضعیت Exit Node
    local exit_status=$(tailscale status --json 2>/dev/null | jq -r '.Self.ExitNodeStatus.BriefExitNode // "none"' 2>/dev/null)
    if [ -n "$exit_status" ] && [ "$exit_status" != "none" ]; then
        echo -e "${GREEN}✅ Exit Node: فعال${NC}"
    else
        echo -e "${YELLOW}⚠️ Exit Node: غیرفعال${NC}"
    fi
    
    # وضعیت مانیتورینگ
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo -e "${GREEN}✅ مانیتورینگ: فعال${NC}"
    else
        echo -e "${RED}❌ مانیتورینگ: غیرفعال${NC}"
    fi
    
    echo ""
}

# حالت نمایش مداوم
watch_mode() {
    while true; do
        show_full_dashboard
        sleep 5
    done
}

# اجرای اصلی
main() {
    mkdir -p "$LOG_DIR"
    
    case "${1:-}" in
        full)
            show_full_dashboard
            ;;
        quick)
            show_quick_status
            ;;
        watch)
            watch_mode
            ;;
        *)
            echo "استفاده: $0 {full|quick|watch}"
            echo ""
            echo "آپشن‌ها:"
            echo "  full   - نمایش کامل داشبورد"
            echo "  quick  - نمایش سریع وضعیت"
            echo "  watch  - نمایش مداوم (هر ۵ ثانیه)"
            ;;
    esac
}

main "$@"
