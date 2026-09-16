#!/bin/bash
# ============================================
# Tailscale Exit Node - مدیریت کاربران
# ============================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
USERS_FILE="$PROJECT_DIR/users/users.json"
LOG_DIR="$PROJECT_DIR/logs"

# لاگ
log() {
    echo -e "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG_DIR/users.log"
}

# ایجاد فایل کاربران
init_users() {
    if [ ! -f "$USERS_FILE" ]; then
        echo '{"users":[]}' > "$USERS_FILE"
        log "${GREEN}✅ فایل کاربران ایجاد شد${NC}"
    fi
}

# اضافه کردن کاربر
add_user() {
    local name=$1
    local email=$2
    
    init_users
    
    # بررسی تکراری نبودن
    if jq -e ".users[] | select(.email==\"$email\")" "$USERS_FILE" &>/dev/null; then
        log "${YELLOW}⚠️ کاربر $email قبلاً اضافه شده${NC}"
        return 1
    fi
    
    # اضافه کردن
    local temp=$(mktemp)
    jq --arg name "$name" --arg email "$email" \
        '.users += [{"name": $name, "email": $email, "status": "active", "added": now | todate}]' \
        "$USERS_FILE" > "$temp" && mv "$temp" "$USERS_FILE"
    
    log "${GREEN}✅ کاربر $name ($email) اضافه شد${NC}"
}

# حذف کاربر
remove_user() {
    local email=$1
    
    local temp=$(mktemp)
    jq --arg email "$email" '.users |= map(select(.email != $email))' \
        "$USERS_FILE" > "$temp" && mv "$temp" "$USERS_FILE"
    
    log "${GREEN}✅ کاربر $email حذف شد${NC}"
}

# غیرفعال کردن کاربر
disable_user() {
    local email=$1
    
    local temp=$(mktemp)
    jq --arg email "$email" \
        '.users |= map(if .email == $email then .status = "disabled" else . end)' \
        "$USERS_FILE" > "$temp" && mv "$temp" "$USERS_FILE"
    
    log "${YELLOW}⚠️ کاربر $email غیرفعال شد${NC}"
}

# فعال کردن کاربر
enable_user() {
    local email=$1
    
    local temp=$(mktemp)
    jq --arg email "$email" \
        '.users |= map(if .email == $email then .status = "active" else . end)' \
        "$USERS_FILE" > "$temp" && mv "$temp" "$USERS_FILE"
    
    log "${GREEN}✅ کاربر $email فعال شد${NC}"
}

# نمایش لیست کاربران
list_users() {
    init_users
    
    echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║       لیست کاربران                       ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
    echo ""
    
    jq -r '.users[] | "\(.name) (\(.email)) - \(.status)"' "$USERS_FILE" 2>/dev/null || echo "کاربری یافت نشد"
    echo ""
}

# نمایش کاربران متصل
show_connected() {
    echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║       کاربران متصل                       ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
    echo ""
    
    tailscale status 2>/dev/null | tail -n +2 || echo "Tailscale متصل نیست"
    echo ""
}

# منوی اصلی
show_menu() {
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     مدیریت کاربران                       ║${NC}"
    echo -e "${BLUE}╠══════════════════════════════════════════╣${NC}"
    echo -e "${BLUE}║  1) اضافه کردن کاربر                     ║${NC}"
    echo -e "${BLUE}║  2) حذف کاربر                            ║${NC}"
    echo -e "${BLUE}║  3) فعال/غیرفعال کردن                    ║${NC}"
    echo -e "${BLUE}║  4) لیست کاربران                         ║${NC}"
    echo -e "${BLUE}║  5) کاربران متصل                         ║${NC}"
    echo -e "${BLUE}║  6) خروج                                 ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
    echo ""
}

# اجرای اصلی
main() {
    mkdir -p "$LOG_DIR" "$(dirname "$USERS_FILE")"
    
    case "${1:-}" in
        add)
            add_user "${2:-}" "${3:-}"
            ;;
        remove)
            remove_user "${2:-}"
            ;;
        disable)
            disable_user "${2:-}"
            ;;
        enable)
            enable_user "${2:-}"
            ;;
        list)
            list_users
            ;;
        connected)
            show_connected
            ;;
        *)
            show_menu
            read -p "انتخاب: " choice
            case $choice in
                1)
                    read -p "نام: " name
                    read -p "ایمیل: " email
                    add_user "$name" "$email"
                    ;;
                2)
                    read -p "ایمیل کاربر: " email
                    remove_user "$email"
                    ;;
                3)
                    read -p "ایمیل کاربر: " email
                    read -p "فعال/غیرفعال (active/disabled): " status
                    if [ "$status" = "active" ]; then
                        enable_user "$email"
                    else
                        disable_user "$email"
                    fi
                    ;;
                4) list_users ;;
                5) show_connected ;;
                6) exit 0 ;;
                *) echo -e "${RED}انتخاب نامعتبر!${NC}" ;;
            esac
            ;;
    esac
}

main "$@"
