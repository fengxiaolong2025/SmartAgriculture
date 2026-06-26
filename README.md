# 智慧农业管理平台 (Smart Agriculture Management Platform)

集 **环境感知 – 智能决策 – 自动控制 – 预警推送 – 数据可视化** 于一体的农业自动化管理平台。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI (Python 3.11) |
| ORM | SQLAlchemy 2.0 (async) |
| 数据库 | PostgreSQL 15 / SQLite (开发) |
| 前端 | Vue 3 + Vite + ECharts 5 + Element Plus |
| 状态管理 | Pinia |
| 认证 | JWT (access + refresh token) |
| 消息协议 | MQTT (EMQX，预留) |

## 项目结构

```
agri-mgmt-platform/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/             # 16 个 API 路由模块 (~70+ 端点)
│   │   ├── models/             # 14 张数据表模型
│   │   ├── schemas/            # Pydantic 数据校验
│   │   ├── services/           # 业务逻辑层
│   │   ├── core/               # JWT/RBAC/异常处理
│   │   └── mock/               # 种子数据 + 模拟生成器
│   └── requirements.txt
│
└── frontend/                   # Vue 3 前端
    └── src/
        ├── views/              # 大屏 + 登录 + 14 个后台管理页面
        ├── stores/             # Pinia 状态管理
        ├── api/                # Axios API 封装
        └── components/         # 大屏组件 + 通用组件
```

## 快速启动

### 1. 启动后端
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. 构建前端
```bash
cd frontend
npm install
npm run build
```

后端会自动 serve 前端静态文件。访问 http://localhost:8000 即可。

### 3. 登录凭据

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 超级管理员 | admin | Admin@123456 |
| 操作员 | operator | Operator@123 |
| 访客 | viewer | Viewer@123 |

## API 文档

启动后端后访问 http://localhost:8000/docs 查看 Swagger UI。

## 数据采集模块

数据采集接口已预留（`POST /api/v1/data/ingest`），MQTT 对接在 Phase 5 进行。
