"""
案例 1: DeerFlow 2.0 基础客户端使用
完整代码示例
"""

from deerflow.client import DeerFlowClient, StreamEvent


def basic_usage():
    """基础使用示例"""
    
    # 初始化客户端（使用默认配置）
    client = DeerFlowClient()
    
    # 简单对话 - 返回字符串
    response = client.chat("你好，请介绍一下 DeerFlow")
    print(f"响应: {response}")
    
    # 带 thread_id 的多轮对话
    thread_id = "my-conversation-001"
    
    # 第一轮
    response1 = client.chat("什么是量子计算？", thread_id=thread_id)
    print(f"第一轮: {response1}")
    
    # 第二轮（会记住上下文）
    response2 = client.chat("它有哪些应用场景？", thread_id=thread_id)
    print(f"第二轮: {response2}")


def streaming_usage():
    """流式输出示例"""
    
    client = DeerFlowClient()
    
    print("流式输出示例:")
    print("-" * 50)
    
    # 流式对话
    for event in client.stream("请写一首关于AI的诗", thread_id="stream-test"):
        if event.type == "messages-tuple":
            # AI 消息
            if event.data.get("type") == "ai":
                content = event.data.get("content", "")
                if content:
                    print(content, end="", flush=True)
                    
            # 工具调用
            elif event.data.get("type") == "ai" and "tool_calls" in event.data:
                print(f"\n[工具调用: {event.data['tool_calls']}]")
                
            # 工具结果
            elif event.data.get("type") == "tool":
                print(f"\n[工具结果: {event.data.get('name')} - {event.data.get('content', '')[:100]}...]")
                
        elif event.type == "values":
            # 完整状态快照
            print(f"\n[状态更新: {len(event.data.get('messages', []))} 条消息]")
            
        elif event.type == "end":
            print("\n[对话结束]")


if __name__ == "__main__":
    basic_usage()
    print("\n" + "=" * 50 + "\n")
    streaming_usage()
