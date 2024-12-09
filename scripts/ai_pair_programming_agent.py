"""
AI Pair Programming Agent
------------------------
一个基于知识库和记忆系统的AI配对编程助手。

主要功能：
1. 知识库管理：自动扫描和导入项目文件
2. 记忆系统：维护对话历史和上下文
3. 提示词管理：动态生成和管理提示词
"""

import os
import json
from typing import Dict, List, Optional, Tuple, Any, Protocol
from dataclasses import dataclass
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import torch
from transformers import AutoTokenizer, AutoModel
import time
import yaml
from pathlib import Path
import hashlib
import re
from datetime import datetime
from abc import ABC, abstractmethod

# ============= 核心接口定义 =============

class VectorStore(Protocol):
    """向量存储接口"""
    def add_vector(self, key: str, vector: np.ndarray) -> None: ...
    def search(self, query_vector: np.ndarray, k: int) -> List[Tuple[str, float]]: ...
    def get_vector(self, key: str) -> Optional[np.ndarray]: ...

class ContentProcessor(Protocol):
    """内容处理器接口"""
    def extract_content(self, content: str) -> Tuple[str, str, List[str]]: ...
    def supported_extensions(self) -> List[str]: ...

# ============= 数据模型 =============

@dataclass
class Memory:
    """记忆单元"""
    content: str
    embedding: np.ndarray
    timestamp: float
    type: str  # 'conversation', 'code', 'prompt'
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class KnowledgeItem:
    """知识条目"""
    id: str
    title: str
    content: str
    category: str
    tags: List[str]
    source_file: Optional[str] = None
    embedding: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = None

@dataclass
class PromptTemplate:
    """提示词模板"""
    name: str
    template: str
    example: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# ============= 实现类 =============

class SimpleVectorStore(VectorStore):
    """简单的向量存储实现"""
    def __init__(self):
        self.vectors: Dict[str, np.ndarray] = {}

    def add_vector(self, key: str, vector: np.ndarray) -> None:
        self.vectors[key] = vector

    def search(self, query_vector: np.ndarray, k: int) -> List[Tuple[str, float]]:
        if not self.vectors:
            return []
        
        similarities = [
            (key, float(cosine_similarity(query_vector.reshape(1, -1), 
                                        vec.reshape(1, -1))[0][0]))
            for key, vec in self.vectors.items()
        ]
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]

    def get_vector(self, key: str) -> Optional[np.ndarray]:
        return self.vectors.get(key)

class EmbeddingManager:
    """嵌入向量管理器"""
    def __init__(self, model_name: str = "shibing624/text2vec-base-chinese"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def get_embedding(self, text: str) -> np.ndarray:
        """生成文本嵌入向量"""
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1)
        
        return embeddings.cpu().numpy()[0]

# ============= 内容处理器 =============

class MarkdownProcessor(ContentProcessor):
    """Markdown文件处理器"""
    def extract_content(self, content: str) -> Tuple[str, str, List[str]]:
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else "Untitled"
        tags = re.findall(r'(?:tags:|#)([a-zA-Z0-9_\-]+)', content)
        return title, content, tags

    def supported_extensions(self) -> List[str]:
        return ['.md', '.markdown']

class PythonProcessor(ContentProcessor):
    """Python文件处理器"""
    def extract_content(self, content: str) -> Tuple[str, str, List[str]]:
        docstring_match = re.search(r'"""(.+?)"""', content, re.DOTALL)
        title = ""
        if docstring_match:
            docstring = docstring_match.group(1).strip()
            first_line = docstring.split('\n')[0]
            title = first_line
        
        tags = re.findall(r'(?:def|class)\s+([a-zA-Z0-9_]+)', content)
        return title or "Python Module", content, tags

    def supported_extensions(self) -> List[str]:
        return ['.py']

# ============= 知识库管理 =============

