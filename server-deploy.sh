#!/bin/bash
# =============================================
# 智慧农业管理平台 - 服务器一键部署脚本
# 在阿里云服务器上以 root 执行:
#   chmod +x server-deploy.sh && ./server-deploy.sh
# =============================================
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

log() { echo -e "${CYAN}[$(date +'%H:%M:%S')]${NC} $1"; }
ok()  { echo -e "${GREEN}✅ $1${NC}"; }
err() { echo -e "${RED}❌ $1${NC}"; exit 1; }

INSTALL_DIR="/opt/agri-platform"
FRONTEND_DIR="${INSTALL_DIR}/frontend"
BACKEND_DIR="${INSTALL_DIR}/backend"
PORT=8001

log "============================================"
log "  智慧农业管理平台 - 部署脚本"
log "============================================"

# ---- 1. 检查系统环境 ----
log "检查系统环境..."

# 检查 Python
if ! command -v python3 &>/dev/null; then
    log "安装 Python3..."
    yum install -y python3 python3-pip 2>/dev/null || apt-get install -y python3 python3-pip
fi
ok "Python3: $(python3 --version)"

# 检查 pip
python3 -m pip --version &>/dev/null || {
    log "安装 pip..."
    python3 -m ensurepip --upgrade
}
ok "pip: $(python3 -m pip --version 2>&1 | head -1)"

# 检查 Node.js (构建前端需要)
if ! command -v node &>/dev/null; then
    log "安装 Node.js 18.x..."
    curl -fsSL https://rpm.nodesource.com/setup_18.x | bash - 2>/dev/null && yum install -y nodejs 2>/dev/null || {
        curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && apt-get install -y nodejs
    }
fi
ok "Node.js: $(node --version)"
ok "npm: $(npm --version)"

# ---- 2. 创建目录 ----
log "创建安装目录..."
mkdir -p ${INSTALL_DIR}
mkdir -p ${FRONTEND_DIR}
cd ${INSTALL_DIR}

# ---- 3. 解压后端 ----
log "部署后端..."
if [ -f /tmp/agri-deploy-package.tar.gz ]; then
    tar -xzf /tmp/agri-deploy-package.tar.gz -C ${INSTALL_DIR}/
    ok "后端文件解压完成"
else
    log "等待上传后端部署包到 /tmp/agri-deploy-package.tar.gz ..."
    log "请通过 scp 上传: scp agri-deploy-package.tar.gz root@服务器IP:/tmp/"
    err "未找到 /tmp/agri-deploy-package.tar.gz"
fi

# ---- 4. 安装 Python 依赖 ----
log "安装 Python 依赖..."
cd ${BACKEND_DIR}
python3 -m pip install --upgrade pip -q
python3 -m pip install -r requirements.txt -q
ok "Python 依赖安装完成"

# ---- 5. 解压前端 ----
log "部署前端..."
if [ -f /tmp/agri-frontend-dist.tar.gz ]; then
    tar -xzf /tmp/agri-frontend-dist.tar.gz -C ${FRONTEND_DIR}/
    ok "前端文件解压完成"
else
    log "未找到前端 dist 包，尝试从源码构建..."
    if [ -d "${FRONTEND_DIR}/src" ]; then
        cd ${FRONTEND_DIR}
        npm install --registry=https://registry.npmmirror.com
        npm run build
        ok "前端构建完成"
    else
        log "前端源码也不存在，跳过前端部署"
    fi
fi

# ---- 6. 开放防火墙端口 ----
log "配置防火墙..."
if command -v firewall-cmd &>/dev/null; then
    firewall-cmd --add-port=${PORT}/tcp --permanent 2>/dev/null && firewall-cmd --reload 2>/dev/null
    ok "firewalld: 端口 ${PORT} 已开放"
elif command -v ufw &>/dev/null; then
    ufw allow ${PORT}/tcp 2>/dev/null
    ok "ufw: 端口 ${PORT} 已开放"
fi

# 阿里云安全组也需要在控制台开放 8001 端口！

# ---- 7. 停止旧进程，启动服务 ----
log "启动服务..."
lsof -ti:${PORT} | xargs kill -9 2>/dev/null || true
sleep 1

cd ${BACKEND_DIR}
nohup uvicorn app.main:app --host 0.0.0.0 --port ${PORT} > /tmp/agri-server.log 2>&1 &
sleep 3

# ---- 8. 验证 ----
log "验证服务..."
if curl -s http://localhost:${PORT}/ | grep -q "Agri Management Platform\|智慧农业管理平台\|Smart Agriculture"; then
    ok "服务启动成功！"
else
    log "检查服务日志..."
    tail -20 /tmp/agri-server.log
    err "服务启动失败，请检查日志"
fi

# ---- 9. 设置开机自启 ----
log "配置开机自启..."
cat > /etc/systemd/system/agri-platform.service << 'SYSTEMD'
[Unit]
Description=Smart Agriculture Management Platform
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/agri-platform/backend
ExecStart=/usr/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SYSTEMD

systemctl daemon-reload
systemctl enable agri-platform.service
ok "systemd 服务已配置 (开机自启)"

# ---- 完成 ----
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  ✅ 部署完成！${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "  🌐 访问地址:  ${CYAN}http://$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_IP'):${PORT}${NC}"
echo -e "  📋 API 文档:  ${CYAN}http://$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_IP'):${PORT}/docs${NC}"
echo -e "  🔑 登录账号:  ${CYAN}admin / Admin@123456${NC}"
echo ""
echo -e "  管理命令:"
echo -e "    systemctl start agri-platform    启动服务"
echo -e "    systemctl stop agri-platform     停止服务"
echo -e "    systemctl restart agri-platform  重启服务"
echo -e "    systemctl status agri-platform   查看状态"
echo -e "    journalctl -u agri-platform -f   查看日志"
echo ""
echo -e "  ${RED}⚠️  请在阿里云安全组中开放 ${PORT} 端口！${NC}"
echo ""
