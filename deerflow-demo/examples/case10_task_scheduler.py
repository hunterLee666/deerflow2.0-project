"""
案例 10: DeerFlow 2.0 任务调度系统
完整代码示例 - 定时任务、工作流调度
"""

from deerflow.client import DeerFlowClient
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import json
import uuid
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """任务定义"""
    id: str
    name: str
    description: str
    prompt: str
    schedule: Optional[str] = None  # cron 表达式或时间
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    thread_id: Optional[str] = None


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, client: DeerFlowClient = None):
        self.client = client or DeerFlowClient()
        self.tasks: Dict[str, Task] = {}
        self.scheduled_tasks: Dict[str, asyncio.Task] = {}
        self.history: List[Dict] = []
        self.running = False
    
    def create_task(
        self,
        name: str,
        description: str,
        prompt: str,
        schedule: Optional[str] = None,
        max_retries: int = 3
    ) -> Task:
        """创建新任务"""
        task = Task(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            prompt=prompt,
            schedule=schedule,
            max_retries=max_retries,
            thread_id=f"task-{uuid.uuid4().hex[:8]}"
        )
        self.tasks[task.id] = task
        return task
    
    async def execute_task(self, task_id: str) -> Task:
        """执行任务"""
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        task.status = TaskStatus.RUNNING
        task.executed_at = datetime.now()
        
        try:
            # 在后台线程执行 DeerFlow
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.client.chat(
                    task.prompt,
                    thread_id=task.thread_id
                )
            )
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            # 记录历史
            self.history.append({
                "task_id": task.id,
                "name": task.name,
                "status": "completed",
                "executed_at": task.executed_at.isoformat(),
                "result_preview": result[:200] if result else None
            })
            
        except Exception as e:
            task.error = str(e)
            task.retry_count += 1
            
            if task.retry_count < task.max_retries:
                task.status = TaskStatus.PENDING
                # 重试延迟
                await asyncio.sleep(2 ** task.retry_count)
                return await self.execute_task(task_id)
            else:
                task.status = TaskStatus.FAILED
                self.history.append({
                    "task_id": task.id,
                    "name": task.name,
                    "status": "failed",
                    "error": str(e)
                })
        
        return task
    
    def schedule_task(self, task_id: str, run_at: datetime):
        """安排任务在指定时间执行"""
        async def delayed_execution():
            delay = (run_at - datetime.now()).total_seconds()
            if delay > 0:
                await asyncio.sleep(delay)
            await self.execute_task(task_id)
        
        self.scheduled_tasks[task_id] = asyncio.create_task(delayed_execution())
    
    def schedule_recurring(self, task_id: str, interval_seconds: int):
        """安排周期性任务"""
        async def recurring_execution():
            while self.running:
                await self.execute_task(task_id)
                await asyncio.sleep(interval_seconds)
        
        self.scheduled_tasks[task_id] = asyncio.create_task(recurring_execution())
    
    def cancel_task(self, task_id: str):
        """取消任务"""
        if task_id in self.scheduled_tasks:
            self.scheduled_tasks[task_id].cancel()
            del self.scheduled_tasks[task_id]
        
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskStatus.CANCELLED
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        return self.tasks.get(task_id)
    
    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[Task]:
        """列出任务"""
        tasks = list(self.tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        return tasks
    
    def get_history(self) -> List[Dict]:
        """获取执行历史"""
        return self.history
    
    async def start(self):
        """启动调度器"""
        self.running = True
        print("Task scheduler started")
    
    async def stop(self):
        """停止调度器"""
        self.running = False
        for task in self.scheduled_tasks.values():
            task.cancel()
        self.scheduled_tasks.clear()
        print("Task scheduler stopped")


class WorkflowEngine:
    """工作流引擎"""
    
    def __init__(self, scheduler: TaskScheduler):
        self.scheduler = scheduler
    
    def create_workflow(
        self,
        name: str,
        steps: List[Dict[str, Any]]
    ) -> str:
        """创建工作流"""
        workflow_id = str(uuid.uuid4())
        
        # 为每个步骤创建任务
        previous_task_id = None
        for i, step in enumerate(steps):
            task = self.scheduler.create_task(
                name=f"{name}-step-{i+1}",
                description=step.get("description", ""),
                prompt=step.get("prompt", ""),
                max_retries=step.get("max_retries", 3)
            )
            
            # 存储工作流信息
            task.metadata = {
                "workflow_id": workflow_id,
                "step_index": i,
                "previous_task": previous_task_id,
                "next_steps": step.get("next_steps", [])
            }
            
            previous_task_id = task.id
        
        return workflow_id
    
    async def execute_workflow(self, workflow_id: str):
        """执行工作流"""
        # 获取工作流中的所有任务
        workflow_tasks = [
            task for task in self.scheduler.tasks.values()
            if task.metadata.get("workflow_id") == workflow_id
        ]
        
        # 按步骤顺序执行
        workflow_tasks.sort(key=lambda t: t.metadata.get("step_index", 0))
        
        results = []
        for task in workflow_tasks:
            print(f"Executing workflow step: {task.name}")
            result = await self.scheduler.execute_task(task.id)
            results.append(result)
            
            # 如果任务失败，停止工作流
            if result.status == TaskStatus.FAILED:
                print(f"Workflow failed at step: {task.name}")
                break
        
        return results


# 使用示例
async def demonstrate_scheduler():
    """演示任务调度"""
    
    print("=" * 60)
    print("DeerFlow 2.0 任务调度演示")
    print("=" * 60)
    
    # 创建调度器
    scheduler = TaskScheduler()
    await scheduler.start()
    
    # 创建任务
    print("\n1. 创建任务")
    
    task1 = scheduler.create_task(
        name="每日报告生成",
        description="生成每日数据分析报告",
        prompt="请生成一份关于人工智能发展趋势的简要报告",
        schedule="0 9 * * *"  # 每天9点
    )
    print(f"创建任务: {task1.name} (ID: {task1.id[:8]})")
    
    task2 = scheduler.create_task(
        name="代码审查",
        description="审查代码质量",
        prompt="请分析以下代码的质量并提出改进建议:\ndef example():\n    pass",
        max_retries=2
    )
    print(f"创建任务: {task2.name} (ID: {task2.id[:8]})")
    
    # 立即执行任务
    print("\n2. 立即执行任务")
    result = await scheduler.execute_task(task1.id)
    print(f"任务状态: {result.status.value}")
    if result.result:
        print(f"结果预览: {result.result[:200]}...")
    
    # 安排延迟任务
    print("\n3. 安排延迟任务（5秒后执行）")
    run_at = datetime.now() + timedelta(seconds=5)
    scheduler.schedule_task(task2.id, run_at)
    print(f"任务将在 {run_at.strftime('%H:%M:%S')} 执行")
    
    # 等待任务执行
    await asyncio.sleep(6)
    
    # 查看任务状态
    print("\n4. 任务状态")
    for task in scheduler.list_tasks():
        print(f"  - {task.name}: {task.status.value}")
    
    # 查看历史
    print("\n5. 执行历史")
    for record in scheduler.get_history():
        print(f"  - {record['name']}: {record['status']}")
    
    # 工作流示例
    print("\n6. 创建工作流")
    workflow_engine = WorkflowEngine(scheduler)
    
    workflow_id = workflow_engine.create_workflow(
        name="内容创作工作流",
        steps=[
            {
                "description": "研究主题",
                "prompt": "请研究量子计算的最新进展"
            },
            {
                "description": "撰写文章",
                "prompt": "基于研究结果撰写一篇科普文章"
            },
            {
                "description": "审核内容",
                "prompt": "请审核文章的准确性和可读性"
            }
        ]
    )
    print(f"工作流创建: {workflow_id[:8]}")
    
    # 停止调度器
    await scheduler.stop()


if __name__ == "__main__":
    asyncio.run(demonstrate_scheduler())
