"""
案例 17: DeerFlow 2.0 分布式部署
完整代码示例 - 服务发现、负载均衡、熔断器
"""

from deerflow.client import DeerFlowClient
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import random
import time
import asyncio


@dataclass
class ServiceInstance:
    """服务实例"""
    id: str
    host: str
    port: int
    weight: int = 1
    healthy: bool = True
    last_heartbeat: datetime = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.last_heartbeat is None:
            self.last_heartbeat = datetime.now()
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def address(self) -> str:
        return f"{self.host}:{self.port}"


class ServiceRegistry:
    """服务注册中心"""
    
    def __init__(self):
        self.services: Dict[str, List[ServiceInstance]] = {}
        self.heartbeat_timeout = 30  # 秒
    
    def register(self, service_name: str, instance: ServiceInstance):
        """注册服务"""
        if service_name not in self.services:
            self.services[service_name] = []
        
        # 检查是否已存在
        existing = [i for i in self.services[service_name] if i.id == instance.id]
        if existing:
            existing[0].last_heartbeat = datetime.now()
            existing[0].healthy = True
        else:
            self.services[service_name].append(instance)
        
        print(f"服务注册: {service_name} - {instance.address}")
    
    def deregister(self, service_name: str, instance_id: str):
        """注销服务"""
        if service_name in self.services:
            self.services[service_name] = [
                i for i in self.services[service_name] 
                if i.id != instance_id
            ]
    
    def discover(self, service_name: str) -> List[ServiceInstance]:
        """发现服务"""
        instances = self.services.get(service_name, [])
        # 过滤健康实例
        return [i for i in instances if i.healthy]
    
    def heartbeat(self, service_name: str, instance_id: str):
        """心跳检测"""
        if service_name in self.services:
            for instance in self.services[service_name]:
                if instance.id == instance_id:
                    instance.last_heartbeat = datetime.now()
                    instance.healthy = True
                    return True
        return False
    
    def check_health(self):
        """健康检查"""
        now = datetime.now()
        for service_name, instances in self.services.items():
            for instance in instances:
                if (now - instance.last_heartbeat).seconds > self.heartbeat_timeout:
                    instance.healthy = False
                    print(f"服务不健康: {service_name} - {instance.address}")


class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.current_index = 0
    
    def round_robin(self, service_name: str) -> Optional[ServiceInstance]:
        """轮询算法"""
        instances = self.registry.discover(service_name)
        if not instances:
            return None
        
        instance = instances[self.current_index % len(instances)]
        self.current_index += 1
        return instance
    
    def random_select(self, service_name: str) -> Optional[ServiceInstance]:
        """随机选择"""
        instances = self.registry.discover(service_name)
        if not instances:
            return None
        return random.choice(instances)
    
    def weighted_random(self, service_name: str) -> Optional[ServiceInstance]:
        """加权随机"""
        instances = self.registry.discover(service_name)
        if not instances:
            return None
        
        total_weight = sum(i.weight for i in instances)
        r = random.uniform(0, total_weight)
        
        current_weight = 0
        for instance in instances:
            current_weight += instance.weight
            if r <= current_weight:
                return instance
        
        return instances[-1]
    
    def least_connections(self, service_name: str, connections: Dict[str, int]) -> Optional[ServiceInstance]:
        """最少连接数"""
        instances = self.registry.discover(service_name)
        if not instances:
            return None
        
        return min(instances, key=lambda i: connections.get(i.id, 0))


