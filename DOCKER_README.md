# Zepp Life 刷步数 - Docker 多用户部署指南

## 功能特性

- **多用户独立**：每人注册自己的账号，配置互不影响
- **登录认证**：注册/登录系统，密码 SHA256 加密存储
- **独立配置**：每个用户有自己的 Zepp Life 账号、密码、步数范围
- **手动刷步**：点击按钮立即执行一次，不会自动重复
- **API 接口**：支持外部调用 `/api/run`

## 部署步骤

### 1. 上传代码到服务器

将整个 `mimotion` 目录上传到服务器，例如：
```bash
scp -r mimotion root@你的服务器IP:/opt/
```

### 2. 服务器上构建并启动

```bash
cd /opt/mimotion
docker-compose up -d --build
```

### 3. 访问 Web 界面

```
http://服务器IP:5000
```

### 4. 注册账号并配置

1. 点击 **注册**，设置用户名和密码
2. 登录后填写：
   - **Zepp Life 账号**：手机号或邮箱（多账号用 `#` 分隔）
   - **Zepp Life 密码**：对应密码（多账号用 `#` 分隔）
   - **最小/最大步数**：建议 15000 ~ 25000
3. 点击 **保存配置**
4. 点击 **立即刷步** 执行一次

> 每个人注册自己的账号，配置完全独立，互不干扰！

## 外网安全访问（推荐）

直接暴露 5000 端口不安全，建议用 Nginx 反向代理 + HTTPS：

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 数据持久化

用户数据和配置保存在以下位置，已挂载到宿主机：
- `user_configs/` — 每个用户的 Zepp Life 配置
- `users.json` — 注册用户列表（密码 SHA256 加密）

升级或重建容器时数据不会丢失。

## 查看日志

```bash
docker logs -f mimotion
```

## 停止服务

```bash
cd /opt/mimotion
docker-compose down
```
