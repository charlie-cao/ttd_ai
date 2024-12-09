"""
AI配对编程助手
-----------
集成知识库和记忆系统的智能编程助手。
"""

from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import time

from .core import (
    EmbeddingManager,
    MemorySystem,
    KnowledgeBase,
    Memory,
    KnowledgeItem
)

class AIPairProgrammingAgent:
    """AI配对编程助手"""
    
    def __init__(
        self,
        model_name: str = "shibing624/text2vec-base-chinese",
        memory_threshold: float = 0.7,
        max_memories: int = 1000,
        device: Optional[str] = None,
        cache_dir: Optional[str] = None
    ):
        """
        初始化AI配对编程助手
        
        Args:
            model_name: 模型名称
            memory_threshold: 记忆相似度阈值
            max_memories: 最大记忆数量
            device: 运行设备
            cache_dir: 模型缓存目录
        """
        self.embedding_manager = EmbeddingManager(
            model_name=model_name,
            device=device,
            cache_dir=cache_dir
        )
        self.memory_system = MemorySystem(
            embedding_manager=self.embedding_manager,
            memory_threshold=memory_threshold,
            max_memories=max_memories
        )
        self.knowledge_base = KnowledgeBase(self.embedding_manager)
        self.conversation_history = []
        self.workspace_path = None
    
    def set_workspace(self, path: str):
        """
        设置工作空间路径
        
        Args:
            path: 工作空间路径
        """
        self.workspace_path = Path(path)
    
    def scan_workspace(self, recursive: bool = True) -> str:
        """
        扫描工作空间
        
        Args:
            recursive: 是否递归扫描子目录
            
        Returns:
            str: 扫描结果统计
        """
        if not self.workspace_path:
            raise ValueError("Workspace path not set")
        
        self.knowledge_base.scan_directory(str(self.workspace_path), recursive)
        return self.get_knowledge_base_stats()
    
    def add_memory(
        self,
        content: str,
        memory_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Memory:
        """
        添加记忆
        
        Args:
            content: 记忆内容
            memory_type: 记忆类型
            metadata: 元数据
            
        Returns:
            Memory: 新创建的记忆
        """
        return self.memory_system.add_memory(content, memory_type, metadata)
    
    def generate_response(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        生成响应
        
        Args:
            user_input: 用户输入
            context: 上下文信息
            
        Returns:
            str: 生成的响应
        """
        # 记录用户输入
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": time.time()
        })
        
        # 添加到记忆系统
        self.add_memory(user_input, "conversation", context)
        
        # 获取相关记忆和知识
        relevant_memories = self.memory_system.retrieve_relevant_memories(
            user_input,
            k=3,
            time_window=3600  # 1小时内的记忆
        )
        
        relevant_knowledge = self.knowledge_base.query(
            user_input,
            k=3,
            threshold=0.5
        )
        
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
                    "content": item.content[:500],  # 限制内容长度
                    "category": item.category,
                    "tags": item.tags,
                    "similarity": sim
                }
                for item, sim in relevant_knowledge
            ]
        
        # 生成响应
        response = self._generate_response_with_context(user_input, enhanced_context)
        
        # 记录响应
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": time.time()
        })
        
        # 添加到记忆系统
        self.add_memory(response, "conversation", {"type": "response"})
        
        return response
    
    def _generate_response_with_context(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> str:
        """
        ���据上下文生成响应
        
        Args:
            user_input: 用户输入
            context: 增强的上下文信息
            
        Returns:
            str: 生成的响应
        """
        # 处理记忆和知识
        relevant_memories = context.get("relevant_memories", [])
        relevant_knowledge = context.get("relevant_knowledge", [])
        
        # 构建响应部分
        response_parts = ["我理解你的请求。让我们结合已有的经验和知识来处理。"]
        
        # 添加记忆上下文
        if relevant_memories:
            memory_context = "\n".join([
                f"相关记忆 ({mem['type']}): {mem['content']}"
                for mem in relevant_memories
            ])
            response_parts.append(f"\n基于历史记忆：\n{memory_context}")
        
        # 添加知识上下文
        if relevant_knowledge:
            knowledge_context = "\n".join([
                f"相关知识 ({item['category']}): {item['title']}\n{item['content']}"
                for item in relevant_knowledge
            ])
            response_parts.append(f"\n参考知识：\n{knowledge_context}")
        
        return "\n".join(response_parts)
    
    def get_conversation_history(
        self,
        limit: Optional[int] = None,
        include_metadata: bool = False
    ) -> List[Dict[str, Any]]:
        """
        获取对话历史
        
        Args:
            limit: 返回的最大条目数
            include_metadata: 是否包含元数据
            
        Returns:
            List[Dict[str, Any]]: 对话历史
        """
        history = self.conversation_history
        if limit:
            history = history[-limit:]
        
        if not include_metadata:
            return [{
                "role": item["role"],
                "content": item["content"]
            } for item in history]
        
        return history
    
    def get_knowledge_base_stats(self) -> str:
        """
        获取知识库统计信息
        
        Returns:
            str: 格式化的统计信息
        """
        stats = self.knowledge_base.get_statistics()
        return (
            f"知识库统计：\n"
            f"- 总条目数：{stats['total_items']}\n"
            f"- 分类统计：{', '.join(f'{k}({v})' for k, v in stats['categories'].items())}\n"
            f"- 热门标签：{', '.join(f'{tag}({count})' for tag, count in stats['popular_tags'])}"
        )
    
    def get_memory_stats(self) -> str:
        """
        获取记忆系统统计信息
        
        Returns:
            str: 格式化的统计信息
        """
        stats = self.memory_system.get_memory_stats()
        return (
            f"记忆系统统计：\n"
            f"- 总记忆数：{stats['total_memories']}\n"
            f"- 类型分布：{', '.join(f'{k}({v})' for k, v in stats['type_distribution'].items())}"
        )
    
    def save_state(self, directory: str):
        """
        保存助手状态
        
        Args:
            directory: 保存目录
        """
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        
        # 保存知识库
        self.knowledge_base.save_knowledge_base(
            str(directory / "knowledge_base.json")
        )
        
        # 保存记忆
        self.memory_system.save_memories(
            str(directory / "memories.json")
        )
        
        # 保存对话历史
        with open(directory / "conversation_history.json", 'w', encoding='utf-8') as f:
            import json
            json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
    
    def load_state(self, directory: str):
        """
        加载助手状态
        
        Args:
            directory: 状态目录
        """
        directory = Path(directory)
        
        # 加载知识库
        if (directory / "knowledge_base.json").exists():
            self.knowledge_base.load_knowledge_base(
                str(directory / "knowledge_base.json")
            )
        
        # 加载记忆
        if (directory / "memories.json").exists():
            self.memory_system.load_memories(
                str(directory / "memories.json")
            )
        
        # 加载对话历史
        if (directory / "conversation_history.json").exists():
            with open(directory / "conversation_history.json", 'r', encoding='utf-8') as f:
                import json
                self.conversation_history = json.load(f)
    
    def __repr__(self) -> str:
        kb_stats = self.knowledge_base.get_statistics()
        mem_stats = self.memory_system.get_memory_stats()
        return (
            f"AIPairProgrammingAgent("
            f"knowledge_items={kb_stats['total_items']}, "
            f"memories={mem_stats['total_memories']}, "
            f"conversations={len(self.conversation_history)})"
        )

def create_agent(
    workspace_path: Optional[str] = None,
    model_name: str = "shibing624/text2vec-base-chinese",
    memory_threshold: float = 0.7,
    max_memories: int = 1000,
    device: Optional[str] = None,
    cache_dir: Optional[str] = None,
    load_state_from: Optional[str] = None
) -> AIPairProgrammingAgent:
    """
    创建AI配对编程助手实例
    
    Args:
        workspace_path: 工作空间路径
        model_name: 模型名称
        memory_threshold: 记忆相似度阈值
        max_memories: 最大记忆数量
        device: 运行设备
        cache_dir: 模型缓存目录
        load_state_from: 状态加载目录
        
    Returns:
        AIPairProgrammingAgent: 助手实例
    """
    agent = AIPairProgrammingAgent(
        model_name=model_name,
        memory_threshold=memory_threshold,
        max_memories=max_memories,
        device=device,
        cache_dir=cache_dir
    )
    
    if workspace_path:
        agent.set_workspace(workspace_path)
        agent.scan_workspace()
    
    if load_state_from:
        agent.load_state(load_state_from)
    
    return agent 