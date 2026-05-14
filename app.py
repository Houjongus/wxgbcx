from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def hello():
    return "✅ 示例程序跑通了！Railway 配置没问题！"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # 关键：读取环境变量
    app.run(host="0.0.0.0", port=port)        # host必须是0.0.0.0
