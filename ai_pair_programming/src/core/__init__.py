"""
AI Pair Programming Core
----------------------
核心功能模块。
"""

from .embedding import EmbeddingManager
from .memory import Memory, MemorySystem
from .knowledge import (
    KnowledgeItem,
    ContentProcessor,
    MarkdownProcessor,
    PythonProcessor,
    KnowledgeBase
)

__all__ = [
    'EmbeddingManager',
    'Memory',
    'MemorySystem',
    'KnowledgeItem',
    'ContentProcessor',
    'MarkdownProcessor',
    'PythonProcessor',
    'KnowledgeBase',
] 