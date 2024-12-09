"""
AI配对编程助手测试
--------------
测试代理类的核心功能。
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from ai_pair_programming import create_agent

@pytest.fixture
def temp_workspace():
    """创建临时工作空间"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture
def agent(temp_workspace):
    """创建测试用的代理实例"""
    return create_agent(
        workspace_path=str(temp_workspace),
        model_name="shibing624/text2vec-base-chinese"
    )

def test_agent_initialization(agent):
    """测试代理初始化"""
    assert agent is not None
    assert agent.workspace_path is not None
    assert agent.embedding_manager is not None
    assert agent.memory_system is not None
    assert agent.knowledge_base is not None

def test_add_memory(agent):
    """测试添加记忆"""
    memory = agent.add_memory(
        "测试记忆内容",
        "test",
        {"test_meta": "value"}
    )
    assert memory is not None
    assert memory.content == "测试记忆内容"
    assert memory.type == "test"
    assert memory.metadata == {"test_meta": "value"}

def test_generate_response(agent):
    """测试生成响应"""
    # 添加一些测试记忆
    agent.add_memory(
        "我们正在开发一个Python项目",
        "conversation"
    )
    
    # 生成响应
    response = agent.generate_response(
        "如何开始项目开发？",
        context={"language": "python"}
    )
    
    assert isinstance(response, str)
    assert len(response) > 0

def test_conversation_history(agent):
    """测试对话历史"""
    # 进行一些对话
    agent.generate_response("第一条消息")
    agent.generate_response("第二条消息")
    
    # 获取历史
    history = agent.get_conversation_history()
    assert len(history) == 4  # 两条用户消息和两条助手响应
    
    # 测试限制
    limited_history = agent.get_conversation_history(limit=2)
    assert len(limited_history) == 2

def test_workspace_scanning(agent, temp_workspace):
    """测试工作空间扫描"""
    # 创建测试文件
    md_file = temp_workspace / "test.md"
    md_file.write_text("# 测试文档\n这是一个测试文档。")
    
    py_file = temp_workspace / "test.py"
    py_file.write_text('"""测试模块"""\n\ndef test_function():\n    pass')
    
    # 扫描工作空间
    stats = agent.scan_workspace()
    assert isinstance(stats, str)
    assert "总条目数" in stats

def test_state_saving_loading(agent, temp_workspace):
    """测试状态保存和加载"""
    # 添加一些测试数据
    agent.add_memory("测试记忆", "test")
    agent.generate_response("测试消息")
    
    # 保存状态
    state_dir = temp_workspace / "state"
    agent.save_state(str(state_dir))
    
    # 创建新实例并加载状态
    new_agent = create_agent(
        workspace_path=str(temp_workspace),
        load_state_from=str(state_dir)
    )
    
    # 验证状态恢复
    assert len(new_agent.conversation_history) == len(agent.conversation_history)
    assert len(new_agent.memory_system.memories) == len(agent.memory_system.memories)

def test_knowledge_base_operations(agent, temp_workspace):
    """测试知识库操作"""
    # 创建测试文档
    docs_dir = temp_workspace / "docs"
    docs_dir.mkdir()
    
    test_doc = docs_dir / "test.md"
    test_doc.write_text("""
    # 测试文档
    这是一个测试文档。
    
    tags: test, documentation
    """)
    
    # 扫描文档
    agent.scan_workspace()
    
    # 查询知识库
    results = agent.knowledge_base.query("测试文档")
    assert len(results) > 0
    
    # 验证知识条目
    item, score = results[0]
    assert item.title == "测试文档"
    assert "test" in item.tags

def test_error_handling(agent):
    """测试错误处理"""
    # 测试无效的工作空间路径
    with pytest.raises(ValueError):
        agent.set_workspace("")
        agent.scan_workspace()
    
    # 测试加载不存在的状态
    with pytest.raises(FileNotFoundError):
        agent.load_state("/nonexistent/path")

if __name__ == "__main__":
    pytest.main([__file__]) 