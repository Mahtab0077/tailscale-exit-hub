#!/bin/bash
# ============================================
# Tailscale Exit Node - بازسازی خودکار
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
PID_FILE="$PROJECT_DIR/exit-node.pid"

# تنظیمات
CHECK_INTERVAL=${CHECK_INTERVAL:-60}
MAX_RETRIES=${MAX_RETRIES:-3}

# لاگ
log() {
    local level=$1
    local message=$2
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" | tee -a "$LOG_DIR/auto-restart.log"
}

# بررسی Tailscale
check_tailscale() {
    if ! command -v tailscale &> /dev/null; then
        log "ERROR" "Tailscale نصب نیست"
        return 1
    fi
    
    if tailscale status &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# بررسی Exit Node
check_exit_node() {
    local status=$(tailscale status --json 2>/dev/null | jq -r '.Self.ExitNodeStatus.BriefExitNode // ""' 2>/dev/null)
    
    if [ -n "$status" ] && [ "$status" != "" ]; then
        return 0
    else
        return 1
    fi
}

# ریست Tailscale
restart_tailscale() {
    log "INFO" "در حال ریست Tailscale..."
    
    tailscale down 2>/dev/null || true
    sleep 2
    
    if [ -f "$CONFIG_DIR/auth.key" ]; then
        local auth_key=$(cat "$CONFIG_DIR/auth.key")
        tailscale up --authkey="$auth_key" --accept-routes --accept-dns=false 2>&1 | tee -a "$LOG_DIR/auto-restart.log"
    fi
    
    sleep 3
    
    if check_tailscale; then
        log "INFO" "Tailscale با موفقیت ریست شد"
        return 0
    else
        log "ERROR" "خطا در ریست Tailscale"
        return 1
    fi
}

# فعال کردن Exit Node
enable_exit_node() {
    log "INFO" "فعال‌سازی Exit Node..."
    
    tailscale set --advertise-exit-node 2>&1 | tee -a "$LOG_DIR/auto-restart.log"
    
    sleep 2
    
    if check_exit_node; then
        log "INFO" "Exit Node فعال شد"
        return 0
    else
        log "ERROR" "خطا در فعال‌سازی Exit Node"
        return 1
    fi
}

# حلقه مانیتورینگ
monitor_loop() {
    log "INFO" "شروع مانیتورینگ..."
    
    local consecutive_failures=0
    
    while true; do
        # بررسی Tailscale
        if ! check_tailscale; then
            consecutive_failures=$((consecutive_failures + 1))
            log "WARN" "Tailscale قطع شده ($consecutive_failures/$MAX_RETRIES)"
            
            if [ $consecutive_failures -ge $MAX_RETRIES ]; then
                log "INFO" "تلاش برای بازسازی..."
                restart_tailscale
                enable_exit_node
                consecutive_failures=0
            fi
        else
            # بررسی Exit Node
            if ! check_exit_node; then
                log "WARN" "Exit Node غیرفعال شده"
                enable_exit_node
            fi
            consecutive_failures=0
        fi
        
        sleep $CHECK_INTERVAL
    done
}

# شروع در پس‌زمینه
start_daemon() {
    if [ -f "$PID_FILE" ]; then
        local old_pid=$(cat "$PID_FILE")
        if kill -0 "$old_pid" 2>/dev/null; then
            log "WARN" "데몬 از قبل در حال اجراست (PID: $old_pid)"
            return 1
        fi
    fi
    
    monitor_loop &
    local pid=$!
    echo $pid > "$PID_FILE"
    
    log "INFO" "데몬 شروع شد (PID: $pid)"
    echo -e "${GREEN}✅ مانیتورینگ شروع شد (PID: $pid)${NC}"
}

# توقف دمون
stop_daemon() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            rm -f "$PID_FILE"
            log "INFO" "데몬 متوقف شد"
            echo -e "${GREEN}✅ مانیتورینگ متوقف شد${NC}"
        else
            rm -f "$PID_FILE"
            log "WARN" "پروسه یافت نشد"
        fi
    else
        log "WARN" "데몬 فعال نیست"
    fi
}

# نمایش وضعیت
show_status() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${GREEN}✅ مانیتورینگ فعال است (PID: $pid)${NC}"
        else
            echo -e "${RED}❌ مانیتورینگ غیرفعال است${NC}"
            rm -f "$PID_FILE"
        fi
    else
        echo -e "${RED}❌ مانیتورینگ غیرفعال است${NC}"
    fi
}

# اجرای اصلی
main() {
    mkdir -p "$LOG_DIR" "$CONFIG_DIR"
    
    case "${1:-}" in
        start)
            start_daemon
            ;;
        stop)
            stop_daemon
            ;;
        status)
            show_status
            ;;
        run-once)
            check_tailscale || restart_tailscale
            check_exit_node || enable_exit_node
            ;;
        *)
            echo "استفاده: $0 {start|stop|status|run-once}"
            echo ""
            echo "آپشن‌ها:"
            echo "  start     - شروع مانیتورینگ در پس‌زمینه"
            echo "  stop      - توقف مانیتورینگ"
            echo "  status    - نمایش وضعیت"
            echo "  run-once  - یکبار بررسی و رفع مشکل"
            ;;
    esac
}

main "$@"
