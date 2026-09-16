#!/bin/bash
# ============================================
# VLESS Subscription Generator
# For GitHub Actions + Cloudflare Tunnel
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
SUBSCRIPTION_DIR="$PROJECT_DIR/subscriptions"
CONFIG_DIR="$PROJECT_DIR/config"

mkdir -p "$SUBSCRIPTION_DIR" "$CONFIG_DIR"

# Generate UUID
generate_uuid() {
    if command -v uuidgen &>/dev/null; then
        uuidgen | tr '[:upper:]' '[:lower:]'
    elif [ -f /proc/sys/kernel/random/uuid ]; then
        cat /proc/sys/kernel/random/uuid
    else
        # Fallback
        cat /dev/urandom | tr -dc 'a-f0-9' | fold -w 32 | head -1 | sed 's/\(........\)\(....\)\(....\)\(....\)\(............\)/\1-\2-\3-\4-\5/'
    fi
}

# Generate VLESS link
generate_vless_link() {
    local email=$1
    local uuid=$2
    local host=$3
    local port=$4
    local path=$5
    local security=$6
    local sni=$7
    
    # VLESS://uuid@host:port?type=ws&security=tls&path=/path&sni=sni#name
    local encoded_path=$(printf '%s' "$path" | sed 's/\//%2F/g')
    local name=$(printf '%s' "$email" | sed 's/@/%40/g' | sed 's/\./%2E/g')
    
    echo "vless://${uuid}@${host}:${port}?type=ws&security=${security}&path=${encoded_path}&sni=${sni}#${name}"
}

# Generate subscription (base64 encoded VLESS links)
generate_subscription() {
    local users_file="$1"
    local output_file="$2"
    local host="$3"
    local port="$4"
    local path="$5"
    local security="$6"
    local sni="$7"
    
    if [ ! -f "$users_file" ]; then
        echo "Users file not found: $users_file" >&2
        return 1
    fi
    
    local links=()
    while IFS= read -r user; do
        local email=$(echo "$user" | jq -r '.email')
        local uuid=$(echo "$user" | jq -r '.uuid')
        local status=$(echo "$user" | jq -r '.status')
        
        if [ "$status" = "active" ] && [ -n "$uuid" ]; then
            local link=$(generate_vless_link "$email" "$uuid" "$host" "$port" "$path" "$security" "$sni")
            links+=("$link")
        fi
    done < <(jq -c '.users[]' "$users_file")
    
    # Join with newline and base64 encode
    printf '%s\n' "${links[@]}" | base64 -w 0 > "$output_file"
    echo "$output_file"
}

# Add VLESS user
add_vless_user() {
    local name=$1
    local email=$2
    local users_file="$SUBSCRIPTION_DIR/users.json"
    
    if [ ! -f "$users_file" ]; then
        echo '{"users":[]}' > "$users_file"
    fi
    
    local uuid=$(generate_uuid)
    local temp=$(mktemp)
    
    jq --arg name "$name" --arg email "$email" --arg uuid "$uuid" \
        '.users += [{"name": $name, "email": $email, "uuid": $uuid, "status": "active", "added": now | todate, "traffic_limit_gb": 100, "traffic_used_gb": 0}]' \
        "$users_file" > "$temp" && mv "$temp" "$users_file"
    
    echo -e "${GREEN}✅ کاربر VLESS اضافه شد: $name ($email)${NC}"
    echo -e "${CYAN}   UUID: $uuid${NC}"
    echo "$uuid"
}

# Remove VLESS user
remove_vless_user() {
    local email=$1
    local users_file="$SUBSCRIPTION_DIR/users.json"
    
    local temp=$(mktemp)
    jq --arg email "$email" '.users |= map(select(.email != $email))' \
        "$users_file" > "$temp" && mv "$temp" "$users_file"
    
    echo -e "${GREEN}✅ کاربر $email حذف شد${NC}"
}

# Disable VLESS user
disable_vless_user() {
    local email=$1
    local users_file="$SUBSCRIPTION_DIR/users.json"
    
    local temp=$(mktemp)
    jq --arg email "$email" \
        '.users |= map(if .email == $email then .status = "disabled" else . end)' \
        "$users_file" > "$temp" && mv "$temp" "$users_file"
    
    echo -e "${YELLOW}⚠️ کاربر $email غیرفعال شد${NC}"
}

# Enable VLESS user
enable_vless_user() {
    local email=$1
    local users_file="$SUBSCRIPTION_DIR/users.json"
    
    local temp=$(mktemp)
    jq --arg email "$email" \
        '.users |= map(if .email == $email then .status = "active" else . end)' \
        "$users_file" > "$temp" && mv "$temp" "$users_file"
    
    echo -e "${GREEN}✅ کاربر $email فعال شد${NC}"
}

