import json
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

if not os.path.exists(CONFIG_FILE):
    print(f"错误：找不到配置文件 {CONFIG_FILE}")
    print("请将 config.json 中的账号密码填写正确后重新运行")
    sys.exit(1)

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    config = json.load(f)

user = config.get("USER", "")
pwd = config.get("PWD", "")
if not user or not pwd or pwd == "your_password":
    print("错误：请先在 config.json 中填写你的 Zepp Life（小米运动）账号和密码！")
    print(f"  当前 USER = {user}")
    print(f"  当前 PWD = {'***' if pwd != 'your_password' else 'your_password（未修改）'}")
    sys.exit(1)

min_step = config.get("MIN_STEP", "18000")
max_step = config.get("MAX_STEP", "25000")
print(f"Zepp Life 刷步数启动")
print(f"  账号: {user}")
print(f"  步数范围: {min_step} ~ {max_step}")
print()

env = os.environ.copy()
env["CONFIG"] = json.dumps(config)

result = subprocess.run([sys.executable, "main.py"], env=env, cwd=os.path.dirname(os.path.abspath(__file__)))

if result.returncode != 0:
    print(f"程序异常退出，返回码: {result.returncode}")
    sys.exit(result.returncode)
else:
    print("执行完毕")
