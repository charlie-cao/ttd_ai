# TDD Todo API

这是一个使用测试驱动开发（TDD）方法构建的 Python FastAPI 后端项目。项目实现了一个带用户认证的待办事项 API。

## 功能特点

- 用户认证（注册和登录）
- 待办事项的 CRUD 操作
- 基于 JWT 的认证机制
- 用户数据隔离
- 完整的测试覆盖
- SQLite 数据库存储

## 技术栈

- FastAPI：现代、快速的 Web 框架
- SQLAlchemy：ORM 和数据库操作
- Pytest：测试框架
- JWT：用户认证
- SQLite：数据库
- Pydantic：数据验证
- Uvicorn：ASGI 服务器

## 项目结构

```
.
├── src/                # 源代码目录
│   ├── __init__.py
│   ├── main.py        # 主应用
│   ├── models.py      # 数据模型
│   ├── database.py    # 数据库配置
│   └── auth.py        # 认证相关
├── tests/             # 测试代码目录
│   ├── __init__.py
│   ├── test_todo.py   # Todo API 测试
│   └── test_auth.py   # 认证测试
├── API_使用说明.txt    # API 使用文档
├── requirements.txt   # 项目依赖
└── README.md         # 项目说明
```

## 开发环境设置

1. 创建虚拟环境：
```bash
python -m venv venv
```

2. 激活虚拟环境：
```bash
# Windows
.\venv\Scripts\activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

## 运行测试

```bash
python -m pytest tests/ -v
```

## 启动服务器

```bash
uvicorn src.main:app --reload
```

## API 文档

- 交互式 API 文档：http://localhost:8000/docs
- 详细使用说明：见 API_使用说明.txt

## 开发原则

项目遵循 TDD（测试驱动开发）的基本原则：

1. 先写测试，后写实现
2. 保持测试简单
3. 重构时保证测试通过

## 安全说明

- 用户密码使用 bcrypt 加密存储
- 使用 JWT 进行身份验证
- 实现了用户数据隔离
- 所有 API 端点都有适当的权限控制

## 许可

MIT License
