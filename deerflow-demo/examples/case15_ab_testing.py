"""
案例 15: DeerFlow 2.0 A/B 测试框架
完整代码示例 - 模型对比、效果评估
"""

from deerflow.client import DeerFlowClient
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import random
import statistics


@dataclass
class Variant:
    """测试变体"""
    id: str
    name: str
    config: Dict[str, Any]
    traffic_percentage: float = 50.0


@dataclass
class Experiment:
    """实验定义"""
    id: str
    name: str
    description: str
    variants: List[Variant]
    status: str = "running"  # 'running', 'paused', 'completed'
    start_date: datetime = None
    end_date: datetime = None
    metrics: List[str] = field(default_factory=list)


@dataclass
class ExperimentResult:
    """实验结果"""
    variant_id: str
    total_requests: int = 0
    total_latency: float = 0
    latencies: List[float] = field(default_factory=list)
    user_satisfaction: List[int] = field(default_factory=list)
    error_count: int = 0


class ABTestFramework:
    """A/B 测试框架"""
    
    def __init__(self):
        self.experiments: Dict[str, Experiment] = {}
        self.results: Dict[str, Dict[str, ExperimentResult]] = {}  # exp_id -> variant_id -> result
        self.user_assignments: Dict[str, str] = {}  # user_id -> variant_id
    
    def create_experiment(
        self,
        name: str,
        description: str,
        variants: List[Variant],
        metrics: List[str] = None
    ) -> str:
        """创建实验"""
        exp_id = f"exp_{int(datetime.now().timestamp())}"
        
        experiment = Experiment(
            id=exp_id,
            name=name,
            description=description,
            variants=variants,
            start_date=datetime.now(),
            metrics=metrics or ["latency", "satisfaction", "accuracy"]
        )
        
        self.experiments[exp_id] = experiment
        self.results[exp_id] = {
            v.id: ExperimentResult(variant_id=v.id)
            for v in variants
        }
        
        return exp_id
    
    def assign_variant(self, experiment_id: str, user_id: str) -> Variant:
        """为用户分配变体"""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        # 检查是否已分配
        assignment_key = f"{experiment_id}:{user_id}"
        if assignment_key in self.user_assignments:
            variant_id = self.user_assignments[assignment_key]
            for v in experiment.variants:
                if v.id == variant_id:
                    return v
        
        # 根据流量比例随机分配
        rand = random.random() * 100
        cumulative = 0
        for variant in experiment.variants:
            cumulative += variant.traffic_percentage
            if rand <= cumulative:
                self.user_assignments[assignment_key] = variant.id
                return variant
        
        # 默认返回第一个
        return experiment.variants[0]
    
    def record_result(
        self,
        experiment_id: str,
        variant_id: str,
        latency: float,
        satisfaction: int = None,
        error: bool = False
    ):
        """记录实验结果"""
        if experiment_id not in self.results:
            return
        
        result = self.results[experiment_id][variant_id]
        result.total_requests += 1
        result.total_latency += latency
        result.latencies.append(latency)
        
        if satisfaction:
            result.user_satisfaction.append(satisfaction)
        
        if error:
            result.error_count += 1
    
    def get_experiment_results(self, experiment_id: str) -> Dict:
        """获取实验结果"""
        if experiment_id not in self.results:
            return {}
        
        results = {}
        for variant_id, result in self.results[experiment_id].items():
            if result.total_requests > 0:
                results[variant_id] = {
                    "total_requests": result.total_requests,
                    "avg_latency": result.total_latency / result.total_requests,
                    "p50_latency": statistics.median(result.latencies) if result.latencies else 0,
                    "p95_latency": self._percentile(result.latencies, 95) if result.latencies else 0,
                    "error_rate": result.error_count / result.total_requests,
                    "avg_satisfaction": statistics.mean(result.user_satisfaction) if result.user_satisfaction else 0
                }
        
        return results
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """计算百分位数"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def determine_winner(self, experiment_id: str, metric: str = "avg_latency") -> Optional[str]:
        """确定获胜变体"""
        results = self.get_experiment_results(experiment_id)
        
        if not results or len(results) < 2:
            return None
        
        # 根据指标选择最优
        if metric in ["avg_latency", "error_rate"]:
            # 越低越好
            return min(results.items(), key=lambda x: x[1].get(metric, float('inf')))[0]
        else:
            # 越高越好
            return max(results.items(), key=lambda x: x[1].get(metric, 0))[0]
    
    def stop_experiment(self, experiment_id: str):
        """停止实验"""
        if experiment_id in self.experiments:
            self.experiments[experiment_id].status = "completed"
            self.experiments[experiment_id].end_date = datetime.now()


class ModelComparisonTest:
    """模型对比测试"""
    
    def __init__(self, ab_framework: ABTestFramework):
        self.ab_framework = ab_framework
        self.clients: Dict[str, DeerFlowClient] = {}
    
    def setup_model_comparison(
        self,
        models: List[str],
        test_queries: List[str]
    ) -> str:
        """设置模型对比实验"""
        
        variants = []
        for i, model in enumerate(models):
            variant = Variant(
                id=f"model-{model}",
                name=f"Model: {model}",
                config={"model_name": model},
                traffic_percentage=100.0 / len(models)
            )
            variants.append(variant)
            
            # 创建客户端
            self.clients[variant.id] = DeerFlowClient(model_name=model)
        
        exp_id = self.ab_framework.create_experiment(
            name="Model Performance Comparison",
            description=f"Compare models: {', '.join(models)}",
            variants=variants,
            metrics=["latency", "response_length", "quality_score"]
        )
        
        return exp_id
    
    def run_comparison_test(self, experiment_id: str, query: str, user_id: str) -> Dict:
        """运行对比测试"""
        import time
        
        # 分配变体
        variant = self.ab_framework.assign_variant(experiment_id, user_id)
        
        # 获取对应客户端
        client = self.clients.get(variant.id, DeerFlowClient())
        
        # 执行请求
        start_time = time.time()
        try:
            response = client.chat(query)
            latency = time.time() - start_time
            error = False
        except Exception as e:
            response = str(e)
            latency = time.time() - start_time
            error = True
        
        # 记录结果
        self.ab_framework.record_result(
            experiment_id=experiment_id,
            variant_id=variant.id,
            latency=latency,
            satisfaction=None,  # 可以添加用户反馈
            error=error
        )
        
        return {
            "variant": variant.name,
            "model": variant.config.get("model_name"),
            "response": response,
            "latency": latency,
            "error": error
        }


# 使用示例
def demonstrate_ab_testing():
    """演示 A/B 测试"""
    
    print("=" * 60)
    print("DeerFlow 2.0 A/B 测试演示")
    print("=" * 60)
    
    # 创建 A/B 测试框架
    ab_framework = ABTestFramework()
    
    # 创建模型对比测试
    model_test = ModelComparisonTest(ab_framework)
    
    # 设置对比实验
    print("\n1. 设置模型对比实验")
    exp_id = model_test.setup_model_comparison(
        models=["gpt-4", "claude-3"],
        test_queries=[]
    )
    print(f"实验 ID: {exp_id}")
    
    # 运行测试
    print("\n2. 运行对比测试")
    test_queries = [
        "解释什么是机器学习",
        "写一段 Python 代码计算斐波那契数列",
        "总结人工智能的发展历程"
    ]
    
    for i, query in enumerate(test_queries):
        user_id = f"user-{i}"
        result = model_test.run_comparison_test(exp_id, query, user_id)
        print(f"\n查询: {query[:30]}...")
        print(f"  模型: {result['model']}")
        print(f"  延迟: {result['latency']:.2f}s")
        print(f"  错误: {result['error']}")
    
    # 查看结果
    print("\n3. 实验结果")
    results = ab_framework.get_experiment_results(exp_id)
    for variant_id, metrics in results.items():
        print(f"\n变体 {variant_id}:")
        print(f"  总请求数: {metrics['total_requests']}")
        print(f"  平均延迟: {metrics['avg_latency']:.2f}s")
        print(f"  P95 延迟: {metrics['p95_latency']:.2f}s")
        print(f"  错误率: {metrics['error_rate']:.2%}")
    
    # 确定获胜者
    print("\n4. 获胜模型")
    winner = ab_framework.determine_winner(exp_id, metric="avg_latency")
    if winner:
        print(f"获胜变体: {winner}")
    
    # 停止实验
    ab_framework.stop_experiment(exp_id)
    print("\n实验已停止")


if __name__ == "__main__":
    demonstrate_ab_testing()