class CircuitBreaker:
    """熔断器"""
    
    STATE_CLOSED = "closed"      # 正常
    STATE_OPEN = "open"          # 熔断
    STATE_HALF_OPEN = "half_open"  # 半开
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        half_open_max_calls: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.state = self.STATE_CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.half_open_calls = 0
    
    def can_execute(self) -> bool:
        """检查是否可以执行"""
        if self.state == self.STATE_CLOSED:
            return True
        
        if self.state == self.STATE_OPEN:
            if self._should_attempt_reset():
                self.state = self.STATE_HALF_OPEN
                self.half_open_calls = 0
                return True
            return False
        
        if self.state == self.STATE_HALF_OPEN:
            if self.half_open_calls < self.half_open_max_calls:
                self.half_open_calls += 1
                return True
            return False
        
        return True
    
    def _should_attempt_reset(self) -> bool:
        """检查是否应该尝试重置"""
        if self.last_failure_time is None:
            return True
        return (datetime.now() - self.last_failure_time).seconds >= self.recovery_timeout
    
    def record_success(self):
        """记录成功"""
        if self.state == self.STATE_HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.half_open_max_calls:
                self._reset()
        else:
            self.failure_count = 0
    
    def record_failure(self):
        """记录失败"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == self.STATE_HALF_OPEN:
            self.state = self.STATE_OPEN
        elif self.failure_count >= self.failure_threshold:
            self.state = self.STATE_OPEN
    
    def _reset(self):
        """重置熔断器"""
        self.state = self.STATE_CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.half_open_calls = 0
        self.last_failure_time = None


class DistributedDeerFlowClient:
    """分布式 DeerFlow 客户端"""
    
    def __init__(self, registry: ServiceRegistry, load_balancer: LoadBalancer):
        self.registry = registry
        self.load_balancer = load_balancer
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.connections: Dict[str, int] = {}  # 连接数统计
    
    def _get_circuit_breaker(self, instance_id: str) -> CircuitBreaker:
        """获取熔断器"""
        if instance_id not in self.circuit_breakers:
            self.circuit_breakers[instance_id] = CircuitBreaker()
        return self.circuit_breakers[instance_id]
    
    def _call_remote(self, instance: ServiceInstance, message: str) -> str:
        """调用远程服务（模拟）"""
        # 实际实现应该使用 HTTP/gRPC 调用
        # 这里模拟远程调用
        time.sleep(0.1)  # 模拟网络延迟
        
        if random.random() < 0.1:  # 10% 失败率
            raise Exception("Remote service error")
        
        return f"[Remote:{instance.address}] Response to: {message[:30]}..."
    
    def chat(self, message: str, **kwargs) -> str:
        """分布式对话"""
        service_name = "deerflow-service"
        
        # 选择实例
        instance = self.load_balancer.weighted_random(service_name)
        if not instance:
            raise Exception("No available service instance")
        
        # 检查熔断器
        cb = self._get_circuit_breaker(instance.id)
        if not cb.can_execute():
            # 尝试其他实例
            instances = self.registry.discover(service_name)
            for inst in instances:
                if inst.id != instance.id:
                    cb = self._get_circuit_breaker(inst.id)
                    if cb.can_execute():
                        instance = inst
                        break
            else:
                raise Exception("Circuit breaker open for all instances")
        
        # 记录连接数
        self.connections[instance.id] = self.connections.get(instance.id, 0) + 1
        
        try:
            # 执行调用
            response = self._call_remote(instance, message)
            cb.record_success()
            return response
            
        except Exception as e:
            cb.record_failure()
            raise e
        finally:
            self.connections[instance.id] -= 1


# 使用示例
def demonstrate_distributed():
    """演示分布式部署"""
    
    print("=" * 60)
    print("DeerFlow 2.0 分布式部署演示")
    print("=" * 60)
    
    # 创建服务注册中心
    registry = ServiceRegistry()
    
    # 注册多个服务实例
    print("\n1. 注册服务实例")
    for i in range(3):
        instance = ServiceInstance(
            id=f"deerflow-{i+1}",
            host="localhost",
            port=8000 + i,
            weight=random.randint(1, 5)
        )
        registry.register("deerflow-service", instance)
    
    # 创建负载均衡器
    load_balancer = LoadBalancer(registry)
    
    # 创建分布式客户端
    client = DistributedDeerFlowClient(registry, load_balancer)
    
    # 模拟请求
    print("\n2. 模拟请求")
    for i in range(10):
        try:
            response = client.chat(f"测试消息 {i+1}")
            print(f"请求 {i+1}: {response}")
        except Exception as e:
            print(f"请求 {i+1} 失败: {e}")
    
    # 健康检查
    print("\n3. 健康检查")
    registry.check_health()
    
    print("\n4. 服务状态")
    instances = registry.discover("deerflow-service")
    print(f"健康实例数: {len(instances)}")


if __name__ == "__main__":
    demonstrate_distributed()
