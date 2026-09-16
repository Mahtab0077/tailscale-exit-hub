#!/usr/bin/env python3
"""
Tailscale Exit Node - پنل مدیریت
"""

import http.server
import json
import subprocess
import os
from urllib.parse import parse_qs, urlparse

# تنظیمات
PORT = int(os.environ.get('PORT', 8080))
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS_FILE = os.path.join(PROJECT_DIR, 'users', 'users.json')

class TailscaleHandler(http.server.BaseHTTPRequestHandler):
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        
        if path == '/':
            self.serve_home()
        elif path == '/status':
            self.serve_status()
        elif path == '/users':
            self.serve_users()
        elif path == '/health':
            self.serve_health()
        elif path.startswith('/api/'):
            self.handle_api(path, params)
        else:
            self.send_error(404)
    
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        params = json.loads(post_data) if post_data else {}
        
        if path.startswith('/api/'):
            self.handle_api_post(path, params)
        else:
            self.send_error(404)
    
    def serve_home(self):
        html = """
<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tailscale Exit Node Manager</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Tahoma, Arial; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        .card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            backdrop-filter: blur(10px);
        }
        h1 { text-align: center; margin-bottom: 30px; color: #00d4ff; }
        h2 { color: #00d4ff; margin-bottom: 15px; }
        .status { 
            display: flex; 
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .status.online { color: #00ff88; }
        .status.offline { color: #ff4444; }
        .btn {
            background: #00d4ff;
            color: #000;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            margin: 5px;
        }
        .btn:hover { background: #00a8cc; }
        .btn.danger { background: #ff4444; }
        .btn.danger:hover { background: #cc0000; }
        .user-list { list-style: none; }
        .user-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .user-actions { display: flex; gap: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Tailscale Exit Node Manager</h1>
        
        <div class="card">
            <h2>📡 وضعیت سیستم</h2>
            <div id="status">در حال بارگذاری...</div>
        </div>
        
        <div class="card">
            <h2>👥 کاربران</h2>
            <div id="users">در حال بارگذاری...</div>
            <button class="btn" onclick="refreshAll()">🔄 بروزرسانی</button>
        </div>
        
        <div class="card">
            <h2>🎮 کنترل‌ها</h2>
            <button class="btn" onclick="enableExitNode()">✅ فعال کردن Exit Node</button>
            <button class="btn danger" onclick="disableExitNode()">❌ غیرفعال کردن Exit Node</button>
            <button class="btn" onclick="restartTailscale()">🔄 ریست Tailscale</button>
        </div>
    </div>
    
    <script>
        async function fetchStatus() {
            const res = await fetch('/api/status');
            const data = await res.json();
            document.getElementById('status').innerHTML = `
                <div class="status ${data.tailscale ? 'online' : 'offline'}">
                    <span>Tailscale:</span>
                    <span>${data.tailscale ? '✅ متصل' : '❌ قطع'}</span>
                </div>
                <div class="status ${data.exitNode ? 'online' : 'offline'}">
                    <span>Exit Node:</span>
                    <span>${data.exitNode ? '✅ فعال' : '❌ غیرفعال'}</span>
                </div>
                <div class="status">
                    <span>IP:</span>
                    <span>${data.ip || 'N/A'}</span>
                </div>
            `;
        }
        
        async function fetchUsers() {
            const res = await fetch('/api/users');
            const data = await res.json();
            let html = '<ul class="user-list">';
            data.users.forEach(user => {
                html += `
                    <li class="user-item">
                        <span>${user.name} (${user.email})</span>
                        <div class="user-actions">
                            <button class="btn" onclick="toggleUser('${user.email}', '${user.status}')">
                                ${user.status === 'active' ? '🔴 قطع' : '🟢 وصل'}
                            </button>
                        </div>
                    </li>
                `;
            });
            html += '</ul>';
            document.getElementById('users').innerHTML = html;
        }
        
        async function enableExitNode() {
            await fetch('/api/exit-node/enable', { method: 'POST' });
            refreshAll();
        }
        
        async function disableExitNode() {
            await fetch('/api/exit-node/disable', { method: 'POST' });
            refreshAll();
        }
        
        async function restartTailscale() {
            await fetch('/api/restart', { method: 'POST' });
            refreshAll();
        }
        
        async function toggleUser(email, currentStatus) {
            const newStatus = currentStatus === 'active' ? 'disabled' : 'active';
            await fetch('/api/user/toggle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, status: newStatus })
            });
            refreshAll();
        }
        
        function refreshAll() {
            fetchStatus();
            fetchUsers();
        }
        
        // بارگذاری اولیه
        refreshAll();
        
        // بروزرسانی خودکار هر ۱۰ ثانیه
        setInterval(refreshAll, 10000);
    </script>
</body>
</html>
"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_status(self):
        status = self.get_status()
        self.send_json(status)
    
    def serve_users(self):
        users = self.get_users()
        self.send_json({'users': users})
    
    def serve_health(self):
        self.send_json({'status': 'ok'})
    
    def handle_api(self, path, params):
        if path == '/api/status':
            self.serve_status()
        elif path == '/api/users':
            self.serve_users()
        else:
            self.send_error(404)
    
    def handle_api_post(self, path, params):
        if path == '/api/exit-node/enable':
            subprocess.run(['tailscale', 'set', '--advertise-exit-node'], capture_output=True)
            self.send_json({'success': True})
        elif path == '/api/exit-node/disable':
            subprocess.run(['tailscale', 'set', '--exit-node='], capture_output=True)
            self.send_json({'success': True})
        elif path == '/api/restart':
            subprocess.run(['tailscale', 'down'], capture_output=True)
            subprocess.run(['tailscale', 'up', '--accept-routes'], capture_output=True)
            self.send_json({'success': True})
        elif path == '/api/user/toggle':
            self.toggle_user(params.get('email'), params.get('status'))
            self.send_json({'success': True})
        else:
            self.send_error(404)
    
    def get_status(self):
        try:
            # بررسی Tailscale
            ts_result = subprocess.run(['tailscale', 'status'], capture_output=True, text=True)
            tailscale = ts_result.returncode == 0
            
            # بررسی Exit Node
            exit_node = False
            if tailscale:
                json_result = subprocess.run(['tailscale', 'status', '--json'], capture_output=True, text=True)
                if json_result.returncode == 0:
                    data = json.loads(json_result.stdout)
                    exit_status = data.get('Self', {}).get('ExitNodeStatus', {}).get('BriefExitNode', '')
                    exit_node = bool(exit_status)
            
            # IP
            ip = None
            if tailscale:
                ip_result = subprocess.run(['tailscale', 'ip', '-4'], capture_output=True, text=True)
                if ip_result.returncode == 0:
                    ip = ip_result.stdout.strip()
            
            return {
                'tailscale': tailscale,
                'exitNode': exit_node,
                'ip': ip
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_users(self):
        try:
            if os.path.exists(USERS_FILE):
                with open(USERS_FILE, 'r') as f:
                    return json.load(f).get('users', [])
            return []
        except Exception as e:
            return []
    
    def toggle_user(self, email, status):
        try:
            if os.path.exists(USERS_FILE):
                with open(USERS_FILE, 'r') as f:
                    data = json.load(f)
                
                for user in data.get('users', []):
                    if user.get('email') == email:
                        user['status'] = status
                        break
                
                with open(USERS_FILE, 'w') as f:
                    json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error: {e}")
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")

def main():
    print(f"🚀 Tailscale Exit Node Manager")
    print(f"📍 http://localhost:{PORT}")
    print(f"📍 http://0.0.0.0:{PORT}")
    print()
    
    server = http.server.HTTPServer(('0.0.0.0', PORT), TailscaleHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 متوقف شد")
        server.server_close()

if __name__ == '__main__':
    main()
