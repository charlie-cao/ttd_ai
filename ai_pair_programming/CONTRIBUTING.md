# 贡献指南

感谢你考虑为AI配对编程助手项目做出贡献！

## 开发流程

1. Fork本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 开发环境设置

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/ai-pair-programming.git
cd ai-pair-programming
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装开发依赖：
```bash
pip install -e ".[dev]"
```

## 代码规范

- 使用[Black](https://github.com/psf/black)进行代码格式化
- 使用[isort](https://pycqa.github.io/isort/)进行导入排序
- 使用[mypy](http://mypy-lang.org/)进行类型检查
- 遵循[PEP 8](https://www.python.org/dev/peps/pep-0008/)编码规范

## 提交规范

提交信息应该清晰描述更改内容，建议使用以下格式：

- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码风格更改
- refactor: 代码重构
- test: 测试相关
- chore: 构建过程或辅助工具的变动

示例：
```
feat: 添加JSON文件处理器
```

## 测试

- 所有新功能都需要添加测试
- 确保所有测试通过：
```bash
pytest
```

## 文档

- 更新相关文档
- 添加必要的代码注释
- 保持README.md的更新

## Pull Request流程

1. 确保PR描述清晰地说明了更改内容和原因
2. 确保所有测试通过
3. 更新相关文档
4. 等待review

## 行为准则

- 保持友善和专业
- 尊重其他贡献者
- 接受建设性的批评
- 专注于项目目标

## 问题反馈

- 使用GitHub Issues提交问题
- 清晰描述问题和复现步骤
- 提供相关的日志和错误信息
- 标注相关标签

## 许可证

通过提交PR，你同意你的贡献将在MIT许可证下发布。 