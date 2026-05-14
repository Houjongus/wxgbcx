import json
import os
import subprocess
import sys
import hashlib
import secrets
from functools import wraps
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CONFIG_DIR = os.path.join(DATA_DIR, "user_configs")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)


def get_user_config_path(username):
    safe_name = hashlib.md5(username.encode()).hexdigest()
    return os.path.join(CONFIG_DIR, f"{safe_name}.json")


def load_user_config(username):
    path = get_user_config_path(username)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "USER": "",
        "PWD": "",
        "MIN_STEP": "15000",
        "MAX_STEP": "20000"
    }


def save_user_config(username, config):
    path = get_user_config_path(username)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated


def run_mimotion(config):
    env = os.environ.copy()
    env["CONFIG"] = json.dumps(config)
    result = subprocess.run(
        [sys.executable, os.path.join(BASE_DIR, "main.py")],
        env=env,
        cwd=BASE_DIR,
        capture_output=True,
        text=True
    )
    return result.stdout + result.stderr


HTML_LOGIN = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zepp Life 刷步数 - 登录</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .login-box {
            background: white;
            border-radius: 20px;
            padding: 40px;
            width: 100%;
            max-width: 400px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 8px;
            font-size: 24px;
        }
        .subtitle {
            text-align: center;
            color: #888;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #555;
            font-size: 14px;
        }
        input {
            width: 100%;
            padding: 14px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            font-size: 15px;
            transition: border-color 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            width: 100%;
            padding: 16px;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-secondary {
            background: #f0f0f0;
            color: #555;
            margin-top: 12px;
        }
        .status {
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-size: 14px;
            text-align: center;
        }
        .status.error {
            background: #f8d7da;
            color: #721c24;
        }
        .status.success {
            background: #d4edda;
            color: #155724;
        }
        .tabs {
            display: flex;
            margin-bottom: 24px;
            background: #f5f5f5;
            border-radius: 12px;
            padding: 4px;
        }
        .tab {
            flex: 1;
            text-align: center;
            padding: 10px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            color: #888;
            transition: all 0.3s;
        }
        .tab.active {
            background: white;
            color: #667eea;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>🏃 Zepp Life 刷步数</h1>
        <p class="subtitle">每人独立配置，互不干扰</p>

        {% if message %}
        <div class="status {{ message_type }}">{{ message }}</div>
        {% endif %}

        <div class="tabs">
            <div class="tab active" onclick="showTab('login')">登录</div>
            <div class="tab" onclick="showTab('register')">注册</div>
        </div>

        <form id="login-form" method="POST" action="/login">
            <div class="form-group">
                <label>用户名</label>
                <input type="text" name="username" placeholder="输入用户名" required>
            </div>
            <div class="form-group">
                <label>密码</label>
                <input type="password" name="password" placeholder="输入密码" required>
            </div>
            <button type="submit" class="btn btn-primary">登录</button>
        </form>

        <form id="register-form" method="POST" action="/register" style="display:none;">
            <div class="form-group">
                <label>用户名</label>
                <input type="text" name="username" placeholder="设置用户名" required>
            </div>
            <div class="form-group">
                <label>密码</label>
                <input type="password" name="password" placeholder="设置密码" required>
            </div>
            <button type="submit" class="btn btn-primary">注册</button>
        </form>
    </div>

    <script>
        function showTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            if (tab === 'login') {
                document.getElementById('login-form').style.display = 'block';
                document.getElementById('register-form').style.display = 'none';
            } else {
                document.getElementById('login-form').style.display = 'none';
                document.getElementById('register-form').style.display = 'block';
            }
        }
    </script>
</body>
</html>
"""

HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zepp Life 刷步数 - 控制台</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
        }
        h1 {
            color: white;
            font-size: 24px;
        }
        .user-info {
            color: rgba(255,255,255,0.9);
            font-size: 14px;
        }
        .logout-btn {
            background: rgba(255,255,255,0.2);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 13px;
            margin-left: 12px;
        }
        .card {
            background: white;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        .card h2 {
            font-size: 18px;
            margin-bottom: 16px;
            color: #333;
        }
        .form-group {
            margin-bottom: 16px;
        }
        label {
            display: block;
            margin-bottom: 6px;
            font-weight: 600;
            color: #555;
            font-size: 14px;
        }
        input[type="text"], input[type="password"], input[type="number"] {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 15px;
            transition: border-color 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        .hint {
            font-size: 12px;
            color: #888;
            margin-top: 4px;
        }
        .btn {
            width: 100%;
            padding: 14px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-success {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            margin-top: 10px;
        }
        .status {
            padding: 16px;
            border-radius: 10px;
            margin-bottom: 16px;
            font-size: 14px;
        }
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .log-box {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 16px;
            border-radius: 10px;
            font-family: 'Consolas', monospace;
            font-size: 13px;
            white-space: pre-wrap;
            max-height: 400px;
            overflow-y: auto;
            line-height: 1.6;
        }
        .log-box .success { color: #4ec9b0; }
        .log-box .error { color: #f44747; }
        .two-col {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏃 Zepp Life 刷步数</h1>
            <div>
                <span class="user-info">用户: {{ username }}</span>
                <a href="/logout"><button class="logout-btn">退出</button></a>
            </div>
        </div>

        {% if message %}
        <div class="status {{ message_type }}">
            {{ message }}
        </div>
        {% endif %}

        <div class="card">
            <h2>⚙️ 我的账号配置</h2>
            <form method="POST" action="/save">
                <div class="form-group">
                    <label>Zepp Life 账号（多账号用 # 分隔）</label>
                    <input type="text" name="user" value="{{ config.USER }}" placeholder="13800138000#13800138001">
                    <div class="hint">支持手机号或邮箱，多个账号用 # 分隔</div>
                </div>
                <div class="form-group">
                    <label>Zepp Life 密码（多账号用 # 分隔）</label>
                    <input type="password" name="pwd" value="{{ config.PWD }}" placeholder="password1#password2">
                    <div class="hint">账号和密码数量必须一一对应</div>
                </div>
                <div class="two-col">
                    <div class="form-group">
                        <label>最小步数</label>
                        <input type="number" name="min_step" value="{{ config.MIN_STEP }}" placeholder="15000">
                    </div>
                    <div class="form-group">
                        <label>最大步数</label>
                        <input type="number" name="max_step" value="{{ config.MAX_STEP }}" placeholder="20000">
                    </div>
                </div>
                <div class="hint">步数会在设定范围内随机，建议 15000~25000</div>
                <button type="submit" class="btn btn-primary">💾 保存配置</button>
            </form>
        </div>

        <div class="card">
            <h2>🚀 手动执行</h2>
            <form method="POST" action="/run">
                <button type="submit" class="btn btn-success">▶️ 立即刷步</button>
            </form>
        </div>

        {% if log %}
        <div class="card">
            <h2>📋 执行日志</h2>
            <div class="log-box">{{ log | safe }}</div>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""


@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login_page"))


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "GET":
        return render_template_string(HTML_LOGIN)

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    users = load_users()
    if username not in users:
        return render_template_string(HTML_LOGIN, message="用户名不存在", message_type="error")

    if users[username] != hash_password(password):
        return render_template_string(HTML_LOGIN, message="密码错误", message_type="error")

    session["username"] = username
    return redirect(url_for("dashboard"))


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if not username or not password:
        return render_template_string(HTML_LOGIN, message="用户名和密码不能为空", message_type="error")

    users = load_users()
    if username in users:
        return render_template_string(HTML_LOGIN, message="用户名已存在", message_type="error")

    users[username] = hash_password(password)
    save_users(users)

    # 创建默认配置
    save_user_config(username, {
        "USER": "",
        "PWD": "",
        "MIN_STEP": "15000",
        "MAX_STEP": "20000"
    })

    session["username"] = username
    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login_page"))


@app.route("/dashboard")
@login_required
def dashboard():
    username = session["username"]
    config = load_user_config(username)
    return render_template_string(
        HTML_DASHBOARD,
        username=username,
        config=config,
        message=request.args.get("msg"),
        message_type=request.args.get("type"),
        log=request.args.get("log")
    )


@app.route("/save", methods=["POST"])
@login_required
def save():
    username = session["username"]
    config = {
        "USER": request.form.get("user", "").strip(),
        "PWD": request.form.get("pwd", "").strip(),
        "MIN_STEP": request.form.get("min_step", "15000").strip(),
        "MAX_STEP": request.form.get("max_step", "20000").strip()
    }
    save_user_config(username, config)
    return render_template_string(
        HTML_DASHBOARD,
        username=username,
        config=config,
        message="✅ 配置已保存",
        message_type="success",
        log=None
    )


@app.route("/run", methods=["POST"])
@login_required
def run_now():
    username = session["username"]
    config = load_user_config(username)
    if not config.get("USER") or not config.get("PWD"):
        return render_template_string(
            HTML_DASHBOARD,
            username=username,
            config=config,
            message="❌ 请先填写 Zepp Life 账号密码",
            message_type="error",
            log=None
        )
    log = run_mimotion(config)
    log_html = log.replace("\n", "<br>")
    log_html = log_html.replace("[success]", '<span class="success">[success]</span>')
    log_html = log_html.replace("失败", '<span class="error">失败</span>')
    log_html = log_html.replace("success", '<span class="success">success</span>')
    return render_template_string(
        HTML_DASHBOARD,
        username=username,
        config=config,
        message="✅ 执行完成",
        message_type="success",
        log=log_html
    )


@app.route("/api/run", methods=["POST"])
@login_required
def api_run():
    username = session["username"]
    config = load_user_config(username)
    if not config.get("USER") or not config.get("PWD"):
        return jsonify({"success": False, "error": "未配置账号密码"}), 400
    log = run_mimotion(config)
    return jsonify({"success": True, "log": log})


# ==============================================
# 👇 只有这里被我改了！适配 Railway 端口！
# ==============================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
