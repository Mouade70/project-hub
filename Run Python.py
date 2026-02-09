from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import hashlib
import socket
import requests
import ssl
import os

app = Flask(__name__)
CORS(app)

HTML_CONTENT = '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MouadeLab Mobile</title>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.1.1/crypto-js.min.js"></script>
    <style>
        :root {
            --primary: #6366f1;
            --secondary: #ec4899;
            --bg-dark: #0f172a;
            --bg-card: #1e293b;
            --text: #f8fafc;
            --success: #10b981;
            --danger: #ef4444;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Tajawal', sans-serif;
        }
        
        body {
            background: var(--bg-dark);
            color: var(--text);
            padding: 1rem;
            min-height: 100vh;
        }
        
        .header {
            text-align: center;
            padding: 2rem 1rem;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            border-radius: 20px;
            margin-bottom: 1.5rem;
        }
        
        .header h1 {
            font-size: 1.8rem;
            margin-bottom: 0.5rem;
        }
        
        .tools-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .tool-btn {
            background: var(--bg-card);
            border: 2px solid transparent;
            border-radius: 16px;
            padding: 1.5rem 1rem;
            color: var(--text);
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .tool-btn:active {
            transform: scale(0.95);
        }
        
        .tool-btn.active {
            border-color: var(--primary);
            background: rgba(99, 102, 241, 0.2);
        }
        
        .tool-btn i {
            font-size: 2rem;
            margin-bottom: 0.5rem;
            display: block;
            color: var(--primary);
        }
        
        .tool-section {
            display: none;
            background: var(--bg-card);
            padding: 1.5rem;
            border-radius: 20px;
            margin-bottom: 1rem;
        }
        
        .tool-section.active {
            display: block;
            animation: fadeIn 0.3s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        h2 {
            margin-bottom: 1rem;
            color: var(--primary);
        }
        
        .input-group {
            margin-bottom: 1rem;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
        }
        
        input, select, textarea {
            width: 100%;
            padding: 1rem;
            border-radius: 12px;
            border: 2px solid #334155;
            background: #0f172a;
            color: var(--text);
            font-size: 1rem;
        }
        
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: var(--primary);
        }
        
        .btn {
            width: 100%;
            padding: 1rem;
            border-radius: 12px;
            border: none;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            font-size: 1rem;
            font-weight: 700;
            cursor: pointer;
            margin-top: 1rem;
        }
        
        .btn:active {
            transform: scale(0.98);
        }
        
        .result-box {
            margin-top: 1rem;
            padding: 1rem;
            background: rgba(99, 102, 241, 0.1);
            border-radius: 12px;
            border: 2px dashed var(--primary);
            word-break: break-all;
            font-family: monospace;
            font-size: 0.9rem;
        }
        
        .options {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin-bottom: 1rem;
        }
        
        .option {
            padding: 0.5rem 1rem;
            border-radius: 20px;
            background: #334155;
            font-size: 0.8rem;
            cursor: pointer;
        }
        
        .option.active {
            background: var(--primary);
        }
        
        .back-btn {
            background: transparent;
            border: 2px solid var(--primary);
            margin-bottom: 1rem;
        }
        
        .toast {
            position: fixed;
            bottom: 2rem;
            left: 50%;
            transform: translateX(-50%) translateY(100px);
            background: var(--success);
            color: white;
            padding: 1rem 2rem;
            border-radius: 50px;
            opacity: 0;
            transition: all 0.3s;
            z-index: 1000;
        }
        
        .toast.show {
            transform: translateX(-50%) translateY(0);
            opacity: 1;
        }
        
        .strength-bar {
            height: 4px;
            background: #334155;
            border-radius: 2px;
            margin-top: 0.5rem;
            overflow: hidden;
        }
        
        .strength-fill {
            height: 100%;
            width: 0%;
            transition: all 0.3s;
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <div class="header">
        <h1><i class="fas fa-shield-alt"></i> MouadeLab</h1>
        <p>مختبر الأدوات الأمنية</p>
    </div>
    
    <div id="main-menu">
        <div class="tools-grid">
            <div class="tool-btn" onclick="showTool('password')">
                <i class="fas fa-key"></i>
                <div>كلمة مرور</div>
            </div>
            <div class="tool-btn" onclick="showTool('ip')">
                <i class="fas fa-network-wired"></i>
                <div>معلومات IP</div>
            </div>
            <div class="tool-btn" onclick="showTool('port')">
                <i class="fas fa-plug"></i>
                <div>فحص منفذ</div>
            </div>
            <div class="tool-btn" onclick="showTool('url')">
                <i class="fas fa-link"></i>
                <div>فحص رابط</div>
            </div>
            <div class="tool-btn" onclick="showTool('hash')">
                <i class="fas fa-fingerprint"></i>
                <div>Hash</div>
            </div>
            <div class="tool-btn" onclick="showTool('encode')">
                <i class="fas fa-code"></i>
                <div>ترميز</div>
            </div>
        </div>
    </div>

    <!-- Password Generator -->
    <div id="tool-password" class="tool-section">
        <button class="btn back-btn" onclick="showMenu()"><i class="fas fa-arrow-right"></i> رجوع</button>
        <h2>مولد كلمات المرور</h2>
        
        <div class="input-group">
            <label>الطول: <span id="pass-len-val">16</span></label>
            <input type="range" id="pass-len" min="8" max="32" value="16" oninput="updatePassLen(this.value)">
        </div>
        
        <div class="options">
            <div class="option active" onclick="toggleOpt(this, 'upper')">ABC</div>
            <div class="option active" onclick="toggleOpt(this, 'lower')">abc</div>
            <div class="option active" onclick="toggleOpt(this, 'num')">123</div>
            <div class="option active" onclick="toggleOpt(this, 'sym')">!@#</div>
        </div>
        
        <button class="btn" onclick="genPassword()">توليد</button>
        
        <div class="result-box" id="pass-result" style="display:none;">
            <div id="pass-output"></div>
            <div class="strength-bar"><div class="strength-fill" id="strength-bar"></div></div>
            <button class="btn" onclick="copyText('pass-output')" style="margin-top:0.5rem;">نسخ</button>
        </div>
    </div>

    <!-- IP Info -->
    <div id="tool-ip" class="tool-section">
        <button class="btn back-btn" onclick="showMenu()"><i class="fas fa-arrow-right"></i> رجوع</button>
        <h2>معلومات IP</h2>
        
        <div class="input-group">
            <label>عنوان IP (اتركه فارغاً للحصول على IP الخاص بك)</label>
            <input type="text" id="ip-input" placeholder="8.8.8.8">
        </div>
        
        <button class="btn" onclick="getIP()">بحث</button>
        
        <div class="result-box" id="ip-result" style="display:none;"></div>
    </div>

    <!-- Port Scanner -->
    <div id="tool-port" class="tool-section">
        <button class="btn back-btn" onclick="showMenu()"><i class="fas fa-arrow-right"></i> رجوع</button>
        <h2>فحص المنفذ</h2>
        
        <div class="input-group">
            <label>الهدف (IP أو نطاق)</label>
            <input type="text" id="port-target" placeholder="example.com">
        </div>
        
        <div class="input-group">
            <label>رقم المنفذ</label>
            <input type="number" id="port-num" value="80" min="1" max="65535">
        </div>
        
        <button class="btn" onclick="scanPort()">فحص</button>
        
        <div class="result-box" id="port-result" style="display:none;"></div>
    </div>

    <!-- URL Checker -->
    <div id="tool-url" class="tool-section">
        <button class="btn back-btn" onclick="showMenu()"><i class="fas fa-arrow-right"></i> رجوع</button>
        <h2>فحص الرابط</h2>
        
        <div class="input-group">
            <label>الرابط</label>
            <input type="url" id="url-input" placeholder="https://google.com">
        </div>
        
        <button class="btn" onclick="checkURL()">فحص</button>
        
        <div class="result-box" id="url-result" style="display:none;"></div>
    </div>

    <!-- Hash Generator -->
    <div id="tool-hash" class="tool-section">
        <button class="btn back-btn" onclick="showMenu()"><i class="fas fa-arrow-right"></i> رجوع</button>
        <h2>مولد Hash</h2>
        
        <div class="input-group">
            <label>النص</label>
            <textarea id="hash-input" rows="3"></textarea>
        </div>
        
        <div class="input-group">
            <label>النوع</label>
            <select id="hash-type">
                <option value="MD5">MD5</option>
                <option value="SHA1">SHA1</option>
                <option value="SHA256" selected>SHA256</option>
                <option value="SHA512">SHA512</option>
            </select>
        </div>
        
        <button class="btn" onclick="genHash()">توليد</button>
        
        <div class="result-box" id="hash-result" style="display:none;">
            <div id="hash-output"></div>
            <button class="btn" onclick="copyText('hash-output')" style="margin-top:0.5rem;">نسخ</button>
        </div>
    </div>

    <!-- Encoder -->
    <div id="tool-encode" class="tool-section">
        <button class="btn back-btn" onclick="showMenu()"><i class="fas fa-arrow-right"></i> رجوع</button>
        <h2>أدوات الترميز</h2>
        
        <div class="input-group">
            <label>النص</label>
            <textarea id="enc-input" rows="3"></textarea>
        </div>
        
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.5rem;">
            <button class="btn" onclick="encode('base64')" style="font-size:0.8rem;">Base64 تشفير</button>
            <button class="btn" onclick="decode('base64')" style="font-size:0.8rem;">Base64 فك</button>
            <button class="btn" onclick="encode('url')" style="font-size:0.8rem;">URL تشفير</button>
            <button class="btn" onclick="decode('url')" style="font-size:0.8rem;">URL فك</button>
        </div>
        
        <div class="result-box" id="enc-result" style="display:none; margin-top:1rem;"></div>
    </div>

    <div class="toast" id="toast"></div>

    <script>
        let passOpts = {upper:true, lower:true, num:true, sym:true};
        
        function showTool(tool) {
            document.getElementById('main-menu').style.display = 'none';
            document.querySelectorAll('.tool-section').forEach(s => s.classList.remove('active'));
            document.getElementById('tool-' + tool).classList.add('active');
        }
        
        function showMenu() {
            document.getElementById('main-menu').style.display = 'block';
            document.querySelectorAll('.tool-section').forEach(s => s.classList.remove('active'));
        }
        
        function showToast(msg) {
            const t = document.getElementById('toast');
            t.textContent = msg;
            t.classList.add('show');
            setTimeout(() => t.classList.remove('show'), 2000);
        }
        
        function updatePassLen(v) {
            document.getElementById('pass-len-val').textContent = v;
        }
        
        function toggleOpt(el, type) {
            passOpts[type] = !passOpts[type];
            el.classList.toggle('active');
        }
        
        function genPassword() {
            const len = parseInt(document.getElementById('pass-len').value);
            const chars = {
                upper: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                lower: 'abcdefghijklmnopqrstuvwxyz',
                num: '0123456789',
                sym: '!@#$%^&*'
            };
            
            let charset = '';
            if(passOpts.upper) charset += chars.upper;
            if(passOpts.lower) charset += chars.lower;
            if(passOpts.num) charset += chars.num;
            if(passOpts.sym) charset += chars.sym;
            
            if(!charset) {
                showToast('اختر خياراً واحداً على الأقل');
                return;
            }
            
            let pass = '';
            const arr = new Uint32Array(len);
            crypto.getRandomValues(arr);
            for(let i=0; i<len; i++) pass += charset[arr[i] % charset.length];
            
            document.getElementById('pass-output').textContent = pass;
            document.getElementById('pass-result').style.display = 'block';
            
            // Strength
            let strength = 0;
            if(passOpts.upper) strength++;
            if(passOpts.lower) strength++;
            if(passOpts.num) strength++;
            if(passOpts.sym) strength++;
            if(len > 12) strength++;
            
            const colors = ['#ef4444', '#f59e0b', '#eab308', '#10b981', '#059669'];
            document.getElementById('strength-bar').style.width = (strength/5*100) + '%';
            document.getElementById('strength-bar').style.background = colors[strength-1] || colors[0];
        }
        
        async function getIP() {
            const ip = document.getElementById('ip-input').value.trim();
            const url = ip ? `https://ipapi.co/${ip}/json/` : 'https://ipapi.co/json/';
            
            try {
                const r = await fetch(url);
                const d = await r.json();
                
                if(d.error) throw new Error(d.reason);
                
                document.getElementById('ip-result').innerHTML = `
                    <div><strong>IP:</strong> ${d.ip}</div>
                    <div><strong>الدولة:</strong> ${d.country_name}</div>
                    <div><strong>المدينة:</strong> ${d.city}</div>
                    <div><strong>المنطقة:</strong> ${d.region}</div>
                    <div><strong>ISP:</strong> ${d.org || 'Unknown'}</div>
                `;
                document.getElementById('ip-result').style.display = 'block';
            } catch(e) {
                showToast('خطأ: ' + e.message);
            }
        }
        
        async function scanPort() {
            const target = document.getElementById('port-target').value;
            const port = document.getElementById('port-num').value;
            
            if(!target) {
                showToast('أدخل الهدف');
                return;
            }
            
            // Simulation for mobile (real scanning needs backend)
            const commonPorts = {
                21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP',
                53: 'DNS', 80: 'HTTP', 443: 'HTTPS', 3306: 'MySQL'
            };
            
            const isOpen = Math.random() > 0.5;
            const service = commonPorts[port] || 'Unknown';
            
            document.getElementById('port-result').innerHTML = `
                <div style="color:${isOpen?'var(--success)':'var(--danger)'}; font-weight:bold; font-size:1.2rem;">
                    <i class="fas fa-${isOpen?'check':'times'}-circle"></i>
                    المنفذ ${port} ${isOpen?'مفتوح':'مغلق'}
                </div>
                <div>الخدمة: ${service}</div>
                <div style="font-size:0.8rem; opacity:0.7; margin-top:0.5rem;">
                    ملاحظة: هذا فحص توضيحي. للفحص الحقيقي استخدم النسخة الكاملة.
                </div>
            `;
            document.getElementById('port-result').style.display = 'block';
        }
        
        async function checkURL() {
            let url = document.getElementById('url-input').value.trim();
            if(!url) {
                showToast('أدخل الرابط');
                return;
            }
            if(!url.startsWith('http')) url = 'https://' + url;
            
            const start = performance.now();
            
            try {
                // Using fetch with no-cors for basic check
                await fetch(url, {mode: 'no-cors', method: 'HEAD'});
                const time = Math.round(performance.now() - start);
                
                document.getElementById('url-result').innerHTML = `
                    <div style="color:var(--success); font-weight:bold;">
                        <i class="fas fa-check-circle"></i> الرابط يعمل
                    </div>
                    <div>زمن الاستجابة: ${time}ms</div>
                    <div>البروتوكول: ${url.startsWith('https')?'HTTPS':'HTTP'}</div>
                `;
            } catch(e) {
                document.getElementById('url-result').innerHTML = `
                    <div style="color:var(--danger);">
                        <i class="fas fa-times-circle"></i> لم يتم الوصول للرابط
                    </div>
                    <div style="font-size:0.8rem;">قد يكون الرابط محمياً أو غير صالح</div>
                `;
            }
            document.getElementById('url-result').style.display = 'block';
        }
        
        function genHash() {
            const text = document.getElementById('hash-input').value;
            const type = document.getElementById('hash-type').value;
            
            if(!text) {
                showToast('أدخل النص');
                return;
            }
            
            let hash;
            switch(type) {
                case 'MD5': hash = CryptoJS.MD5(text); break;
                case 'SHA1': hash = CryptoJS.SHA1(text); break;
                case 'SHA256': hash = CryptoJS.SHA256(text); break;
                case 'SHA512': hash = CryptoJS.SHA512(text); break;
            }
            
            document.getElementById('hash-output').textContent = hash.toString();
            document.getElementById('hash-result').style.display = 'block';
        }
        
        function encode(type) {
            const text = document.getElementById('enc-input').value;
            if(!text) return;
            
            let result;
            if(type === 'base64') {
                result = btoa(unescape(encodeURIComponent(text)));
            } else {
                result = encodeURIComponent(text);
            }
            
            document.getElementById('enc-result').textContent = result;
            document.getElementById('enc-result').style.display = 'block';
        }
        
        function decode(type) {
            const text = document.getElementById('enc-input').value;
            if(!text) return;
            
            try {
                let result;
                if(type === 'base64') {
                    result = decodeURIComponent(escape(atob(text)));
                } else {
                    result = decodeURIComponent(text);
                }
                document.getElementById('enc-result').textContent = result;
            } catch(e) {
                showToast('خطأ في فك الترميز');
            }
            document.getElementById('enc-result').style.display = 'block';
        }
        
        function copyText(id) {
            const text = document.getElementById(id).textContent;
            navigator.clipboard.writeText(text).then(() => showToast('تم النسخ!'));
        }
    </script>
</body>
</html>'''

@app.route('/')
def home():
    return HTML_CONTENT

@app.route('/api/hash', methods=['POST'])
def api_hash():
    data = request.get_json()
    text = data.get('text', '')
    algo = data.get('type', 'SHA256').upper()
    
    if algo == 'MD5':
        h = hashlib.md5(text.encode()).hexdigest()
    elif algo == 'SHA1':
        h = hashlib.sha1(text.encode()).hexdigest()
    elif algo == 'SHA256':
        h = hashlib.sha256(text.encode()).hexdigest()
    elif algo == 'SHA512':
        h = hashlib.sha512(text.encode()).hexdigest()
    else:
        return jsonify({'error': 'Unknown algorithm'}), 400
    
    return jsonify({'hash': h, 'algorithm': algo})

@app.route('/api/ip/<ip>')
def api_ip(ip):
    try:
        r = requests.get(f'https://ipapi.co/{ip}/json/', timeout=5)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/myip')
def api_myip():
    try:
        r = requests.get('https://ipapi.co/json/', timeout=5)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/port', methods=['POST'])
def api_port():
    """Scan port - limited to common ports for security"""
    data = request.get_json()
    target = data.get('target')
    port = int(data.get('port', 80))
    
    # Security: only allow common ports
    allowed = [21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 3389, 8080]
    if port not in allowed:
        return jsonify({'error': 'Port not allowed'}), 403
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((target, port))
        sock.close()
        
        try:
            service = socket.getservbyport(port)
        except:
            service = 'unknown'
        
        return jsonify({
            'target': target,
            'port': port,
            'status': 'open' if result == 0 else 'closed',
            'service': service
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("="*50)
    print("MouadeLab Mobile Server")
    print("="*50)
    print("افتح المتصفح على:")
    print("http://localhost:5000")
    print("="*50)
    # Run on all interfaces so you can access from phone browser
    app.run(host='0.0.0.0', port=5000, debug=False)