class KnowledgeBase:
    """知识库管理器"""
    def __init__(self, embedding_manager: EmbeddingManager, vector_store: Optional[VectorStore] = None):
        self.embedding_manager = embedding_manager
        self.vector_store = vector_store or SimpleVectorStore()
        self.knowledge_items: Dict[str, KnowledgeItem] = {}
        self.categories: Dict[str, List[str]] = {}
        self.tags: Dict[str, List[str]] = {}
        self.processors: Dict[str, ContentProcessor] = {
            '.md': MarkdownProcessor(),
            '.py': PythonProcessor(),
        }

    def register_processor(self, processor: ContentProcessor):
        """注册新的内容处理器"""
        for ext in processor.supported_extensions():
            self.processors[ext] = processor

    def scan_directory(self, directory_path: str, recursive: bool = True):
        """扫描目录并导入知识"""
        base_path = Path(directory_path)
        pattern = "**/*" if recursive else "*"
        
        for file_path in base_path.glob(pattern):
            if file_path.is_file() and file_path.suffix in self.processors:
                try:
                    self.import_file(file_path)
                except Exception as e:
                    print(f"Error importing {file_path}: {str(e)}")

    def import_file(self, file_path: Path):
        """导入单个文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        processor = self.processors.get(file_path.suffix)
        if not processor:
            return
        
        title, content, tags = processor.extract_content(content)
        file_id = hashlib.md5(f"{file_path}:{hash(content)}".encode()).hexdigest()[:12]
        category = file_path.parent.name or "general"
        
        item = KnowledgeItem(
            id=file_id,
            title=title,
            content=content,
            category=category,
            tags=tags,
            source_file=str(file_path),
            metadata={
                "file_type": file_path.suffix,
                "imported_at": datetime.now().isoformat(),
                "file_size": os.path.getsize(file_path)
            }
        )
        
        self.add_item(item)

    def add_item(self, item: KnowledgeItem):
        """添加知识条目"""
        if item.embedding is None:
            item.embedding = self.embedding_manager.get_embedding(f"{item.title}\n{item.content}")
        
        self.knowledge_items[item.id] = item
        self.vector_store.add_vector(item.id, item.embedding)
        
        if item.category not in self.categories:
            self.categories[item.category] = []
        self.categories[item.category].append(item.id)
        
        for tag in item.tags:
            if tag not in self.tags:
                self.tags[tag] = []
            self.tags[tag].append(item.id)

    def query(self, query_text: str, k: int = 3, category: Optional[str] = None, 
             tags: Optional[List[str]] = None) -> List[Tuple[KnowledgeItem, float]]:
        """查询知识库"""
        query_embedding = self.embedding_manager.get_embedding(query_text)
        results = self.vector_store.search(query_embedding, k)
        
        items_with_scores = [
            (self.knowledge_items[item_id], score)
            for item_id, score in results
            if item_id in self.knowledge_items
        ]
        
        if category:
            items_with_scores = [
                (item, score) for item, score in items_with_scores
                if item.category == category
            ]
        
        if tags:
            items_with_scores = [
                (item, score) for item, score in items_with_scores
                if any(tag in item.tags for tag in tags)
            ]
        
        return items_with_scores

    def get_statistics(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        return {
            "total_items": len(self.knowledge_items),
            "categories": {
                category: len(items)
                for category, items in self.categories.items()
            },
            "total_tags": len(self.tags),
            "popular_tags": sorted(
                [(tag, len(items)) for tag, items in self.tags.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }

# ============= AI配对编程助手 =============

class AIPairProgrammingAgent:
    """AI配对编程助手"""
    def __init__(self, model_name: str = "shibing624/text2vec-base-chinese"):
        self.embedding_manager = EmbeddingManager(model_name)
        self.knowledge_base = KnowledgeBase(self.embedding_manager)
        self.memories: List[Memory] = []
        self.conversation_history = []
        self.memory_threshold = 0.7
        self.workspace_path = None

    def set_workspace(self, path: str):
        """设置工作空间路径"""
        self.workspace_path = path

    def scan_workspace(self, recursive: bool = True):
        """扫描工作空间"""
        if not self.workspace_path:
            raise ValueError("Workspace path not set")
        return self.scan_directory_to_knowledge_base(self.workspace_path, recursive)

    def scan_directory_to_knowledge_base(self, directory_path: str, recursive: bool = True) -> str:
        """扫描目录并构建知识库"""
        self.knowledge_base.scan_directory(directory_path, recursive)
        return self.get_knowledge_base_stats()

    def add_memory(self, content: str, memory_type: str, metadata: Optional[Dict[str, Any]] = None):
        """添加记忆"""
        embedding = self.embedding_manager.get_embedding(content)
        memory = Memory(
            content=content,
            embedding=embedding,
            timestamp=time.time(),
            type=memory_type,
            metadata=metadata
        )
        self.memories.append(memory)

    def retrieve_relevant_memories(self, query: str, k: int = 3) -> List[Tuple[Memory, float]]:
        """检索相关记忆"""
        if not self.memories:
            return []

        query_embedding = self.embedding_manager.get_embedding(query)
        similarities = [
            (memory, float(cosine_similarity(query_embedding.reshape(1, -1), 
                                          memory.embedding.reshape(1, -1))[0][0]))
            for memory in self.memories
        ]
        
        relevant_memories = [
            (memory, sim) for memory, sim in similarities
            if sim >= self.memory_threshold
        ]
        relevant_memories.sort(key=lambda x: x[1], reverse=True)
        return relevant_memories[:k]

    def generate_response(self, user_input: str, context: Optional[Dict] = None) -> str:
        """生成响应"""
        self.conversation_history.append({"role": "user", "content": user_input})
        self.add_memory(user_input, "conversation", context)
        
        # 获取相关记忆和知识
        relevant_memories = self.retrieve_relevant_memories(user_input)
        relevant_knowledge = self.knowledge_base.query(user_input)
        
        # 构建增强上下文
        enhanced_context = context or {}
        if relevant_memories:
            enhanced_context["relevant_memories"] = [
                {
                    "content": memory.content,
                    "type": memory.type,
                    "similarity": sim,
                    "metadata": memory.metadata
                }
                for memory, sim in relevant_memories
            ]
        
        if relevant_knowledge:
            enhanced_context["relevant_knowledge"] = [
                {
                    "title": item.title,
                    "content": item.content,
                    "category": item.category,
                    "tags": item.tags,
                    "similarity": sim
                }
                for item, sim in relevant_knowledge
            ]
        
        # 生成响应
        response = self._generate_response_with_context(user_input, enhanced_context)
        
        self.conversation_history.append({"role": "assistant", "content": response})
        self.add_memory(response, "conversation", {"type": "response"})
        
        return response

    def _generate_response_with_context(self, user_input: str, context: Dict) -> str:
        """根据上下文生成响应"""
        # 这里可以集成不同的响应生成策略
        relevant_memories = context.get("relevant_memories", [])
        relevant_knowledge = context.get("relevant_knowledge", [])
        
        memory_context = "\n".join([
            f"相关记忆 ({mem['type']}): {mem['content']}"
            for mem in relevant_memories
        ])
        
        knowledge_context = "\n".join([
            f"相关知识 ({item['category']}): {item['title']}\n{item['content'][:200]}..."
            for item in relevant_knowledge
        ])
        
        response_parts = ["我理解你的请求。让我们结合已有的经验和知识来处理。"]
        if memory_context:
            response_parts.append(f"\n基于历史记忆：\n{memory_context}")
        if knowledge_context:
            response_parts.append(f"\n参考知识：\n{knowledge_context}")
        
        return "\n".join(response_parts)

    def get_knowledge_base_stats(self) -> str:
        """获取知识库统计信息"""
        stats = self.knowledge_base.get_statistics()
        return (
            f"知识库统计：\n"
            f"- 总条目数：{stats['total_items']}\n"
            f"- 分类统计：{', '.join(f'{k}({v})' for k, v in stats['categories'].items())}\n"
            f"- 热门标签：{', '.join(f'{tag}({count})' for tag, count in stats['popular_tags'])}"
        )

def create_agent(workspace_path: Optional[str] = None, 
                model_name: str = "shibing624/text2vec-base-chinese") -> AIPairProgrammingAgent:
    """创建AI配对编程助手实例"""
    agent = AIPairProgrammingAgent(model_name)
    if workspace_path:
        agent.set_workspace(workspace_path)
        agent.scan_workspace()
    return agent

if __name__ == "__main__":
    # 使用示例
    agent = create_agent("./workspace")
    
    # 扫描特定目录
    print(agent.scan_directory_to_knowledge_base("docs"))
    
    # 交互示例
    response = agent.generate_response(
        "让我们开始一个新的Python项目，使用TDD方式开发",
        context={"os": "windows", "env_tool": "venv", "language": "中文"}
    )
    print(response)
    
    # 打印知识库统计
    print("\n" + agent.get_knowledge_base_stats()) 