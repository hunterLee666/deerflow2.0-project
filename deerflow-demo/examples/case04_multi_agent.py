"""
案例 4: DeerFlow 2.0 多 Agent 协作系统
完整代码示例
"""

from deerflow.client import DeerFlowClient
from typing import List, Dict, Any
import asyncio
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor


@dataclass
class AgentConfig:
    """Agent 配置"""
    name: str
    model_name: str
    system_prompt: str
    tools: List[str]
    thinking_enabled: bool = True


class MultiAgentSystem:
    """
    多 Agent 协作系统
    使用 DeerFlow 2.0 的 subagent 功能
    """
    
    def __init__(self):
        self.client = DeerFlowClient(
            subagent_enabled=True,  # 启用子代理
            plan_mode=True
        )
        
        # 定义专业 Agent
        self.agents = {
            "researcher": AgentConfig(
                name="研究员",
                model_name="gpt-4",
                system_prompt="你是一个专业的研究员，擅长深度研究和技术分析。使用搜索工具收集最新信息。",
                tools=["web_search", "crawler", "python_repl"],
                thinking_enabled=True
            ),
            "writer": AgentConfig(
                name="写作者",
                model_name="gpt-4",
                system_prompt="你是一个专业的技术写作者，擅长将复杂技术转化为清晰的文档。",
                tools=["file_read", "file_write"],
                thinking_enabled=False
            ),
            "reviewer": AgentConfig(
                name="审核员",
                model_name="claude-3",
                system_prompt="你是一个严格的内容审核员，负责检查报告的准确性、完整性和可读性。",
                tools=["file_read"],
                thinking_enabled=True
            ),
            "coder": AgentConfig(
                name="程序员",
                model_name="gpt-4",
                system_prompt="你是一个专业的程序员，擅长编写和调试代码。",
                tools=["bash", "python_repl", "file_write"],
                thinking_enabled=False
            )
        }
    
    async def research_phase(self, topic: str, thread_id: str) -> Dict[str, Any]:
        """
        研究阶段 - 收集信息
        """
        print(f"[研究员] 开始研究: {topic}")
        
        loop = asyncio.get_event_loop()
        
        prompt = f"""
        请深入研究以下主题: {topic}
        
        任务:
        1. 搜索最新的相关资料（至少5个来源）
        2. 分析关键技术点
        3. 整理成结构化的研究笔记
        4. 列出重要的参考文献
        
        请使用 web_search 和 crawler 工具获取信息。
        """
        
        research_result = await loop.run_in_executor(
            None,
            lambda: self.client.chat(prompt, thread_id=f"{thread_id}-research")
        )
        
        print(f"[研究员] 研究完成")
        return {
            "phase": "research",
            "content": research_result,
            "agent": "researcher"
        }
    
    async def coding_phase(self, requirements: str, thread_id: str) -> Dict[str, Any]:
        """
        编程阶段 - 实现代码
        """
        print(f"[程序员] 开始编程")
        
        loop = asyncio.get_event_loop()
        
        prompt = f"""
        请根据以下需求编写代码:
        {requirements}
        
        要求:
        1. 代码要完整、可运行
        2. 添加必要的注释
        3. 包含错误处理
        4. 提供使用示例
        
        请使用 python_repl 工具验证代码。
        """
        
        response = await loop.run_in_executor(
            None,
            lambda: self.client.chat(prompt, thread_id=f"{thread_id}-coding")
        )
        
        print(f"[程序员] 编程完成")
        return {
            "phase": "coding",
            "content": response,
            "agent": "coder"
        }
    
    async def writing_phase(self, research_result: str, thread_id: str) -> Dict[str, Any]:
        """
        写作阶段 - 生成文档
        """
        print(f"[写作者] 开始写作")
        
        loop = asyncio.get_event_loop()
        
        prompt = f"""
        基于以下研究笔记，撰写一份专业的技术报告:
        
        {research_result}
        
        报告结构:
        1. 执行摘要
        2. 背景介绍
        3. 技术分析
        4. 应用场景
        5. 结论与建议
        
        要求:
        - 语言专业但易懂
        - 结构清晰
        - 适当使用图表建议
        """
        
        response = await loop.run_in_executor(
            None,
            lambda: self.client.chat(prompt, thread_id=f"{thread_id}-writing")
        )
        
        print(f"[写作者] 写作完成")
        return {
            "phase": "writing",
            "content": response,
            "agent": "writer"
        }
    
    async def review_phase(self, document: str, thread_id: str) -> Dict[str, Any]:
        """
        审核阶段 - 质量检查
        """
        print(f"[审核员] 开始审核")
        
        loop = asyncio.get_event_loop()
        
        prompt = f"""
        请审核以下技术报告:
        
        {document}
        
        审核清单:
        1. 内容准确性 - 技术概念是否正确？
        2. 结构完整性 - 是否包含所有必要部分？
        3. 逻辑连贯性 - 论述是否清晰连贯？
        4. 语言表达 - 是否有语法或用词问题？
        5. 改进建议 - 如何提升报告质量？
        
        请给出详细的审核意见。
        """
        
        response = await loop.run_in_executor(
            None,
            lambda: self.client.chat(prompt, thread_id=f"{thread_id}-review")
        )
        
        print(f"[审核员] 审核完成")
        return {
            "phase": "review",
            "content": response,
            "agent": "reviewer"
        }
    
    async def execute_workflow(self, topic: str) -> Dict[str, Any]:
        """
        执行完整的工作流
        """
        thread_id = f"workflow-{hash(topic) % 10000}"
        
        print(f"\n{'='*60}")
        print(f"开始多 Agent 协作工作流: {topic}")
        print(f"{'='*60}\n")
        
        # 阶段 1: 研究
        research_result = await self.research_phase(topic, thread_id)
        
        # 阶段 2: 写作（依赖研究结果）
        writing_result = await self.writing_phase(research_result["content"], thread_id)
        
        # 阶段 3: 审核（依赖写作结果）
        review_result = await self.review_phase(writing_result["content"], thread_id)
        
        # 并行执行编程任务（不依赖其他阶段）
        coding_result = await self.coding_phase(
            f"实现一个与 {topic} 相关的 Python 示例程序",
            thread_id
        )
        
        print(f"\n{'='*60}")
        print("工作流完成")
        print(f"{'='*60}\n")
        
        return {
            "topic": topic,
            "thread_id": thread_id,
            "phases": [
                research_result,
                writing_result,
                review_result,
                coding_result
            ],
            "final_report": writing_result["content"],
            "code_example": coding_result["content"],
            "review_feedback": review_result["content"]
        }


# 使用示例
async def main():
    system = MultiAgentSystem()
    
    result = await system.execute_workflow(
        "量子计算在密码学中的应用"
    )
    
    print("\n最终报告:")
    print(result["final_report"][:500] + "...")
    
    print("\n代码示例:")
    print(result["code_example"][:500] + "...")
    
    print("\n审核反馈:")
    print(result["review_feedback"][:500] + "...")


if __name__ == "__main__":
    asyncio.run(main())
