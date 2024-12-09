"""
基本使用示例
----------
展示AI配对编程助手的基本功能。
"""

from ai_pair_programming import create_agent

def main():
    # 创建助手实例
    agent = create_agent(
        workspace_path="./workspace",
        model_name="shibing624/text2vec-base-chinese"
    )
    
    # 扫描工作空间
    print("扫描工作空间...")
    print(agent.scan_workspace())
    
    # 交互示例
    print("\n开始交互...")
    
    # 示例1：项目初始化
    response = agent.generate_response(
        "让我们开始一个新的Python项目，使用TDD方式开发",
        context={
            "os": "windows",
            "env_tool": "venv",
            "language": "中文"
        }
    )
    print("\n用户: 让我们开始一个新的Python项目，使用TDD方式开发")
    print(f"助手: {response}")
    
    # 示例2：功能开发
    response = agent.generate_response(
        "我们需要实现用户认证功能，包括注册和登录",
        context={
            "framework": "flask",
            "database": "sqlite"
        }
    )
    print("\n用户: 我们需要实现用户认证功能，包括注册和登录")
    print(f"助手: {response}")
    
    # 查看统计信息
    print("\n知识库统计:")
    print(agent.get_knowledge_base_stats())
    
    print("\n记忆系统统计:")
    print(agent.get_memory_stats())
    
    # 保存状态
    print("\n保存助手状态...")
    agent.save_state("./agent_state")

if __name__ == "__main__":
    main() 