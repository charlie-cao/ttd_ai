"""
记忆系统模块
----------
管理对话历史和上下文记忆。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from datetime import datetime
import json
from pathlib import Path
import time

from .embedding import EmbeddingManager

@dataclass
class Memory:
    """记忆单元"""
    content: str
    embedding: np.ndarray
    timestamp: float
    type: str  # 'conversation', 'code', 'prompt'
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "content": self.content,
            "embedding": self.embedding.tolist(),
            "timestamp": self.timestamp,
            "type": self.type,
            "metadata": self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Memory":
        """从字典创建实例"""
        return cls(
            content=data["content"],
            embedding=np.array(data["embedding"]),
            timestamp=data["timestamp"],
            type=data["type"],
            metadata=data["metadata"]
        )

class MemorySystem:
    """记忆系统"""
    
    def __init__(
        self,
        embedding_manager: EmbeddingManager,
        memory_threshold: float = 0.7,
        max_memories: int = 1000
    ):
        """
        初始化记忆系统
        
        Args:
            embedding_manager: 嵌入向量管理器
            memory_threshold: 记忆相似度阈值
            max_memories: 最大记忆数量
        """
        self.embedding_manager = embedding_manager
        self.memory_threshold = memory_threshold
        self.max_memories = max_memories
        self.memories: List[Memory] = []
    
    def add_memory(
        self,
        content: str,
        memory_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Memory:
        """
        添加新记忆
        
        Args:
            content: 记忆内容
            memory_type: 记忆类型
            metadata: 元数据
            
        Returns:
            Memory: 新创建的记忆
        """
        embedding = self.embedding_manager.get_embedding(content)
        memory = Memory(
            content=content,
            embedding=embedding,
            timestamp=time.time(),
            type=memory_type,
            metadata=metadata
        )
        
        self.memories.append(memory)
        
        # 如果超过最大记忆数量，删除最旧的记忆
        if len(self.memories) > self.max_memories:
            self.memories.sort(key=lambda x: x.timestamp)
            self.memories = self.memories[-self.max_memories:]
        
        return memory
    
    def retrieve_relevant_memories(
        self,
        query: str,
        k: int = 3,
        memory_type: Optional[str] = None,
        time_window: Optional[float] = None
    ) -> List[Tuple[Memory, float]]:
        """
        检索相关记忆
        
        Args:
            query: 查询文本
            k: 返回结果数量
            memory_type: 筛选记忆类型
            time_window: 时间窗口（秒）
            
        Returns:
            List[Tuple[Memory, float]]: 记忆和相似度得分列表
        """
        if not self.memories:
            return []
        
        query_embedding = self.embedding_manager.get_embedding(query)
        current_time = time.time()
        
        # 筛选记忆
        candidate_memories = self.memories
        if memory_type:
            candidate_memories = [m for m in candidate_memories if m.type == memory_type]
        if time_window:
            candidate_memories = [
                m for m in candidate_memories
                if current_time - m.timestamp <= time_window
            ]
        
        # 计算相似度
        similarities = [
            (memory, float(np.dot(query_embedding, memory.embedding) /
                         (np.linalg.norm(query_embedding) * np.linalg.norm(memory.embedding))))
            for memory in candidate_memories
        ]
        
        # 筛选并排序
        relevant_memories = [
            (memory, sim) for memory, sim in similarities
            if sim >= self.memory_threshold
        ]
        relevant_memories.sort(key=lambda x: x[1], reverse=True)
        
        return relevant_memories[:k]
    
    def save_memories(self, path: str):
        """
        保存记忆到文件
        
        Args:
            path: 保存路径
        """
        data = {
            "memory_threshold": self.memory_threshold,
            "max_memories": self.max_memories,
            "memories": [memory.to_dict() for memory in self.memories]
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_memories(self, path: str):
        """
        从文件加载记忆
        
        Args:
            path: 记忆文件路径
        """
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.memory_threshold = data["memory_threshold"]
        self.max_memories = data["max_memories"]
        self.memories = [Memory.from_dict(m) for m in data["memories"]]
    
    def clear_memories(self, memory_type: Optional[str] = None):
        """
        清除记忆
        
        Args:
            memory_type: 要清除的记忆类型，None表示清除所有
        """
        if memory_type:
            self.memories = [m for m in self.memories if m.type != memory_type]
        else:
            self.memories.clear()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        获取记忆统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        type_counts = {}
        for memory in self.memories:
            type_counts[memory.type] = type_counts.get(memory.type, 0) + 1
        
        return {
            "total_memories": len(self.memories),
            "type_distribution": type_counts,
            "oldest_memory": min(m.timestamp for m in self.memories) if self.memories else None,
            "newest_memory": max(m.timestamp for m in self.memories) if self.memories else None
        }
    
    def __len__(self) -> int:
        return len(self.memories)
    
    def __repr__(self) -> str:
        stats = self.get_memory_stats()
        return f"MemorySystem(memories={stats['total_memories']}, types={list(stats['type_distribution'].keys())})" 