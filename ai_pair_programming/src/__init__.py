"""
AI Pair Programming
-----------------
基于知识库和记忆系统的AI配对编程助手。
"""

from .core import (
    EmbeddingManager,
    Memory,
    MemorySystem,
    KnowledgeItem,
    ContentProcessor,
    MarkdownProcessor,
    PythonProcessor,
    KnowledgeBase
)
from .agent import AIPairProgrammingAgent, create_agent

__version__ = "0.1.0"

__all__ = [
    'EmbeddingManager',
    'Memory',
    'MemorySystem',
    'KnowledgeItem',
    'ContentProcessor',
    'MarkdownProcessor',
    'PythonProcessor',
    'KnowledgeBase',
    'AIPairProgrammingAgent',
    'create_agent',
] 