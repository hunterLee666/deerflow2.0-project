"""
案例 16: DeerFlow 2.0 缓存优化
完整代码示例 - Redis、内存缓存、缓存策略
"""

from deerflow.client import DeerFlowClient
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import json
import time
from functools import wraps


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    created_at: datetime
    expires_at: datetime
    access_count: int = 0
    last_accessed: datetime = None


class MemoryCache:
    """内存缓存"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }
    
    def _generate_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        entry = self.cache.get(key)
        
        if not entry:
            self.stats["misses"] += 1
            return None
        
        # 检查过期
        if datetime.now() > entry.expires_at:
            del self.cache[key]
            self.stats["misses"] += 1
            return None
        
        # 更新访问统计
        entry.access_count += 1
        entry.last_accessed = datetime.now()
        self.stats["hits"] += 1
        
        return entry.value
    
    def set(self, key: str, value: Any, ttl: int = None):
        """设置缓存"""
        # 检查是否需要淘汰
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        ttl = ttl or self.default_ttl
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=ttl)
        )
        
        self.cache[key] = entry
    
    def delete(self, key: str):
        """删除缓存"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
    
    def _evict_oldest(self):
        """淘汰最旧的条目"""
        if not self.cache:
            return
        
        # 找到最少访问且最旧的条目
        oldest = min(self.cache.values(), key=lambda e: (e.access_count, e.created_at))
        del self.cache[oldest.key]
        self.stats["evictions"] += 1
    
    def get_stats(self) -> Dict:
        """获取缓存统计"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0
        
        return {
            **self.stats,
            "hit_rate": hit_rate,
            "size": len(self.cache),
            "max_size": self.max_size
        }


class RedisCache:
    """Redis 缓存（模拟实现）"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.connected = False
        # 实际实现需要 redis-py 库
        try:
            import redis
            self.client = redis.from_url(redis_url)
            self.connected = True
        except ImportError:
            print("Redis not available, using memory cache fallback")
            self.client = None
    
    def get(self, key: str) -> Optional[Any]:
        """从 Redis 获取"""
        if not self.connected or not self.client:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"Redis get error: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """设置到 Redis"""
        if not self.connected or not self.client:
            return
        
        try:
            self.client.setex(key, ttl, json.dumps(value))
        except Exception as e:
            print(f"Redis set error: {e}")
    
    def delete(self, key: str):
        """从 Redis 删除"""
        if not self.connected or not self.client:
            return
        
        try:
            self.client.delete(key)
        except Exception as e:
            print(f"Redis delete error: {e}")


class CachedDeerFlowClient:
    """带缓存的 DeerFlow 客户端"""
    
    def __init__(
        self,
        memory_cache_size: int = 1000,
        memory_ttl: int = 3600,
        redis_url: str = None
    ):
        self.client = DeerFlowClient()
        self.memory_cache = MemoryCache(max_size=memory_cache_size, default_ttl=memory_ttl)
        self.redis_cache = RedisCache(redis_url) if redis_url else None
        
        # 缓存配置
        self.cache_config = {
            "exact_match": True,  # 完全匹配缓存
            "semantic_cache": False,  # 语义缓存（需要向量数据库）
            "ttl": {
                "chat": 3600,  # 对话缓存1小时
                "stream": 300,  # 流式缓存5分钟
                "models": 86400  # 模型列表缓存24小时
            }
        }
    
    def _generate_cache_key(self, method: str, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = {
            "method": method,
            "args": args,
            "kwargs": {k: v for k, v in kwargs.items() if k not in ['thread_id']}
        }
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
    
    def chat(self, message: str, **kwargs) -> str:
        """带缓存的对话"""
        # 生成缓存键
        cache_key = self._generate_cache_key("chat", message, **kwargs)
        
        # 尝试从缓存获取
        # 1. 先查内存
        cached = self.memory_cache.get(cache_key)
        if cached:
            print(f"[内存缓存命中] {message[:30]}...")
            return cached
        
        # 2. 再查 Redis
        if self.redis_cache:
            cached = self.redis_cache.get(cache_key)
            if cached:
                print(f"[Redis缓存命中] {message[:30]}...")
                # 回填内存缓存
                self.memory_cache.set(cache_key, cached, self.cache_config["ttl"]["chat"])
                return cached
        
        # 3. 执行实际请求
        print(f"[缓存未命中] 执行请求...")
        response = self.client.chat(message, **kwargs)
        
        # 4. 写入缓存
        ttl = self.cache_config["ttl"]["chat"]
        self.memory_cache.set(cache_key, response, ttl)
        if self.redis_cache:
            self.redis_cache.set(cache_key, response, ttl)
        
        return response
    
    def stream(self, message: str, **kwargs):
        """带缓存的流式对话"""
        # 流式输出通常不缓存，但这里演示缓存机制
        cache_key = self._generate_cache_key("stream", message, **kwargs)
        
        # 尝试获取缓存的完整响应
        cached = self.memory_cache.get(cache_key)
        if cached and isinstance(cached, list):
            print(f"[流式缓存命中] {message[:30]}...")
            for item in cached:
                yield item
            return
        
        # 执行流式请求并缓存结果
        results = []
        for event in self.client.stream(message, **kwargs):
            results.append(event)
            yield event
        
        # 缓存结果
        self.memory_cache.set(cache_key, results, self.cache_config["ttl"]["stream"])
    
    def list_models(self) -> Dict:
        """带缓存的模型列表"""
        cache_key = "models:list"
        
        cached = self.memory_cache.get(cache_key)
        if cached:
            return cached
        
        models = self.client.list_models()
        self.memory_cache.set(cache_key, models, self.cache_config["ttl"]["models"])
        
        return models
    
    def invalidate_cache(self, pattern: str = None):
        """使缓存失效"""
        if pattern:
            # 删除匹配的键
            keys_to_delete = [k for k in self.memory_cache.cache.keys() if pattern in k]
            for key in keys_to_delete:
                self.memory_cache.delete(key)
                if self.redis_cache:
                    self.redis_cache.delete(key)
        else:
            # 清空所有缓存
            self.memory_cache.clear()
    
    def get_cache_stats(self) -> Dict:
        """获取缓存统计"""
        return {
            "memory": self.memory_cache.get_stats(),
            "redis": {"connected": self.redis_cache.connected if self.redis_cache else False}
        }


def cache_decorator(ttl: int = 3600):
    """缓存装饰器"""
    def decorator(func: Callable):
        cache = MemoryCache()
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # 尝试获取缓存
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 缓存结果
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


# 使用示例
def demonstrate_cache():
    """演示缓存系统"""
    
    print("=" * 60)
    print("DeerFlow 2.0 缓存优化演示")
    print("=" * 60)
    
    # 创建带缓存的客户端
    cached_client = CachedDeerFlowClient(
        memory_cache_size=100,
        memory_ttl=3600
    )
    
    # 测试缓存
    print("\n1. 测试缓存机制")
    query = "什么是机器学习？"
    
    # 第一次请求（缓存未命中）
    print(f"\n第一次请求: {query}")
    start = time.time()
    response1 = cached_client.chat(query)
    duration1 = time.time() - start
    print(f"耗时: {duration1:.2f}s")
    
    # 第二次请求（缓存命中）
    print(f"\n第二次请求（相同）: {query}")
    start = time.time()
    response2 = cached_client.chat(query)
    duration2 = time.time() - start
    print(f"耗时: {duration2:.2f}s")
    print(f"缓存加速: {duration1/duration2:.1f}x")
    
    # 查看缓存统计
    print("\n2. 缓存统计")
    stats = cached_client.get_cache_stats()
    print(json.dumps(stats, indent=2))
    
    # 测试模型列表缓存
    print("\n3. 模型列表缓存")
    models1 = cached_client.list_models()
    print(f"首次获取: {len(models1.get('models', []))} 个模型")
    
    models2 = cached_client.list_models()
    print(f"缓存获取: {len(models2.get('models', []))} 个模型")


if __name__ == "__main__":
    demonstrate_cache()
