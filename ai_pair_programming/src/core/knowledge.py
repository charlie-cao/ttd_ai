"""
知识库管理模块
-----------
管理和检索项目相关的知识。
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple, Protocol
import numpy as np
from pathlib import Path
import json
import yaml
import hashlib
import time
from abc import ABC, abstractmethod

from .embedding import EmbeddingManager

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
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "tags": self.tags,
            "source_file": self.source_file,
            "embedding": self.embedding.tolist() if self.embedding is not None else None,
            "metadata": self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeItem":
        """从字典创建实例"""
        embedding = np.array(data["embedding"]) if data.get("embedding") else None
        return cls(
            id=data["id"],
            title=data["title"],
            content=data["content"],
            category=data["category"],
            tags=data["tags"],
            source_file=data.get("source_file"),
            embedding=embedding,
            metadata=data.get("metadata", {})
        )

class ContentProcessor(Protocol):
    """内容处理器接口"""
    def extract_content(self, content: str) -> Tuple[str, str, List[str]]: ...
    def supported_extensions(self) -> List[str]: ...

class MarkdownProcessor:
    """Markdown文件处理器"""
    def extract_content(self, content: str) -> Tuple[str, str, List[str]]:
        """提取Markdown内容"""
        import re
        
        # 提取标题
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else "Untitled"
        
        # 提取标签
        tags = re.findall(r'(?:tags:|#)([a-zA-Z0-9_\-]+)', content)
        
        return title, content, tags
    
    def supported_extensions(self) -> List[str]:
        return ['.md', '.markdown']

class PythonProcessor:
    """Python文件处理器"""
    def extract_content(self, content: str) -> Tuple[str, str, List[str]]:
        """提取Python文件内容"""
        import re
        
        # 提取文档字符串作为标题
        docstring_match = re.search(r'"""(.+?)"""', content, re.DOTALL)
        title = ""
        if docstring_match:
            docstring = docstring_match.group(1).strip()
            first_line = docstring.split('\n')[0]
            title = first_line
        
        # 提取函数和类名作为标签
        tags = re.findall(r'(?:def|class)\s+([a-zA-Z0-9_]+)', content)
        
        return title or "Python Module", content, tags
    
    def supported_extensions(self) -> List[str]:
        return ['.py']

class KnowledgeBase:
    """知识库管理器"""
    
    def __init__(self, embedding_manager: EmbeddingManager):
        """
        初始化知识库
        
        Args:
            embedding_manager: 嵌入向量管理器
        """
        self.embedding_manager = embedding_manager
        self.knowledge_items: Dict[str, KnowledgeItem] = {}
        self.categories: Dict[str, List[str]] = {}
        self.tags: Dict[str, List[str]] = {}
        
        # 注册默认处理器
        self.processors: Dict[str, ContentProcessor] = {
            '.md': MarkdownProcessor(),
            '.py': PythonProcessor(),
        }
    
    def register_processor(self, processor: ContentProcessor):
        """
        注册新的内容处理器
        
        Args:
            processor: 内容处理器实例
        """
        for ext in processor.supported_extensions():
            self.processors[ext] = processor
    
    def scan_directory(self, directory_path: str, recursive: bool = True):
        """
        扫描目录并导入知识
        
        Args:
            directory_path: 目录路径
            recursive: 是否递归扫描子目录
        """
        base_path = Path(directory_path)
        pattern = "**/*" if recursive else "*"
        
        for file_path in base_path.glob(pattern):
            if file_path.is_file() and file_path.suffix in self.processors:
                try:
                    self.import_file(file_path)
                except Exception as e:
                    print(f"Error importing {file_path}: {str(e)}")
    
    def import_file(self, file_path: Path):
        """
        导入单个文件
        
        Args:
            file_path: 文件路径
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        processor = self.processors.get(file_path.suffix)
        if not processor:
            return
        
        # 提取内容
        title, content, tags = processor.extract_content(content)
        
        # 生成唯一ID
        file_id = hashlib.md5(
            f"{file_path}:{hash(content)}".encode()
        ).hexdigest()[:12]
        
        # 使用父目录作为分类
        category = file_path.parent.name or "general"
        
        # 创建知识条目
        item = KnowledgeItem(
            id=file_id,
            title=title,
            content=content,
            category=category,
            tags=tags,
            source_file=str(file_path),
            metadata={
                "file_type": file_path.suffix,
                "imported_at": time.time(),
                "file_size": file_path.stat().st_size
            }
        )
        
        self.add_item(item)
    
    def add_item(self, item: KnowledgeItem):
        """
        添加知识条目
        
        Args:
            item: 知识条目
        """
        # 生成嵌入向量
        if item.embedding is None:
            item.embedding = self.embedding_manager.get_embedding(
                f"{item.title}\n{item.content}"
            )
        
        self.knowledge_items[item.id] = item
        
        # 更新索引
        if item.category not in self.categories:
            self.categories[item.category] = []
        self.categories[item.category].append(item.id)
        
        for tag in item.tags:
            if tag not in self.tags:
                self.tags[tag] = []
            self.tags[tag].append(item.id)
    
    def query(
        self,
        query_text: str,
        k: int = 3,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        threshold: float = 0.5
    ) -> List[Tuple[KnowledgeItem, float]]:
        """
        查询知识库
        
        Args:
            query_text: 查询文本
            k: 返回结果数量
            category: 筛选分类
            tags: 筛选标签
            threshold: 相似度阈值
            
        Returns:
            List[Tuple[KnowledgeItem, float]]: 知识条目和相似度得分列表
        """
        query_embedding = self.embedding_manager.get_embedding(query_text)
        
        # 筛选候选项
        candidate_items = self.knowledge_items.values()
        if category:
            category_items = set(self.categories.get(category, []))
            candidate_items = [
                item for item in candidate_items
                if item.id in category_items
            ]
        
        if tags:
            tagged_items = set()
            for tag in tags:
                tagged_items.update(self.tags.get(tag, []))
            candidate_items = [
                item for item in candidate_items
                if item.id in tagged_items
            ]
        
        # 计算相似度
        similarities = [
            (item, float(np.dot(query_embedding, item.embedding) /
                       (np.linalg.norm(query_embedding) * np.linalg.norm(item.embedding))))
            for item in candidate_items
        ]
        
        # 筛选并排序
        relevant_items = [
            (item, sim) for item, sim in similarities
            if sim >= threshold
        ]
        relevant_items.sort(key=lambda x: x[1], reverse=True)
        
        return relevant_items[:k]
    
    def save_knowledge_base(self, path: str):
        """
        保存知识库到文件
        
        Args:
            path: 保存路径
        """
        data = {
            "items": [item.to_dict() for item in self.knowledge_items.values()]
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_knowledge_base(self, path: str):
        """
        从文件加载知识库
        
        Args:
            path: 知识库文件路径
        """
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 清空当前知识库
        self.knowledge_items.clear()
        self.categories.clear()
        self.tags.clear()
        
        # 加载知识条目
        for item_data in data["items"]:
            item = KnowledgeItem.from_dict(item_data)
            self.add_item(item)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取知识库统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
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
    
    def __len__(self) -> int:
        return len(self.knowledge_items)
    
    def __repr__(self) -> str:
        stats = self.get_statistics()
        return f"KnowledgeBase(items={stats['total_items']}, categories={len(stats['categories'])})" 