# List VLESS users
list_vless_users() {
    local users_file="$SUBSCRIPTION_DIR/users.json"
    
    if [ ! -f "$users_file" ]; then
        echo "No users found"
        return
    fi
    
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                      لیست کاربران VLESS                              ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    jq -r '.users[] | "\(.name) (\(.email)) - \(.status) - UUID: \(.uuid) - Limit: \(.traffic_limit_gb)GB - Used: \(.traffic_used_gb)GB"' "$users_file" 2>/dev/null || echo "کاربری یافت نشد"
    echo ""
}

# Generate subscription file
build_subscription() {
    local host=${1:-"ENTER_CLOUDFLARE_HOST"}
    local port=${2:-"443"}
    local path=${3:-"/vless"}
    local security=${4:-"tls"}
    local sni=${5:-"$host"}
    
    local users_file="$SUBSCRIPTION_DIR/users.json"
    local output_file="$SUBSCRIPTION_DIR/subscription.txt"
    local b64_file="$SUBSCRIPTION_DIR/subscription.b64"
    
    if [ ! -f "$users_file" ]; then
        echo -e "${RED}❌ فایل کاربران یافت نشد${NC}"
        return 1
    fi
    
    # Generate subscription
    generate_subscription "$users_file" "$b64_file" "$host" "$port" "$path" "$security" "$sni"
    
    # Also create readable version
    while IFS= read -r user; do
        local email=$(echo "$user" | jq -r '.email')
        local uuid=$(echo "$user" | jq -r '.uuid')
        local status=$(echo "$user" | jq -r '.status')
        
        if [ "$status" = "active" ] && [ -n "$uuid" ]; then
            generate_vless_link "$email" "$uuid" "$host" "$port" "$path" "$security" "$sni"
        fi
    done < <(jq -c '.users[]' "$users_file") > "$output_file"
    
    echo -e "${GREEN}✅ سابسکرایبشن ساخته شد:${NC}"
    echo -e "${CYAN}   فایل متنی: $output_file${NC}"
    echo -e "${CYAN}   فایل base64: $b64_file${NC}"
    
    cat "$output_file"
}

# Show subscription for specific user
show_user_subscription() {
    local email=$1
    local host=${2:-"ENTER_CLOUDFLARE_HOST"}
    local port=${3:-"443"}
    local path=${4:-"/vless"}
    local security=${5:-"tls"}
    local sni=${6:-"$host"}
    
    local users_file="$SUBSCRIPTION_DIR/users.json"
    
    local user=$(jq -r --arg email "$email" '.users[] | select(.email == $email)' "$users_file" 2>/dev/null)
    
    if [ -z "$user" ] || [ "$user" = "null" ]; then
        echo -e "${RED}❌ کاربر یافت نشد${NC}"
        return 1
    fi
    
    local uuid=$(echo "$user" | jq -r '.uuid')
    local status=$(echo "$user" | jq -r '.status')
    
    if [ "$status" != "active" ]; then
        echo -e "${YELLOW}⚠️ کاربر غیرفعال است${NC}"
        return 1
    fi
    
    local link=$(generate_vless_link "$email" "$uuid" "$host" "$port" "$path" "$security" "$sni")
    
    echo -e "${GREEN}🔗 لینک VLESS برای $email:${NC}"
    echo ""
    echo "$link"
    echo ""
    echo -e "${CYAN}📱 برای استفاده در V2RayNG / Shadowrocket / Clash کپی کنید${NC}"
}

# Main
main() {
    case "${1:-}" in
        add)
            add_vless_user "${2:-}" "${3:-}"
            ;;
        remove)
            remove_vless_user "${2:-}"
            ;;
        disable)
            disable_vless_user "${2:-}"
            ;;
        enable)
            enable_vless_user "${2:-}"
            ;;
        list)
            list_vless_users
            ;;
        build)
            build_subscription "${2:-}" "${3:-}" "${4:-}" "${5:-}" "${6:-}"
            ;;
        show)
            show_user_subscription "${2:-}" "${3:-}" "${4:-}" "${5:-}" "${6:-}"
            ;;
        *)
            echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
            echo -e "${BLUE}║           VLESS Subscription Manager                                 ║${NC}"
            echo -e "${BLUE}╠══════════════════════════════════════════════════════════════════════╣${NC}"
            echo -e "${BLUE}║  add <name> <email>       - اضافه کردن کاربر                        ║${NC}"
            echo -e "${BLUE}║  remove <email>           - حذف کاربر                               ║${NC}"
            echo -e "${BLUE}║  disable <email>          - غیرفعال کردن                           ║${NC}"
            echo -e "${BLUE}║  enable <email>           - فعال کردن                               ║${NC}"
            echo -e "${BLUE}║  list                     - لیست کاربران                            ║${NC}"
            echo -e "${BLUE}║  build [host] [port]      - ساخت سابسکرایبشن کامل                  ║${NC}"
            echo -e "${BLUE}║  show <email> [host]      - نمایش لینک کاربر خاص                   ║${NC}"
            echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
            ;;
    esac
}

main "$@"