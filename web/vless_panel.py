#!/usr/bin/env python3
"""
VLESS Subscription Manager - پنل مدیریت وب
"""

import http.server
import json
import subprocess
import os
import base64
import urllib.parse
from urllib.parse import parse_qs, urlparse

# تنظیمات
PORT = int(os.environ.get('PORT', 9090))
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUBSCRIPTION_DIR = os.path.join(PROJECT_DIR, 'subscriptions')
USERS_FILE = os.path.join(SUBSCRIPTION_DIR, 'users.json')
SCRIPTS_DIR = os.path.join(PROJECT_DIR, 'scripts')

class VLESSManager:
    def __init__(self):
        os.makedirs(SUBSCRIPTION_DIR, exist_ok=True)
        if not os.path.exists(USERS_FILE):
            self._save_users({'users': []})
    
    def _load_users(self):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {'users': []}
    
    def _save_users(self, data):
        with open(USERS_FILE, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def generate_uuid(self):
        import uuid
        return str(uuid.uuid4())
    
    def add_user(self, name, email, traffic_gb=100):
        data = self._load_users()
        # بررسی تکراری نبودن
        for u in data['users']:
            if u['email'] == email:
                return False, "کاربر قبلاً اضافه شده"
        
        uuid = self.generate_uuid()
        user = {
            'name': name,
            'email': email,
            'uuid': uuid,
            'status': 'active',
            'traffic_limit_gb': traffic_gb,
            'traffic_used_gb': 0,
            'added': str(os.path.getctime(USERS_FILE))
        }
        data['users'].append(user)
        self._save_users(data)
        return True, uuid
    
    def remove_user(self, email):
        data = self._load_users()
        initial_len = len(data['users'])
        data['users'] = [u for u in data['users'] if u['email'] != email]
        if len(data['users']) < initial_len:
            self._save_users(data)
            return True, "کاربر حذف شد"
        return False, "کاربر یافت نشد"
    
    def toggle_user(self, email, status=None):
        data = self._load_users()
        for u in data['users']:
            if u['email'] == email:
                if status:
                    u['status'] = status
                else:
                    u['status'] = 'active' if u.get('status') != 'active' else 'disabled'
                self._save_users(data)
                return True, f"کاربر {u['status']} شد"
        return False, "کاربر یافت نشد"
    
    def get_users(self):
        return self._load_users()['users']
    
    def get_user(self, email):
        for u in self.get_users():
            if u['email'] == email:
                return u
        return None
    
    def generate_vless_link(self, email, host, port=443, path='/vless', security='tls'):
        user = self.get_user(email)
        if not user:
            return None
        
        uuid = user['uuid']
        encoded_path = urllib.parse.quote(path, safe='')
        encoded_name = urllib.parse.quote(email, safe='')
        sni = host
        
        link = f"vless://{uuid}@{host}:{port}?type=ws&security={security}&path={encoded_path}&sni={sni}#{encoded_name}"
        return link
    
    def generate_subscription(self, host, port=443, path='/vless', security='tls'):
        users = [u for u in self.get_users() if u.get('status') == 'active']
        links = []
        for u in users:
            link = self.generate_vless_link(u['email'], host, port, path, security)
            if link:
                links.append(link)
        
        if not links:
            return None
        
        # Base64 encode
        content = '\n'.join(links)
        return base64.b64encode(content.encode()).decode()

class VLESSHandler(http.server.BaseHTTPRequestHandler):
    manager = VLESSManager()
    
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def _send_html(self, html):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        
        if path == '/':
            self._serve_dashboard()
        elif path == '/api/users':
            self._send_json({'users': self.manager.get_users()})
        elif path == '/api/subscription':
            host = params.get('host', ['your-tunnel.trycloudflare.com'])[0]
            sub = self.manager.generate_subscription(host)
            if sub:
                self._send_json({'subscription': sub, 'host': host})
            else:
                self._send_json({'error': 'No active users'}, 404)
        elif path == '/api/user/link':
            email = params.get('email', [''])[0]
            host = params.get('host', ['your-tunnel.trycloudflare.com'])[0]
            link = self.manager.generate_vless_link(email, host)
            if link:
                self._send_json({'link': link, 'email': email, 'host': host})
            else:
                self._send_json({'error': 'User not found'}, 404)
        elif path == '/health':
            self._send_json({'status': 'ok'})
        else:
            self.send_error(404)
    
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            params = json.loads(post_data) if post_data else {}
        except:
            params = {}
        
        if path == '/api/user/add':
            name = params.get('name', '')
            email = params.get('email', '')
            traffic = params.get('traffic_gb', 100)
            if not name or not email:
                self._send_json({'error': 'name and email required'}, 400)
                return
            ok, result = self.manager.add_user(name, email, traffic)
            if ok:
                self._send_json({'success': True, 'uuid': result})
            else:
                self._send_json({'error': result}, 400)
        
        elif path == '/api/user/remove':
            email = params.get('email', '')
            ok, msg = self.manager.remove_user(email)
            if ok:
                self._send_json({'success': True})
            else:
                self._send_json({'error': msg}, 404)
        
        elif path == '/api/user/toggle':
            email = params.get('email', '')
            status = params.get('status')
            ok, msg = self.manager.toggle_user(email, status)
            if ok:
                self._send_json({'success': True, 'status': msg})
            else:
                self._send_json({'error': msg}, 404)
        
        else:
            self.send_error(404)
    
    def _serve_dashboard(self):
        html = """<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VLESS Manager - پنل مدیریت</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: Tahoma, Arial, sans-serif;
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; padding: 20px; }
        .header h1 { color: #00d4ff; font-size: 28px; }
        .header p { color: #aaa; margin-top: 5px; }
        .card {
            background: rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 20px;
            margin: 15px 0;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        .card h2 { color: #00d4ff; margin-bottom: 15px; font-size: 18px; }
        .form-group { margin: 10px 0; }
        .form-group label { display: block; margin-bottom: 5px; color: #ccc; font-size: 14px; }
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            background: rgba(0,0,0,0.3);
            color: #fff;
            font-size: 14px;
        }
        .form-group input:focus { outline: none; border-color: #00d4ff; }
        .btn {
            background: linear-gradient(135deg, #00d4ff, #0099ff);
            color: #fff;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            margin: 5px;
            transition: transform 0.2s;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn-danger { background: linear-gradient(135deg, #ff4444, #cc0000); }
        .btn-warning { background: linear-gradient(135deg, #ffaa00, #ff8800); }
        .btn-success { background: linear-gradient(135deg, #00cc66, #009944); }
        .btn-info { background: linear-gradient(135deg, #9966ff, #7744dd); }
        .user-list { list-style: none; }
        .user-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            flex-wrap: wrap;
            gap: 10px;
        }
        .user-info { flex: 1; min-width: 200px; }
        .user-name { font-weight: bold; color: #fff; }
        .user-email { color: #aaa; font-size: 12px; }
        .user-uuid { color: #666; font-size: 11px; font-family: monospace; }
        .user-status {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }
        .status-active { background: rgba(0,255,136,0.2); color: #00ff88; }
        .status-disabled { background: rgba(255,68,68,0.2); color: #ff4444; }
        .user-actions { display: flex; gap: 5px; flex-wrap: wrap; }
        .user-actions .btn { padding: 6px 12px; font-size: 12px; }
        .link-box {
            background: rgba(0,0,0,0.4);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            padding: 12px;
            margin: 10px 0;
            word-break: break-all;
            font-family: monospace;
            font-size: 12px;
            color: #00ff88;
            display: none;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-box {
            background: rgba(0,212,255,0.1);
            border: 1px solid rgba(0,212,255,0.3);
            border-radius: 12px;
            padding: 15px;
            text-align: center;
        }
        .stat-number { font-size: 32px; font-weight: bold; color: #00d4ff; }
        .stat-label { color: #aaa; font-size: 12px; margin-top: 5px; }
        .toast {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            border-radius: 8px;
            color: #fff;
            font-weight: bold;
            z-index: 1000;
            display: none;
        }
        .toast.success { background: linear-gradient(135deg, #00cc66, #009944); }
        .toast.error { background: linear-gradient(135deg, #ff4444, #cc0000); }
        .toggle {
            position: relative;
            width: 50px;
            height: 26px;
            background: rgba(255,255,255,0.2);
            border-radius: 13px;
            cursor: pointer;
            transition: background 0.3s;
        }
        .toggle.on { background: #00ff88; }
        .toggle::after {
            content: '';
            position: absolute;
            width: 22px;
            height: 22px;
            border-radius: 50%;
            background: #fff;
            top: 2px;
            left: 2px;
            transition: transform 0.3s;
        }
        .toggle.on::after { transform: translateX(24px); }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .tab {
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            background: rgba(255,255,255,0.1);
            border: 1px solid transparent;
        }
        .tab.active {
            background: rgba(0,212,255,0.2);
            border-color: #00d4ff;
            color: #00d4ff;
        }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        @media (max-width: 600px) {
            .user-item { flex-direction: column; align-items: flex-start; }
            .user-actions { width: 100%; justify-content: center; }
        }
    </style>
</head>
<body>
    <div class="toast" id="toast"></div>
    <div class="container">
        <div class="header">
            <h1>⚡ VLESS Manager</h1>
            <p>پنل مدیریت کاربران و سابسکرایبشن</p>
        </div>
        
        <div class="stats">
            <div class="stat-box">
                <div class="stat-number" id="total-users">0</div>
                <div class="stat-label">کل کاربران</div>
            </div>
            <div class="stat-box">
                <div class="stat-number" id="active-users">0</div>
                <div class="stat-label">فعال</div>
            </div>
            <div class="stat-box">
                <div class="stat-number" id="total-traffic">0 GB</div>
                <div class="stat-label">مجموع ترافیک</div>
            </div>
        </div>
        
        <div class="tabs">
            <div class="tab active" onclick="switchTab('users')">👥 کاربران</div>
            <div class="tab" onclick="switchTab('add')">➕ اضافه کردن</div>
            <div class="tab" onclick="switchTab('subscription')">🔗 سابسکرایبشن</div>
        </div>
        
        <div id="tab-users" class="tab-content active">
            <div class="card">
                <h2>👥 لیست کاربران</h2>
                <div id="users-list">در حال بارگذاری...</div>
            </div>
        </div>
        
        <div id="tab-add" class="tab-content">
            <div class="card">
                <h2>➕ اضافه کردن کاربر جدید</h2>
                <div class="form-group">
                    <label>نام:</label>
                    <input type="text" id="add-name" placeholder="نام کاربر">
                </div>
                <div class="form-group">
                    <label>ایمیل / شناسه:</label>
                    <input type="email" id="add-email" placeholder="user@example.com">
                </div>
                <div class="form-group">
                    <label>سقف ترافیک (GB):</label>
                    <input type="number" id="add-traffic" value="100" min="1">
                </div>
                <button class="btn btn-success" onclick="addUser()">✅ اضافه کردن</button>
            </div>
        </div>
        
        <div id="tab-subscription" class="tab-content">
            <div class="card">
                <h2>🔗 سابسکرایبشن VLESS</h2>
                <div class="form-group">
                    <label>Cloudflare Tunnel Host:</label>
                    <input type="text" id="sub-host" placeholder="your-tunnel.trycloudflare.com">
                </div>
                <div class="form-group">
                    <label>Port:</label>
                    <input type="number" id="sub-port" value="443">
                </div>
                <div class="form-group">
                    <label>Path:</label>
                    <input type="text" id="sub-path" value="/vless">
                </div>
                <button class="btn btn-info" onclick="generateSubscription()">🔨 ساخت سابسکرایبشن</button>
                
                <div id="subscription-result" class="link-box"></div>
                <button class="btn btn-warning" id="copy-sub" style="display:none" onclick="copySubscription()">📋 کپی Base64</button>
            </div>
        </div>
    </div>
    
    <script>
        function showToast(msg, type='success') {
            const t = document.getElementById('toast');
            t.textContent = msg;
            t.className = 'toast ' + type;
            t.style.display = 'block';
            setTimeout(() => t.style.display = 'none', 3000);
        }
        
        function switchTab(name) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('tab-' + name).classList.add('active');
        }
        
        async function loadUsers() {
            const res = await fetch('/api/users');
            const data = await res.json();
            const users = data.users || [];
            
            document.getElementById('total-users').textContent = users.length;
            document.getElementById('active-users').textContent = users.filter(u => u.status === 'active').length;
            document.getElementById('total-traffic').textContent = users.reduce((a,b) => a + (b.traffic_limit_gb || 0), 0) + ' GB';
            
            let html = '<ul class="user-list">';
            users.forEach(u => {
                const statusClass = u.status === 'active' ? 'status-active' : 'status-disabled';
                const statusText = u.status === 'active' ? 'فعال' : 'غیرفعال';
                const toggleClass = u.status === 'active' ? 'on' : '';
                html += `
                    <li class="user-item">
                        <div class="user-info">
                            <div class="user-name">${u.name}</div>
                            <div class="user-email">${u.email}</div>
                            <div class="user-uuid">${u.uuid}</div>
                            <div style="margin-top:5px">
                                <span class="user-status ${statusClass}">${statusText}</span>
                                <span style="color:#aaa;font-size:11px;margin-left:10px">ترافیک: ${u.traffic_used_gb || 0}/${u.traffic_limit_gb} GB</span>
                            </div>
                        </div>
                        <div class="user-actions">
                            <div class="toggle ${toggleClass}" onclick="toggleUser('${u.email}')" title="فعال/غیرفعال"></div>
                            <button class="btn btn-info" onclick="showLink('${u.email}')">📋 لینک</button>
                            <button class="btn btn-danger" onclick="removeUser('${u.email}')">🗑️ حذف</button>
                        </div>
                    </li>
                `;
            });
            html += '</ul>';
            document.getElementById('users-list').innerHTML = html;
        }
        
        async function addUser() {
            const name = document.getElementById('add-name').value;
            const email = document.getElementById('add-email').value;
            const traffic = document.getElementById('add-traffic').value;
            
            if (!name || !email) {
                showToast('نام و ایمیل الزامی است', 'error');
                return;
            }
            
            const res = await fetch('/api/user/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name, email, traffic_gb: parseInt(traffic)})
            });
            const data = await res.json();
            if (data.success) {
                showToast('کاربر اضافه شد ✅');
                document.getElementById('add-name').value = '';
                document.getElementById('add-email').value = '';
                loadUsers();
            } else {
                showToast(data.error || 'خطا', 'error');
            }
        }
        
        async function removeUser(email) {
            if (!confirm('آیا مطمئن هستید؟')) return;
            const res = await fetch('/api/user/remove', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email})
            });
            const data = await res.json();
            if (data.success) {
                showToast('کاربر حذف شد');
                loadUsers();
            }
        }
        
        async function toggleUser(email) {
            const res = await fetch('/api/user/toggle', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email})
            });
            const data = await res.json();
            showToast(data.status || 'تغییر وضعیت انجام شد');
            loadUsers();
        }
        
        async function showLink(email) {
            const host = document.getElementById('sub-host').value || 'your-tunnel.trycloudflare.com';
            const res = await fetch(`/api/user/link?email=${email}&host=${host}`);
            const data = await res.json();
            if (data.link) {
                prompt('لینک VLESS را کپی کنید:', data.link);
            }
        }
        
        async function generateSubscription() {
            const host = document.getElementById('sub-host').value;
            if (!host) {
                showToast('Cloudflare Host را وارد کنید', 'error');
                return;
            }
            const res = await fetch(`/api/subscription?host=${host}`);
            const data = await res.json();
            if (data.subscription) {
                const box = document.getElementById('subscription-result');
                box.textContent = data.subscription;
                box.style.display = 'block';
                document.getElementById('copy-sub').style.display = 'inline-block';
                showToast('سابسکرایبشن ساخته شد ✅');
            } else {
                showToast('کاربری یافت نشد', 'error');
            }
        }
        
        function copySubscription() {
            const text = document.getElementById('subscription-result').textContent;
            navigator.clipboard.writeText(text);
            showToast('کپی شد! 📋');
        }
        
        // بارگذاری خودکار
        loadUsers();
        setInterval(loadUsers, 5000);
    </script>
</body>
</html>"""
        self._send_html(html)
    
    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")

def main():
    print(f"🚀 VLESS Manager Panel")
    print(f"📍 http://localhost:{PORT}")
    print(f"📍 http://0.0.0.0:{PORT}")
    print()
    print("Quick Start:")
    print("  1. Add users via dashboard")
    print("  2. Run GitHub Actions workflow to get Cloudflare Tunnel URL")
    print("  3. Enter tunnel host in dashboard")
    print("  4. Generate subscription links")
    print()
    
    server = http.server.HTTPServer(('0.0.0.0', PORT), VLESSHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 متوقف شد")
        server.server_close()

if __name__ == '__main__':
    main()
