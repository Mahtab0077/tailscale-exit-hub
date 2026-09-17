# Knowledge Graph Report: tailscale-exit-hub

> Generated via graphify analysis

## Overview

- **Repository**: Tailscale Exit Node & Free VLESS VPN Manager Hub
- **Total Components**: 40 nodes
- **Relationships**: 92 edges (38 call relationships)
- **Core Files**: 3 Python modules

## Architecture

### Components by Module

#### 1. Web Server (`web/server.py`)
- **TailscaleHandler**: Main HTTP request handler
  - `do_GET()`: Routes GET requests
  - `do_POST()`: Routes POST requests
- **Endpoints**:
  - `/` - Home page
  - `/api/status` - System status
  - `/api/users` - User management
  - `/api/health` - Health check
  - `/api/*` - API endpoints

#### 2. VLESS Panel (`web/vless_panel.py`)
- User management system
- VLESS subscription generation
- Configuration management

#### 3. Cleanup Script (`scripts/cleanup_tailscale_nodes.py`)
- Tailscale node cleanup automation
- Environment configuration

## Call Flow

### Request Handling
```
do_GET()
  ├→ serve_home()
  ├→ serve_status() → get_status() → send_json()
  ├→ serve_users() → get_users() → send_json()
  ├→ serve_health()
  └→ handle_api()

do_POST()
  └→ handle_api_post()
```

### Data Flow
- API requests → Handler → Service layer → Response JSON
- User operations → VLESS panel → Config update
- Status queries → System interrogation → JSON response

## Key Relationships

## Node Details

### scripts/cleanup_tailscale_nodes.py
- `cleanup_tailscale_nodes.py` (code)
- `get_env_or_prompt()` (code)
- `main()` (code)

### web/server.py
- `.do_GET()` (code)
- `.do_POST()` (code)
- `.get_status()` (code)
- `.get_users()` (code)
- `.handle_api()` (code)
- `.handle_api_post()` (code)
- `.log_message()` (code)
- `.send_json()` (code)
- `.serve_health()` (code)
- `.serve_home()` (code)
- `.serve_status()` (code)
- `.serve_users()` (code)
- `.toggle_user()` (code)
- `TailscaleHandler` (code)
- `main()` (code)
- `server.py` (code)

### web/vless_panel.py
- `.__init__()` (code)
- `._load_users()` (code)
- `._save_users()` (code)
- `._send_html()` (code)
- `._send_json()` (code)
- `._serve_dashboard()` (code)
- `.add_user()` (code)
- `.do_GET()` (code)
- `.do_POST()` (code)
- `.generate_subscription()` (code)
- `.generate_uuid()` (code)
- `.generate_vless_link()` (code)
- `.get_user()` (code)
- `.get_users()` (code)
- `.log_message()` (code)
- `.remove_user()` (code)
- `.toggle_user()` (code)
- `VLESSHandler` (code)
- `VLESSManager` (code)
- `main()` (code)
- `vless_panel.py` (code)

## Call Relationships

1. `get()` → `home()`
2. `get()` → `status()`
3. `get()` → `users()`
4. `get()` → `health()`
5. `get()` → `api()`
6. `post()` → `post()`
7. `api()` → `status()`
8. `api()` → `users()`
9. `post()` → `json()`
10. `post()` → `user()`
11. `health()` → `json()`
12. `status()` → `status()`
13. `status()` → `json()`
14. `users()` → `users()`
15. `users()` → `json()`
16. `get()` → `dashboard()`
17. `get()` → `json()`
18. `get()` → `users()`
19. `get()` → `subscription()`
20. `get()` → `link()`

... and 18 more relationships
