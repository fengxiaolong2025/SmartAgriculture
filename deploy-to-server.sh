#!/bin/bash
# =============================================
# 从你的本地电脑执行此脚本，将项目部署到阿里云
# =============================================
set -e

SERVER="121.41.71.134"
USER="root"
REMOTE_DIR="/opt/agri-platform"
PORT=8001

echo "============================================"
echo "  智慧农业管理平台 - 阿里云部署"
echo "============================================"

# Step 1: 从 GitHub 克隆最新代码
echo ""
echo "📦 Step 1: 从 GitHub 拉取代码..."
ssh ${USER}@${SERVER} << 'ENDSSH'
    if [ -d /opt/agri-platform ]; then
        cd /opt/agri-platform && git pull origin main
    else
        git clone https://github.com/fengxiaolong2025/SmartAgriculture.git /opt/agri-platform
    fi
ENDSSH

# Step 2: 安装 Python 依赖
echo ""
echo "🐍 Step 2: 安装 Python 依赖..."
ssh ${USER}@${SERVER} "cd ${REMOTE_DIR}/backend && pip3 install -r requirements.txt"

# Step 3: 构建前端
echo ""
echo "🔨 Step 3: 构建前端..."
ssh ${USER}@${SERVER} << 'ENDSSH'
    cd /opt/agri-platform/frontend
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    npm run build
ENDSSH

# Step 4: 开放端口
echo ""
echo "🔥 Step 4: 配置防火墙..."
ssh ${USER}@${SERVER} << 'ENDSSH'
    firewall-cmd --add-port=8001/tcp --permanent 2>/dev/null && firewall-cmd --reload 2>/dev/null || true
    iptables -I INPUT -p tcp --dport 8001 -j ACCEPT 2>/dev/null || true
ENDSSH

# Step 5: 重启服务
echo ""
echo "🚀 Step 5: 启动服务..."
ssh ${USER}@${SERVER} << 'ENDSSH'
    lsof -ti:8001 | xargs kill -9 2>/dev/null || true
    sleep 1
    cd /opt/agri-platform/backend
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8001 > /tmp/agri-server.log 2>&1 &
    sleep 3
    curl -s http://localhost:8001/ | head -c 200
ENDSSH

echo ""
echo "============================================"
echo "  ✅ 部署完成！"
echo "  🌐 http://${SERVER}:${PORT}"
echo "  🔑 admin / Admin@123456"
echo "============================================"
