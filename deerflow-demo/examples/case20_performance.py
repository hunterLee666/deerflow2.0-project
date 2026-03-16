"""
案例 20: DeerFlow 2.0 性能优化技巧
完整代码示例 - 连接池、批量处理、异步优化、内存管理
"""

import asyncio
import time
import functools
from typing import List, Dict, Any, Optional, Callable, Coroutine
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from collections import deque
import gc
import psutil
import os

from deerflow.client import DeerFlowClient, StreamEvent


@dataclass
class PerformanceMetrics:
    """性能指标"""
    total_requests: int = 0
    total_latency: float = 0
    min_latency: float = float('inf')
    max_latency: float = 0
    active_connections: int = 0
    queue_size: int = 0
    memory_usage_mb: float = 0


class ConnectionPool:
    """DeerFlow 客户端连接池"""
    
    def __init__(
        self,
        pool_size: int = 10,
        max_overflow: int = 5,
        timeout: float = 30.0,
        recycle: int = 3600
    ):
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.timeout = timeout
        self.recycle = recycle
        
        self._pool: deque = deque()
        self._overflow: int = 0
        self._in_use: set = set()
        self._lock = asyncio.Lock()
        self._semaphore = asyncio.Semaphore(pool_size + max_overflow)
        self._metrics = PerformanceMetrics()
        
        # 预创建客户端
        self._initialize_pool()
    
    def _initialize_pool(self):
        """初始化连接池"""
        for _ in range(self.pool_size):
            client = DeerFlowClient()
            self._pool.append({
                'client': client,
                'created_at': time.time(),
                'use_count': 0
            })
    
    async def acquire(self) -> DeerFlowClient:
        """获取连接"""
        async with self._semaphore:
            async with self._lock:
                if self._pool:
                    conn = self._pool.popleft()
                    conn['use_count'] += 1
                    self._in_use.add(id(conn))
                    self._metrics.active_connections = len(self._in_use)
                    return conn['client']
                
                if self._overflow < self.max_overflow:
                    self._overflow += 1
                    client = DeerFlowClient()
                    conn = {
                        'client': client,
                        'created_at': time.time(),
                        'use_count': 1
                    }
                    self._in_use.add(id(conn))
                    self._metrics.active_connections = len(self._in_use)
                    return client
                
                raise Exception("Connection pool exhausted")
    
    async def release(self, client: DeerFlowClient):
        """释放连接"""
        async with self._lock:
            # 找到对应的连接
            for conn in list(self._pool):
                if conn['client'] is client:
                    self._in_use.discard(id(conn))
                    # 检查是否需要回收
                    if time.time() - conn['created_at'] > self.recycle:
                        # 创建新连接替换
                        conn['client'] = DeerFlowClient()
                        conn['created_at'] = time.time()
                        conn['use_count'] = 0
                    self._pool.append(conn)
                    self._metrics.active_connections = len(self._in_use)
                    return
            
            # 溢出连接直接丢弃
            self._overflow -= 1
            self._metrics.active_connections = len(self._in_use)
    
    async def execute(
        self,
        func: Callable[[DeerFlowClient], Any],
        *args,
        **kwargs
    ) -> Any:
        """执行操作"""
        client = await self.acquire()
        try:
            start = time.time()
            result = await func(client, *args, **kwargs)
            latency = time.time() - start
            
            # 更新指标
            self._metrics.total_requests += 1
            self._metrics.total_latency += latency
            self._metrics.min_latency = min(self._metrics.min_latency, latency)
            self._metrics.max_latency = max(self._metrics.max_latency, latency)
            
            return result
        finally:
            await self.release(client)
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        avg_latency = (
            self._metrics.total_latency / self._metrics.total_requests
            if self._metrics.total_requests > 0 else 0
        )
        
        return {
            'pool_size': self.pool_size,
            'available': len(self._pool),
            'in_use': len(self._in_use),
            'overflow': self._overflow,
            'total_requests': self._metrics.total_requests,
            'avg_latency_ms': avg_latency * 1000,
            'min_latency_ms': self._metrics.min_latency * 1000,
            'max_latency_ms': self._metrics.max_latency * 1000
        }


