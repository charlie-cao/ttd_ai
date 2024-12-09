# CI/CD 配置指南

本文档详细说明了项目的 CI/CD 流程配置，包括代码质量检查、测试自动化、覆盖率报告和自动部署。

## 1. GitHub Actions 配置

我们使用 GitHub Actions 作为主要的 CI 工具，配置文件位于 `.github/workflows/ci.yml`。

### 1.1 工作流触发条件
```yaml
on:
  push:
    branches: [ master ]
  pull_request:
    branches: [ master ]
```

### 1.2 后端测试流程
```yaml
backend-tests:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      working-directory: ./backend
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    - name: Run tests with coverage
      working-directory: ./backend
      run: |
        pytest --cov --cov-report=xml
```

### 1.3 前端测试流程
```yaml
frontend-tests:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    - name: Install dependencies
      working-directory: ./frontend
      run: npm install --legacy-peer-deps
    - name: Run tests with coverage
      working-directory: ./frontend
      run: npx vitest run --coverage
```

## 2. 代码覆盖率报告

我们使用 Codecov 来跟踪和展示代码覆盖率。

### 2.1 配置步骤
1. 注册 Codecov 账号
2. 获取 Codecov token
3. 在 GitHub 仓库设置中添加 secret：`CODECOV_TOKEN`
4. 在 CI 配置中添加上传步骤：
```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v5
  with:
    token: ${{ secrets.CODECOV_TOKEN }}
```

### 2.2 覆盖率报告配置
- 后端：使用 pytest-cov 生成 XML 格式报告
- 前端：使用 @vitest/coverage-v8 生成覆盖率报告

## 3. 自动部署流程

我们使用 Render 作为部署平台，实现了前后端分离部署。

### 3.1 前端部署 (Static Site)
- 仓库：`charlie-cao/ttd_ai`
- 分支：`master`
- 构建命令：`npm install && npm run build`
- 发布目录：`dist`
- 环境变量：
  ```
  NODE_VERSION=18
  VITE_API_URL=https://ttd-ai-backend.onrender.com
  ```

### 3.2 后端部署 (Web Service)
- 仓库：同上
- 根目录：`backend`
- 构建命令：`pip install -r requirements.txt`
- 启动命令：`cd src && uvicorn main:app --host 0.0.0.0 --port $PORT`
- 环境变量：
  ```
  DATABASE_URL=postgresql://...
  SECRET_KEY=your-secret-key
  ALGORITHM=HS256
  ACCESS_TOKEN_EXPIRE_MINUTES=30
  CORS_ORIGINS=http://localhost:5173,https://ttd-ai-frontend.onrender.com
  ```

### 3.3 数据库配置 (PostgreSQL)
- 平台：Render
- 类型：PostgreSQL
- 连接：通过环境变量注入到后端服务

## 4. 开发工作流程

1. 功能开发
   - 创建功能分支
   - 编写测试
   - 实现功能
   - 提交代码

2. 代码审查
   - 创建 Pull Request
   - CI 自动运行测试
   - Codecov 生成覆盖率报告
   - 审查代码和测试结果

3. 合并和部署
   - 合并到 master 分支
   - 自动触发部署流程
   - 监控部署状态
   - 验证功能

## 5. 监控和维护

1. 性能监控
   - Render 提供的基础监控
   - 应用日志查看
   - 数据库性能监控

2. 错误追踪
   - 查看应用日志
   - 监控错误率
   - 设置告警通知

3. 定期维护
   - 更新依赖
   - 检查安全漏洞
   - 优化性能
   - 备份数据

## 6. 安全实践

1. 密钥管理
   - 使用环境变量存储敏感信息
   - 定期轮换密钥
   - 使用 GitHub Secrets 保护 CI/CD 密钥

2. 访问控制
   - 实施 CORS 策略
   - 使用 JWT 认证
   - 限制数据库访问

3. 数据保护
   - 数据库自动备份
   - 加密敏感数据
   - 实施访问日志 