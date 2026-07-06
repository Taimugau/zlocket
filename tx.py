# palofsc - Hệ thống game Tài Xỉu 3D có đặt cược và tạo tài khoản (chạy hosting với Flask)
# Yêu cầu: Python 3.8+, cài Flask: pip install flask

from flask import Flask, render_template_string, request, jsonify, session
import random
import json
import os
import hashlib
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'SUNWIN_SECRET_KEY_2026_BYPASS'

# File lưu dữ liệu người dùng
USER_DB = 'users.json'
BET_HISTORY = 'bet_history.json'

# Khởi tạo file dữ liệu nếu chưa có
def init_db():
    if not os.path.exists(USER_DB):
        with open(USER_DB, 'w', encoding='utf-8') as f:
            json.dump({}, f)
    if not os.path.exists(BET_HISTORY):
        with open(BET_HISTORY, 'w', encoding='utf-8') as f:
            json.dump([], f)

init_db()

# Hàm băm mật khẩu
def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# Đọc/ghi user
def load_users():
    with open(USER_DB, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_users(users):
    with open(USER_DB, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# Đọc/ghi lịch sử
def load_history():
    with open(BET_HISTORY, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_history(hist):
    with open(BET_HISTORY, 'w', encoding='utf-8') as f:
        json.dump(hist, f, ensure_ascii=False, indent=2)

# Trang HTML nhúng (giao diện Sun Win style)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sun Win - Tài Xỉu 3D</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; font-family:'Segoe UI',Arial,sans-serif; }
        body { background: #0b0e14; color: #e0e6f0; display: flex; justify-content: center; padding: 20px; }
        #app { max-width: 650px; width: 100%; background: #141a24; border-radius: 28px; padding: 24px; box-shadow: 0 8px 40px rgba(0,0,0,0.8); border: 1px solid #2a3344; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #2a3344; padding-bottom: 16px; margin-bottom: 18px; }
        .logo { font-size: 28px; font-weight: 900; background: linear-gradient(135deg,#f7b731,#f5a623); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
        .user-info { background: #1e2634; padding: 8px 18px; border-radius: 40px; font-size: 14px; }
        .user-info span { color: #f5a623; font-weight: bold; }
        .balance-box { background: #0f141e; border-radius: 20px; padding: 20px; text-align: center; margin-bottom: 18px; border: 1px solid #2a3344; }
        .balance-box .label { font-size: 14px; color: #8899bb; }
        .balance-box .amount { font-size: 42px; font-weight: 700; color: #7bed9f; letter-spacing: 2px; }
        .dice-area { background: #0b1018; border-radius: 24px; padding: 20px 10px; margin-bottom: 18px; border: 1px solid #1f2a3a; }
        canvas { display: block; margin: 0 auto; width: 100%; max-width: 400px; height: auto; background: #0b1018; border-radius: 16px; }
        .bet-panel { background: #101823; border-radius: 20px; padding: 20px; margin: 16px 0; border: 1px solid #1f2a3a; }
        .bet-row { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
        .bet-row label { font-size: 16px; color: #aabbdd; min-width: 60px; }
        .bet-row input { flex: 1; padding: 12px 16px; border-radius: 40px; border: 1px solid #2a3344; background: #0b1018; color: #fff; font-size: 18px; min-width: 100px; }
        .bet-row input:focus { outline: 2px solid #f5a623; border-color:transparent; }
        .bet-buttons { display: flex; gap: 16px; margin-top: 16px; }
        .btn { flex: 1; padding: 14px 0; border: none; border-radius: 60px; font-size: 20px; font-weight: 700; cursor: pointer; transition: 0.2s; }
        .btn-tai { background: #2ecc71; color: #0b1018; }
        .btn-tai:hover { background: #27ae60; transform: scale(1.02); }
        .btn-xiu { background: #e74c3c; color: #fff; }
        .btn-xiu:hover { background: #c0392b; transform: scale(1.02); }
        .btn:disabled { opacity:0.4; pointer-events:none; }
        .result-box { background: #0f141e; border-radius: 16px; padding: 16px; text-align: center; margin-top: 12px; border-left: 4px solid #f5a623; }
        .result-box .main { font-size: 26px; font-weight: 600; }
        .result-box .sub { font-size: 16px; color: #8899bb; margin-top: 6px; }
        .history { margin-top: 20px; max-height: 180px; overflow-y: auto; background: #0b1018; border-radius: 16px; padding: 12px; border: 1px solid #1a2230; }
        .history-item { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #1a2230; font-size: 14px; }
        .history-item .win { color: #2ecc71; }
        .history-item .lose { color: #e74c3c; }
        .auth-section { display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
        .auth-section input { flex:1; padding: 10px 16px; border-radius: 40px; border: 1px solid #2a3344; background: #0b1018; color:#fff; min-width:120px; }
        .auth-section button { padding: 10px 24px; border-radius: 40px; border:none; background: #f5a623; color:#0b1018; font-weight:700; cursor:pointer; }
        .auth-section button:hover { background: #e0951a; }
        .logout-btn { background: #555; color:#fff; margin-left:8px; }
        .logout-btn:hover { background:#777; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: #0b1018; }
        ::-webkit-scrollbar-thumb { background: #2a3344; border-radius: 8px; }
    </style>
</head>
<body>
<div id="app">
    <div class="header">
        <div class="logo">🎲 SUN WIN</div>
        <div class="user-info" id="userDisplay">👤 <span id="usernameDisplay">Chưa đăng nhập</span></div>
    </div>

    <!-- Auth -->
    <div class="auth-section" id="authSection">
        <input type="text" id="regUser" placeholder="Tên đăng nhập">
        <input type="password" id="regPass" placeholder="Mật khẩu">
        <button onclick="register()">Đăng ký</button>
        <button onclick="login()" style="background:#3498db;">Đăng nhập</button>
        <button onclick="logout()" class="logout-btn">Thoát</button>
    </div>

    <!-- Balance -->
    <div class="balance-box">
        <div class="label">💰 Số dư</div>
        <div class="amount" id="balanceDisplay">0</div>
    </div>

    <!-- Dice 3D Canvas -->
    <div class="dice-area">
        <canvas id="diceCanvas" width="400" height="320"></canvas>
    </div>

    <!-- Bet panel -->
    <div class="bet-panel">
        <div class="bet-row">
            <label>Tiền cược</label>
            <input type="number" id="betAmount" value="1000" min="100" step="100">
        </div>
        <div class="bet-buttons">
            <button class="btn btn-tai" id="btnTai" onclick="placeBet('tai')">🔵 TÀI (1:1)</button>
            <button class="btn btn-xiu" id="btnXiu" onclick="placeBet('xiu')">🔴 XỈU (1:1)</button>
        </div>
    </div>

    <!-- Result -->
    <div class="result-box" id="resultBox">
        <div class="main" id="resultMain">⚀ ⚁ ⚂</div>
        <div class="sub" id="resultSub">Chọn cửa để bắt đầu</div>
    </div>

    <!-- History -->
    <div class="history" id="historyBox">
        <div style="color:#8899bb; text-align:center; padding:8px;">Lịch sử giao dịch</div>
    </div>
</div>

<script>
// ---------- MÀN HÌNH CHÍNH (kết nối API Flask) ----------
const canvas = document.getElementById('diceCanvas');
const ctx = canvas.getContext('2d');
let currentUser = null;
let balance = 0;
let diceValues = [1,1,1];
let isRolling = false;

// Hiển thị user
function updateUI() {
    document.getElementById('usernameDisplay').innerText = currentUser || 'Chưa đăng nhập';
    document.getElementById('balanceDisplay').innerText = balance.toLocaleString();
    // Enable/disable bet buttons
    const taiBtn = document.getElementById('btnTai');
    const xiuBtn = document.getElementById('btnXiu');
    if (currentUser && !isRolling) {
        taiBtn.disabled = false;
        xiuBtn.disabled = false;
    } else {
        taiBtn.disabled = true;
        xiuBtn.disabled = true;
    }
}

// Vẽ xúc xắc 3D (giống phong cách Sun Win)
function drawDice(x, y, size, value) {
    const half = size/2;
    const depth = size*0.2;
    // Mặt trước
    ctx.fillStyle = '#1a2330';
    ctx.shadowColor = '#f5a62366';
    ctx.shadowBlur = 10;
    ctx.fillRect(x-half, y-half, size, size);
    ctx.strokeStyle = '#f5a623';
    ctx.lineWidth = 2;
    ctx.strokeRect(x-half, y-half, size, size);
    // Mặt bên
    ctx.fillStyle = '#111a24';
    ctx.beginPath();
    ctx.moveTo(x+half, y-half);
    ctx.lineTo(x+half+depth, y-half-depth);
    ctx.lineTo(x+half+depth, y+half-depth);
    ctx.lineTo(x+half, y+half);
    ctx.closePath();
    ctx.fill();
    ctx.strokeStyle = '#886633';
    ctx.stroke();
    // Mặt trên
    ctx.fillStyle = '#0d1520';
    ctx.beginPath();
    ctx.moveTo(x-half, y-half);
    ctx.lineTo(x-half+depth, y-half-depth);
    ctx.lineTo(x+half+depth, y-half-depth);
    ctx.lineTo(x+half, y-half);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    // Chấm
    ctx.shadowBlur = 6;
    ctx.fillStyle = '#f5a623';
    const dotR = size*0.07;
    const posMap = [
        [[0,0]],
        [[-1,-1],[1,1]],
        [[-1,-1],[0,0],[1,1]],
        [[-1,-1],[-1,1],[1,-1],[1,1]],
        [[-1,-1],[-1,1],[0,0],[1,-1],[1,1]],
        [[-1,-1],[-1,1],[0,-1],[0,1],[1,-1],[1,1]]
    ];
    const dots = posMap[value-1] || [[0,0]];
    dots.forEach(([r,c]) => {
        const cx = x + c*size*0.24;
        const cy = y + r*size*0.24;
        ctx.beginPath();
        ctx.arc(cx, cy, dotR, 0, 2*Math.PI);
        ctx.fill();
    });
    // Chấm bên
    ctx.fillStyle = '#886633';
    if (value>=2) {
        ctx.beginPath();
        ctx.arc(x+half+depth*0.5, y-depth*0.2, dotR*0.6, 0, 2*Math.PI);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(x+half+depth*0.5, y+depth*0.2, dotR*0.6, 0, 2*Math.PI);
        ctx.fill();
    }
}

function renderDice() {
    ctx.clearRect(0,0,400,320);
    const baseY = 170;
    const spacing = 90;
    const size = 70;
    const startX = 200 - spacing;
    for (let i=0; i<3; i++) {
        const x = startX + i*spacing + (i===1? -5:5);
        const y = baseY + (i===1 ? -8 : 8);
        drawDice(x, y, size, diceValues[i]);
    }
}

// Cập nhật kết quả
function setResult(dice, sum, betType, win) {
    const main = document.getElementById('resultMain');
    const sub = document.getElementById('resultSub');
    const diceStr = dice.join(' - ');
    if (win === true) {
        main.innerHTML = `🎉 ${diceStr}  |  Tổng: ${sum}  →  THẮNG`;
        sub.innerHTML = `Cược ${betType.toUpperCase()} +${betAmount}đ`;
        sub.style.color = '#2ecc71';
    } else if (win === false) {
        main.innerHTML = `😞 ${diceStr}  |  Tổng: ${sum}  →  THUA`;
        sub.innerHTML = `Cược ${betType.toUpperCase()} -${betAmount}đ`;
        sub.style.color = '#e74c3c';
    } else {
        main.innerHTML = `${diceStr}  |  Tổng: ${sum}`;
        sub.innerHTML = 'Chọn cửa để chơi';
        sub.style.color = '#8899bb';
    }
}

// Gọi API đặt cược
let betAmount = 1000;
function placeBet(type) {
    if (!currentUser) { alert('Vui lòng đăng nhập'); return; }
    if (isRolling) return;
    const amountInput = document.getElementById('betAmount');
    betAmount = parseInt(amountInput.value);
    if (isNaN(betAmount) || betAmount < 100) { alert('Tiền cược tối thiểu 100'); return; }
    if (betAmount > balance) { alert('Số dư không đủ'); return; }

    isRolling = true;
    document.getElementById('btnTai').disabled = true;
    document.getElementById('btnXiu').disabled = true;

    // Gửi yêu cầu đến server
    fetch('/api/bet', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            username: currentUser,
            bet_type: type,
            amount: betAmount
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            // Cập nhật kết quả
            diceValues = data.dice;
            balance = data.new_balance;
            renderDice();
            setResult(data.dice, data.sum, type, data.win);
            document.getElementById('balanceDisplay').innerText = balance.toLocaleString();
            // Thêm lịch sử
            addHistory(data.dice, data.sum, type, data.win, data.amount);
        } else {
            alert('Lỗi: ' + data.message);
        }
        isRolling = false;
        document.getElementById('btnTai').disabled = false;
        document.getElementById('btnXiu').disabled = false;
        if (!currentUser) {
            document.getElementById('btnTai').disabled = true;
            document.getElementById('btnXiu').disabled = true;
        }
    })
    .catch(err => {
        alert('Lỗi kết nối server');
        isRolling = false;
        document.getElementById('btnTai').disabled = false;
        document.getElementById('btnXiu').disabled = false;
    });
}

// Lịch sử giao diện
function addHistory(dice, sum, type, win, amount) {
    const box = document.getElementById('historyBox');
    const item = document.createElement('div');
    item.className = 'history-item';
    const txt = `${dice.join('-')}  Tổng:${sum}  ${type.toUpperCase()}  ${win?'✅':'❌'}  ${win?'+':'-'}${Math.abs(amount)}`;
    item.innerHTML = `<span>${txt}</span><span class="${win?'win':'lose'}">${win?'Thắng':'Thua'}</span>`;
    box.prepend(item);
    // Giới hạn 20 item
    while (box.children.length > 25) box.removeChild(box.lastChild);
}

// Lấy thông tin user hiện tại
function fetchUserInfo() {
    if (!currentUser) return;
    fetch(`/api/user/${currentUser}`)
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            balance = data.balance;
            document.getElementById('balanceDisplay').innerText = balance.toLocaleString();
            // Load lịch sử
            if (data.history) {
                const box = document.getElementById('historyBox');
                box.innerHTML = '<div style="color:#8899bb; text-align:center; padding:8px;">📜 Lịch sử gần nhất</div>';
                data.history.slice(-10).reverse().forEach(h => {
                    const item = document.createElement('div');
                    item.className = 'history-item';
                    const win = h.win;
                    const txt = `${h.dice.join('-')}  Tổng:${h.sum}  ${h.bet_type.toUpperCase()}  ${win?'✅':'❌'}  ${win?'+':'-'}${Math.abs(h.amount)}`;
                    item.innerHTML = `<span>${txt}</span><span class="${win?'win':'lose'}">${win?'Thắng':'Thua'}</span>`;
                    box.appendChild(item);
                });
            }
            updateUI();
        }
    });
}

// Auth functions
function register() {
    const u = document.getElementById('regUser').value.trim();
    const p = document.getElementById('regPass').value;
    if (!u || !p) { alert('Nhập đầy đủ'); return; }
    fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username:u, password:p })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        if (data.status === 'ok') {
            document.getElementById('regUser').value = '';
            document.getElementById('regPass').value = '';
        }
    });
}

function login() {
    const u = document.getElementById('regUser').value.trim();
    const p = document.getElementById('regPass').value;
    if (!u || !p) { alert('Nhập đầy đủ'); return; }
    fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username:u, password:p })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            currentUser = u;
            balance = data.balance || 0;
            updateUI();
            fetchUserInfo();
            document.getElementById('regUser').value = '';
            document.getElementById('regPass').value = '';
            alert('Đăng nhập thành công');
        } else {
            alert('Sai tên hoặc mật khẩu');
        }
    });
}

function logout() {
    currentUser = null;
    balance = 0;
    document.getElementById('usernameDisplay').innerText = 'Chưa đăng nhập';
    document.getElementById('balanceDisplay').innerText = '0';
    document.getElementById('btnTai').disabled = true;
    document.getElementById('btnXiu').disabled = true;
    document.getElementById('resultMain').innerHTML = '⚀ ⚁ ⚂';
    document.getElementById('resultSub').innerHTML = 'Đã đăng xuất';
    document.getElementById('historyBox').innerHTML = '<div style="color:#8899bb; text-align:center; padding:8px;">Lịch sử giao dịch</div>';
}

// Khởi tạo
renderDice();
document.getElementById('btnTai').disabled = true;
document.getElementById('btnXiu').disabled = true;

// Tự động kiểm tra session (nếu có)
window.onload = function() {
    // Không lưu session phía client, yêu cầu đăng nhập lại
};
</script>
</body>
</html>
'''

# ------------------- API ROUTES -------------------
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or not password:
        return jsonify({'status':'error', 'message':'Thiếu thông tin'})
    users = load_users()
    if username in users:
        return jsonify({'status':'error', 'message':'Tên đã tồn tại'})
    users[username] = {
        'password': hash_password(password),
        'balance': 100000,  # tiền thưởng khởi tạo
        'created': datetime.now().isoformat()
    }
    save_users(users)
    return jsonify({'status':'ok', 'message':'Đăng ký thành công, nhận 100,000đ'})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    users = load_users()
    if username not in users:
        return jsonify({'status':'error', 'message':'Sai tên hoặc mật khẩu'})
    if users[username]['password'] != hash_password(password):
        return jsonify({'status':'error', 'message':'Sai tên hoặc mật khẩu'})
    return jsonify({'status':'ok', 'balance': users[username]['balance']})

@app.route('/api/user/<username>')
def api_user(username):
    users = load_users()
    if username not in users:
        return jsonify({'status':'error', 'message':'User not found'})
    history = load_history()
    user_history = [h for h in history if h.get('username') == username]
    return jsonify({
        'status':'ok',
        'balance': users[username]['balance'],
        'history': user_history[-50:]
    })

@app.route('/api/bet', methods=['POST'])
def api_bet():
    data = request.json
    username = data.get('username', '').strip()
    bet_type = data.get('bet_type', '').strip().lower()
    amount = int(data.get('amount', 0))

    if bet_type not in ['tai', 'xiu']:
        return jsonify({'status':'error', 'message':'Cửa cược không hợp lệ'})
    if amount < 100:
        return jsonify({'status':'error', 'message':'Tiền cược tối thiểu 100'})

    users = load_users()
    if username not in users:
        return jsonify({'status':'error', 'message':'User không tồn tại'})
    if users[username]['balance'] < amount:
        return jsonify({'status':'error', 'message':'Số dư không đủ'})

    # Quay số
    dice = [random.randint(1,6) for _ in range(3)]
    total = sum(dice)
    # Xác định thắng thua (bỏ qua trường hợp 3 hoặc 18 -> nhà cái ăn)
    is_tai = (total >= 11 and total <= 17)
    is_xiu = (total >= 4 and total <= 10)
    win = False
    if bet_type == 'tai' and is_tai:
        win = True
    elif bet_type == 'xiu' and is_xiu:
        win = True
    # Nếu tổng 3 hoặc 18 -> thua (cửa đặc biệt không áp dụng ở đây)
    if total == 3 or total == 18:
        win = False

    # Cập nhật số dư
    if win:
        users[username]['balance'] += amount
        result_amount = amount
    else:
        users[username]['balance'] -= amount
        result_amount = -amount
    save_users(users)

    # Lưu lịch sử
    history = load_history()
    history.append({
        'username': username,
        'dice': dice,
        'sum': total,
        'bet_type': bet_type,
        'amount': result_amount,
        'win': win,
        'time': datetime.now().isoformat()
    })
    save_history(history)

    return jsonify({
        'status':'ok',
        'dice': dice,
        'sum': total,
        'win': win,
        'amount': result_amount,
        'new_balance': users[username]['balance']
    })

if __name__ == '__main__':
    # Chạy trên cổng 5000, có thể thay đổi để phù hợp hosting
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
