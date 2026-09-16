# Knowledge Graph & Architecture Report: tailscale-exit-hub

> Generated via Graphify analysis on `tailscale-exit-hub` codebase.

---

## 📊 Overview
- **Repository:** `Rezzzz77/tailscale-backup` (Tailscale Exit Node & Free VLESS VPN Manager Hub)
- **Total Files:** 15+ core files across scripts, workflows, web panels, and configuration docs.
- **Core Systems:**
  1. **Tailscale Exit Node Automation:** Automated connection, configuration, ephemeral nodes, and cleanups via GitHub Actions and bash scripts.
  2. **VLESS Free VPN System:** Subscription generation, user management, and a Python-based web control panel (`vless_panel.py`).

---

## 🏗️ Architecture & Component Graph

```mermaid
graph TD
    subgraph Core Scripts (scripts/)
        A[start-exit-node.sh] --> B[Tailscale Daemon]
        C[generate-vless-subscription.sh] --> D[VLESS Config Generator]
        E[manage-users.sh] --> F[User & Traffic Management]
        G[auto-restart.sh] --> H[Service Health Monitor]
    end

    subgraph Web Panel (web/)
        I[vless_panel.py] --> F
        I --> D
    end

    subgraph Automation (.github/workflows/)
        J[tailscale-exit-node.yml] --> A
        K[vless-free.yml] --> I
    end

    subgraph Entrypoint
        L[start-vless-manager.sh] --> I
    end
```

---

## 📁 Key Components & Modules

### 1. Web Management Panel (`web/vless_panel.py`)
- **HTTP Server / API:** Built on Python's built-in `http.server` with JSON REST APIs.
- **Features:**
  - Add/Remove/Disable users (`/api/user/add`, `/api/user/remove`).
  - List active users and usage stats (`/api/users`).
  - Generate VLESS client subscription links encoded in Base64 (`/api/subscription`).

### 2. Startup & Orchestration (`start-vless-manager.sh`)
- Initializes environment and starts the VLESS panel on port `9090`.
- Manages process lifecycle (`vless-panel.pid`), signal traps (`INT`, `TERM`), and quick testing commands.

### 3. Tailscale Automation (`scripts/` & `.github/workflows/`)
- **`tailscale-exit-node.yml`**: Automates running Tailscale exit nodes with ephemeral flags and authentication keys.
- **`auto-restart.sh`**: Keeps services running robustly against transient drops.

---

## 🚀 Quick Reference & Endpoints
- **Web Dashboard:** `http://localhost:9090`
- **Add User API:** `POST /api/user/add`
- **Subscription API:** `GET /api/subscription?host=<tunnel-host>`