class BatchProcessor:
    """批量处理器"""
    
    def __init__(
        self,
        pool: ConnectionPool,
        batch_size: int = 10,
        max_wait_time: float = 1.0
    ):
        self.pool = pool
        self.batch_size = batch_size
        self.max_wait_time = max_wait_time
        
        self._queue: asyncio.Queue = asyncio.Queue()
        self._results: Dict[str, Any] = {}
        self._processing = False
        self._lock = asyncio.Lock()
    
    async def submit(self, item: Dict[str, Any]) -> str:
        """提交任务"""
        request_id = f"req_{time.time()}_{id(item)}"
        item['request_id'] = request_id
        item['future'] = asyncio.Future()
        
        await self._queue.put(item)
        
        # 启动批处理
        if not self._processing:
            asyncio.create_task(self._process_batch())
        
        # 等待结果
        return await item['future']
    
    async def _process_batch(self):
        """处理批次"""
        self._processing = True
        
        try:
            while not self._queue.empty():
                batch = []
                start_time = time.time()
                
                # 收集批次
                while len(batch) < self.batch_size:
                    try:
                        timeout = max(0, self.max_wait_time - (time.time() - start_time))
                        item = await asyncio.wait_for(
                            self._queue.get(),
                            timeout=timeout
                        )
                        batch.append(item)
                    except asyncio.TimeoutError:
                        break
                
                if batch:
                    await self._execute_batch(batch)
        
        finally:
            self._processing = False
    
    async def _execute_batch(self, batch: List[Dict]):
        """执行批次"""
        async def process_item(client: DeerFlowClient, item: Dict):
            try:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: client.chat(
                        item['message'],
                        thread_id=item.get('thread_id')
                    )
                )
                item['future'].set_result(response)
            except Exception as e:
                item['future'].set_exception(e)
        
        # 并发处理批次中的所有项目
        tasks = [
            self.pool.execute(process_item, item)
            for item in batch
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)


class AsyncOptimizer:
    """异步优化器"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.semaphore = asyncio.Semaphore(max_workers * 2)
    
    async def run_sync(self, func: Callable, *args, **kwargs) -> Any:
        """在线程池中运行同步函数"""
        async with self.semaphore:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                self.executor,
                functools.partial(func, *args, **kwargs)
            )
    
    async def parallel_map(
        self,
        func: Callable,
        items: List[Any],
        max_concurrency: int = None
    ) -> List[Any]:
        """并行映射"""
        semaphore = asyncio.Semaphore(max_concurrency or self.max_workers)
        
        async def wrapped(item):
            async with semaphore:
                return await self.run_sync(func, item)
        
        tasks = [wrapped(item) for item in items]
        return await asyncio.gather(*tasks)
    
    async def chunked_parallel(
        self,
        func: Callable,
        items: List[Any],
        chunk_size: int = 10
    ) -> List[Any]:
        """分块并行处理"""
        results = []
        
        for i in range(0, len(items), chunk_size):
            chunk = items[i:i + chunk_size]
            chunk_results = await self.parallel_map(func, chunk)
            results.extend(chunk_results)
            
            # 给系统一些喘息时间
            await asyncio.sleep(0.01)
        
        return results


class MemoryManager:
    """内存管理器"""
    
    def __init__(self, max_memory_mb: float = 1024):
        self.max_memory_mb = max_memory_mb
        self.gc_threshold = max_memory_mb * 0.8
    
    def get_memory_usage(self) -> float:
        """获取当前内存使用（MB）"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    def should_gc(self) -> bool:
        """是否应该执行垃圾回收"""
        return self.get_memory_usage() > self.gc_threshold
    
    async def optimize(self):
        """执行内存优化"""
        if self.should_gc():
            print(f"Memory usage: {self.get_memory_usage():.2f} MB, running GC...")
            
            # 强制垃圾回收
            gc.collect()
            
            # 如果有 psutil，可以尝试释放内存
            if hasattr(psutil.Process(os.getpid()), 'memory_maps'):
                try:
                    psutil.Process(os.getpid()).memory_maps()
                except:
                    pass
            
            print(f"Memory after GC: {self.get_memory_usage():.2f} MB")
    
    def monitor(self, interval: int = 60):
        """启动内存监控"""
        async def monitor_loop():
            while True:
                await asyncio.sleep(interval)
                await self.optimize()
        
        asyncio.create_task(monitor_loop())


