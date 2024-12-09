# AI Pair Programming Assistant

一个基于知识库和记忆系统的AI配对编程助手。

## 特性

- 🧠 智能知识库管理
  - 自动扫描和导入项目文件
  - 支持多种文件格式（Markdown、Python等）
  - 基于语义的相似度搜索

- 💭 上下文记忆系统
  - 对话历史管理
  - 语义相似度检索
  - 上下文关联分析

- 🔧 可扩展的架构
  - 模块化设计
  - 插件式内容处理器
  - 自定义向量存储

## 安装

```bash
# 使用pip安装
pip install ai-pair-programming

# 开发环境安装
pip install -e ".[dev]"
```

## 快速开始

```python
from ai_pair_programming import create_agent

# 创建agent实例
agent = create_agent("./workspace")

# 扫描工作目录
agent.scan_workspace()

# 交互示例
response = agent.generate_response(
    "让我们开始一个新的Python项目",
    context={"os": "windows", "env_tool": "venv"}
)
print(response)

# 查看知识库统计
print(agent.get_knowledge_base_stats())
```

## 项目结构

```
ai_pair_programming/
├── src/                    # 源代码
│   ├── core/              # 核心功能
│   │   ├── knowledge.py   # 知识库管理
│   │   ├── memory.py      # 记忆系统
│   │   └── embedding.py   # 向量嵌入
│   ├── processors/        # 内容处理器
│   │   ├── markdown.py    # Markdown处理
│   │   └── python.py      # Python处理
│   └── utils/             # 工具函数
├── tests/                 # 测试文件
├── docs/                  # 文档
└── examples/             # 使用示例
```

## 开发指南

1. 克隆仓库
```bash
git clone https://github.com/yourusername/ai-pair-programming.git
cd ai-pair-programming
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖
```bash
pip install -e ".[dev]"
```

4. 运行测试
```bash
pytest
```

## 添加新的内容处理器

```python
from ai_pair_programming.core import ContentProcessor
from typing import Tuple, List

class JsonProcessor(ContentProcessor):
    def extract_content(self, content: str) -> Tuple[str, str, List[str]]:
        # 实现JSON文件的处理逻辑
        ...
    
    def supported_extensions(self) -> List[str]:
        return ['.json']

# 注册处理器
knowledge_base.register_processor(JsonProcessor())
```

## 许可证

MIT License

## 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request
</rewritten_file> 