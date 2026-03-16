"""
案例 2: DeerFlow 2.0 高级配置使用
完整代码示例
"""

from deerflow.client import DeerFlowClient
from langgraph.checkpoint.memory import MemorySaver


def advanced_configuration():
    """高级配置示例"""
    
    # 使用自定义配置路径
    client = DeerFlowClient(
        config_path="./config/custom_config.yaml",  # 自定义配置文件
        checkpointer=MemorySaver(),                    # 内存状态持久化
        model_name="gpt-4",                           # 指定模型
        thinking_enabled=True,                        # 启用扩展思考
        subagent_enabled=True,                        # 启用子代理
        plan_mode=True                                # 启用计划模式
    )
    
    # 查看可用模型
    models = client.list_models()
    print("可用模型:")
    for model in models.get("models", []):
        print(f"  - {model['name']}: {model.get('display_name', 'N/A')}")
        print(f"    支持思考: {model.get('supports_thinking', False)}")
    
    # 查看可用技能
    skills = client.list_skills()
    print("\n可用技能:")
    for skill in skills.get("skills", []):
        print(f"  - {skill['name']}: {skill['description']}")
        print(f"    类别: {skill['category']}, 已启用: {skill['enabled']}")
    
    # 获取特定模型信息
    model_info = client.get_model("gpt-4")
    if model_info:
        print(f"\nGPT-4 信息: {model_info}")
    
    # 获取内存数据
    memory = client.get_memory()
    print(f"\n当前内存: {memory}")
    
    # 使用高级功能进行对话
    response = client.chat(
        "帮我制定一个学习 Python 的计划",
        thread_id="advanced-test",
        model_name="gpt-4",              # 临时覆盖模型
        thinking_enabled=True,           # 启用深度思考
        subagent_enabled=True,           # 允许使用子代理
        plan_mode=True,                  # 启用计划模式
        recursion_limit=150              # 设置递归限制
    )
    print(f"\n响应: {response}")


def reset_agent_example():
    """重置 Agent 示例"""
    
    client = DeerFlowClient()
    
    # 进行一些对话
    client.chat("你好", thread_id="reset-test")
    
    # 修改配置后重置 Agent
    # 例如：安装了新技能、更新了内存等
    client.reset_agent()
    print("Agent 已重置，下次调用将重新创建")


if __name__ == "__main__":
    advanced_configuration()