class PerformanceOptimizer:
    """性能优化器 - 整合所有优化策略"""
    
    def __init__(
        self,
        pool_size: int = 10,
        batch_size: int = 10,
        max_workers: int = 4
    ):
        self.pool = ConnectionPool(pool_size=pool_size)
        self.batch_processor = BatchProcessor(self.pool, batch_size=batch_size)
        self.async_optimizer = AsyncOptimizer(max_workers=max_workers)
        self.memory_manager = MemoryManager()
        
        # 启动内存监控
        self.memory_manager.monitor()
    
    async def optimized_chat(
        self,
        message: str,
        thread_id: Optional[str] = None,
        use_batch: bool = False
    ) -> str:
        """优化的聊天接口"""
        
        if use_batch:
            # 使用批处理
            return await self.batch_processor.submit({
                'message': message,
                'thread_id': thread_id
            })
        else:
            # 使用连接池
            async def do_chat(client: DeerFlowClient):
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(
                    None,
                    lambda: client.chat(message, thread_id=thread_id)
                )
            
            return await self.pool.execute(do_chat)
    
    async def parallel_chats(
        self,
        messages: List[str],
        max_concurrency: int = 5
    ) -> List[str]:
        """并行处理多个聊天"""
        
        async def chat_single(message: str) -> str:
            return await self.optimized_chat(message)
        
        semaphore = asyncio.Semaphore(max_concurrency)
        
        async def wrapped(message: str):
            async with semaphore:
                return await chat_single(message)
        
        tasks = [wrapped(msg) for msg in messages]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stream_with_backpressure(
        self,
        message: str,
        callback: Callable[[str], None],
        max_rate: int = 10  # 每秒最大事件数
    ):
        """带背压控制的流式处理"""
        
        client = await self.pool.acquire()
        try:
            min_interval = 1.0 / max_rate
            last_emit = 0
            
            loop = asyncio.get_event_loop()
            
            def stream_sync():
                return list(client.stream(message))
            
            events = await loop.run_in_executor(None, stream_sync)
            
            for event in events:
                # 背压控制
                now = time.time()
                elapsed = now - last_emit
                if elapsed < min_interval:
                    await asyncio.sleep(min_interval - elapsed)
                
                if event.type == "messages-tuple" and event.data.get("content"):
                    callback(event.data["content"])
                    last_emit = time.time()
        
        finally:
            await self.pool.release(client)
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        return {
            'pool': self.pool.get_metrics(),
            'memory_mb': self.memory_manager.get_memory_usage()
        }


# 性能测试
async def performance_benchmark():
    """性能基准测试"""
    
    print("=" * 60)
    print("DeerFlow 性能优化演示")
    print("=" * 60)
    
    optimizer = PerformanceOptimizer(
        pool_size=5,
        batch_size=3,
        max_workers=4
    )
    
    # 测试 1: 单请求性能
    print("\n测试 1: 单请求性能")
    start = time.time()
    response = await optimizer.optimized_chat("什么是人工智能？")
    single_latency = time.time() - start
    print(f"单请求延迟: {single_latency*1000:.2f} ms")
    print(f"响应: {response[:100]}...")
    
    # 测试 2: 连接池性能
    print("\n测试 2: 连接池性能（10个顺序请求）")
    start = time.time()
    for i in range(10):
        await optimizer.optimized_chat(f"问题 {i+1}: 什么是机器学习？")
    pool_latency = time.time() - start
    print(f"总延迟: {pool_latency*1000:.2f} ms")
    print(f"平均延迟: {pool_latency/10*1000:.2f} ms")
    
    # 测试 3: 并行处理
    print("\n测试 3: 并行处理（5个并发请求）")
    messages = [
        "解释深度学习",
        "什么是神经网络",
        "介绍自然语言处理",
        "计算机视觉概述",
        "强化学习基础"
    ]
    
    start = time.time()
    results = await optimizer.parallel_chats(messages, max_concurrency=5)
    parallel_latency = time.time() - start
    print(f"并行处理延迟: {parallel_latency*1000:.2f} ms")
    print(f"吞吐量: {len(messages)/parallel_latency:.2f} 请求/秒")
    
    # 测试 4: 批量处理
    print("\n测试 4: 批量处理")
    batch_messages = [f"简短问题 {i}" for i in range(6)]
    
    start = time.time()
    batch_results = await asyncio.gather(*[
        optimizer.optimized_chat(msg, use_batch=True)
        for msg in batch_messages
    ])
    batch_latency = time.time() - start
    print(f"批量处理延迟: {batch_latency*1000:.2f} ms")
    
    # 性能指标
    print("\n" + "=" * 60)
    print("性能指标")
    print("=" * 60)
    metrics = optimizer.get_metrics()
    print(json.dumps(metrics, indent=2, default=str))
    
    # 内存使用情况
    print(f"\n内存使用: {metrics['memory_mb']:.2f} MB")


if __name__ == "__main__":
    asyncio.run(performance_benchmark())
