#!/usr/bin/env python3
"""
VLESS Subscription Manager - پنل مدیریت وب
"""

import http.server
import json
import os
import base64
import uuid
import urllib.parse
from urllib.parse import parse_qs, urlparse

# تنظیمات
PORT = int(os.environ.get('PORT', 9090))
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUBSCRIPTION_DIR = os.path.join(PROJECT_DIR, 'subscriptions')
USERS_FILE = os.path.join(SUBSCRIPTION_DIR, 'users.json')

class VLESSManager:
    def __init__(self):
        os.makedirs(SUBSCRIPTION_DIR, exist_ok=True)
        if not os.path.exists(USERS_FILE):
            self._save_users({'users': []})
    
    def _load_users(self):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'users': []}
    
    def _save_users(self, data):
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add_user(self, name, email, traffic_gb=100):
        data = self._load_users()
        for u in data['users']:
            if u['email'] == email:
                return False, "کاربر قبلاً اضافه شده"
        
        user_uuid = str(uuid.uuid4())
        user = {
            'name': name,
            'email': email,
            'uuid': user_uuid,
            'status': 'active',
            'traffic_limit_gb': traffic_gb,
            'traffic_used_gb': 0,
            'added': str(os.path.getctime(USERS_FILE))
        }
        data['users'].append(user)
        self._save_users(data)
        return True, user_uuid
    
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
        
        user_uuid = user['uuid']
        encoded_path = urllib.parse.quote(path, safe='')
        encoded_name = urllib.parse.quote(email, safe='')
        
        link = f"vless://{user_uuid}@{host}:{port}?type=ws&security={security}&path={encoded_path}&sni={host}#{encoded_name}"
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
        
        try:
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
                self._send_json({'error': 'Not found'}, 404)
        except Exception as e:
            self._send_json({'error': str(e)}, 500)
    
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            params = json.loads(post_data.decode('utf-8')) if post_data else {}
        except:
            params = {}
        
        try:
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
                ok, msg = self.manager.toggle_user(email)
                if ok:
                    self._send_json({'status': msg, 'success': True})
                else:
                    self._send_json({'error': msg}, 404)
            else:
                self._send_json({'error': 'Not found'}, 404)
        except Exception as e:
            self._send_json({'error': str(e)}, 500)
    
    def _serve_dashboard(self):
        html = """<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VLESS Manager Panel</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
            color: #fff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 20px;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 48px;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #00d4ff, #0099ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .card {
            background: rgba(15, 52, 96, 0.8);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            border: 1px solid rgba(0, 212, 255, 0.2);
            backdrop-filter: blur(10px);
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-box {
            background: rgba(0, 212, 255, 0.1);
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 12px;
            padding: 15px;
            text-align: center;
        }
        .stat-number { font-size: 32px; font-weight: bold; color: #00d4ff; }
        .stat-label { color: #aaa; font-size: 12px; margin-top: 5px; }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #00d4ff;
            font-weight: bold;
        }
        .form-group input {
            width: 100%;
            padding: 10px;
            border: 1px solid rgba(0, 212, 255, 0.3);
            background: rgba(0, 0, 0, 0.3);
            border-radius: 6px;
            color: #fff;
            font-size: 14px;
        }
        .btn {
            background: linear-gradient(135deg, #00d4ff, #0099ff);
            color: #fff;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            transition: transform 0.2s;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn-danger { background: #ff4444; }
        .btn-success { background: #00cc66; }
        .user-list { list-style: none; }
        .user-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            flex-wrap: wrap;
        }
        .user-info { flex: 1; }
        .user-name { font-weight: bold; }
        .user-email { color: #aaa; font-size: 12px; }
        .link-box {
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 6px;
            padding: 12px;
            margin: 10px 0;
            word-break: break-all;
            font-family: monospace;
            font-size: 12px;
            color: #00ff88;
            max-height: 200px;
            overflow-y: auto;
        }
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
        .toast.success { background: #00cc66; }
        .toast.error { background: #ff4444; }
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
        </div>
        
        <div class="card">
            <h2>👥 لیست کاربران</h2>
            <div id="users-list">در حال بارگذاری...</div>
        </div>
        
        <div class="card">
            <h2>➕ اضافه کردن کاربر جدید</h2>
            <div class="form-group">
                <label>نام:</label>
                <input type="text" id="add-name" placeholder="نام کاربر">
            </div>
            <div class="form-group">
                <label>ایمیل:</label>
                <input type="email" id="add-email" placeholder="user@example.com">
            </div>
            <div class="form-group">
                <label>سقف ترافیک (GB):</label>
                <input type="number" id="add-traffic" value="100" min="1">
            </div>
            <button class="btn btn-success" onclick="addUser()">✅ اضافه کردن</button>
        </div>
        
        <div class="card">
            <h2>🔗 سابسکرایبشن VLESS</h2>
            <div class="form-group">
                <label>Cloudflare Tunnel Host:</label>
                <input type="text" id="sub-host" placeholder="your-tunnel.trycloudflare.com">
            </div>
            <button class="btn" onclick="generateSubscription()">🔨 ساخت سابسکرایبشن</button>
            <div id="subscription-result" class="link-box" style="display:none"></div>
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
        
        async function loadUsers() {
            try {
                const res = await fetch('/api/users');
                const data = await res.json();
                const users = data.users || [];
                
                document.getElementById('total-users').textContent = users.length;
                document.getElementById('active-users').textContent = users.filter(u => u.status === 'active').length;
                
                let html = '<ul class="user-list">';
                users.forEach(u => {
                    html += `
                        <li class="user-item">
                            <div class="user-info">
                                <div class="user-name">${u.name}</div>
                                <div class="user-email">${u.email}</div>
                                <div style="font-size:11px;color:#aaa">UUID: ${u.uuid}</div>
                            </div>
                            <div>
                                <button class="btn" onclick="removeUser('${u.email}')" style="background:#ff4444">🗑️ حذف</button>
                            </div>
                        </li>
                    `;
                });
                html += '</ul>';
                document.getElementById('users-list').innerHTML = html;
            } catch(e) {
                document.getElementById('users-list').innerHTML = 'خطا در بارگذاری: ' + e;
            }
        }
        
        async function addUser() {
            const name = document.getElementById('add-name').value;
            const email = document.getElementById('add-email').value;
            const traffic = document.getElementById('add-traffic').value;
            
            if (!name || !email) {
                showToast('نام و ایمیل الزامی است', 'error');
                return;
            }
            
            try {
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
            } catch(e) {
                showToast('خطا: ' + e, 'error');
            }
        }
        
        async function removeUser(email) {
            if (!confirm('آیا مطمئن هستید؟')) return;
            try {
                const res = await fetch('/api/user/remove', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({email})
                });
                const data = await res.json();
                if (data.success) {
                    showToast('کاربر حذف شد');
                    loadUsers();
                } else {
                    showToast(data.error, 'error');
                }
            } catch(e) {
                showToast('خطا: ' + e, 'error');
            }
        }
        
        async function generateSubscription() {
            const host = document.getElementById('sub-host').value;
            if (!host) {
                showToast('Cloudflare Host را وارد کنید', 'error');
                return;
            }
            try {
                const res = await fetch(`/api/subscription?host=${host}`);
                const data = await res.json();
                if (data.subscription) {
                    const box = document.getElementById('subscription-result');
                    box.textContent = data.subscription;
                    box.style.display = 'block';
                    showToast('سابسکرایبشن ساخته شد ✅');
                } else {
                    showToast(data.error || 'خطا', 'error');
                }
            } catch(e) {
                showToast('خطا: ' + e, 'error');
            }
        }
        
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
    
    server = http.server.HTTPServer(('0.0.0.0', PORT), VLESSHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 متوقف شد")
        server.server_close()

if __name__ == '__main__':
    main()
