from flask import Flask
app = Flask(__name__)

# 网页根路径，访问时会显示的内容
@app.route("/")
def hello():
    return "✅ 你的程序部署成功啦！端口 5000 已正常运行"

# 关键配置：必须绑定 0.0.0.0 和 5000 端口
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
