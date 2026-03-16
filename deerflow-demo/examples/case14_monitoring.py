"""
案例 14: DeerFlow 2.0 监控与日志
完整代码示例 - 指标收集、告警、追踪
"""

from deerflow.client import DeerFlowClient
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import time
import json
import logging
from enum import Enum
import asyncio


class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Metric:
    """指标数据"""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    unit: str = ""


@dataclass
class LogEntry:
    """日志条目"""
    timestamp: datetime
    level: LogLevel
    message: str
    source: str
    context: Dict = field(default_factory=dict)


@dataclass
class Alert:
    """告警"""
    id: str
    name: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.metrics: List[Metric] = []
        self.counters: Dict[str, int] = {}
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = {}
    
    def record_counter(self, name: str, value: int = 1, labels: Dict = None):
        """记录计数器"""
        key = f"{name}:{json.dumps(labels or {}, sort_keys=True)}"
        self.counters[key] = self.counters.get(key, 0) + value
        
        self.metrics.append(Metric(
            name=name,
            value=self.counters[key],
            timestamp=datetime.now(),
            labels=labels or {}
        ))
    
    def record_gauge(self, name: str, value: float, labels: Dict = None):
        """记录仪表盘"""
        key = f"{name}:{json.dumps(labels or {}, sort_keys=True)}"
        self.gauges[key] = value
        
        self.metrics.append(Metric(
            name=name,
            value=value,
            timestamp=datetime.now(),
            labels=labels or {}
        ))
    
    def record_histogram(self, name: str, value: float, labels: Dict = None):
        """记录直方图"""
        key = f"{name}:{json.dumps(labels or {}, sort_keys=True)}"
        if key not in self.histograms:
            self.histograms[key] = []
        self.histograms[key].append(value)
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取所有指标"""
        return {
            "counters": self.counters,
            "gauges": self.gauges,
            "histograms": {
                k: {
                    "count": len(v),
                    "sum": sum(v),
                    "avg": sum(v) / len(v) if v else 0,
                    "min": min(v) if v else 0,
                    "max": max(v) if v else 0
                }
                for k, v in self.histograms.items()
            }
        }


class Logger:
    """增强日志记录器"""
    
    def __init__(self, name: str = "deerflow"):
        self.name = name
        self.logs: List[LogEntry] = []
        
        # 配置标准日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(name)
    
    def log(self, level: LogLevel, message: str, context: Dict = None):
        """记录日志"""
        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            message=message,
            source=self.name,
            context=context or {}
        )
        self.logs.append(entry)
        
        # 同时输出到标准日志
        log_func = {
            LogLevel.DEBUG: self.logger.debug,
            LogLevel.INFO: self.logger.info,
            LogLevel.WARNING: self.logger.warning,
            LogLevel.ERROR: self.logger.error,
            LogLevel.CRITICAL: self.logger.critical
        }.get(level, self.logger.info)
        
        log_func(message)
    
    def debug(self, message: str, context: Dict = None):
        self.log(LogLevel.DEBUG, message, context)
    
    def info(self, message: str, context: Dict = None):
        self.log(LogLevel.INFO, message, context)
    
    def warning(self, message: str, context: Dict = None):
        self.log(LogLevel.WARNING, message, context)
    
    def error(self, message: str, context: Dict = None):
        self.log(LogLevel.ERROR, message, context)
    
    def critical(self, message: str, context: Dict = None):
        self.log(LogLevel.CRITICAL, message, context)
    
    def get_logs(self, level: LogLevel = None, limit: int = 100) -> List[LogEntry]:
        """获取日志"""
        logs = self.logs
        if level:
            logs = [l for l in logs if l.level == level]
        return logs[-limit:]


class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.rules: List[Dict] = []
        self.handlers: List[callable] = []
    
    def add_rule(self, name: str, condition: callable, severity: str):
        """添加告警规则"""
        self.rules.append({
            "name": name,
            "condition": condition,
            "severity": severity
        })
    
    def add_handler(self, handler: callable):
        """添加告警处理器"""
        self.handlers.append(handler)
    
    def check_alerts(self, metrics: Dict):
        """检查告警"""
        for rule in self.rules:
            if rule["condition"](metrics):
                alert = Alert(
                    id=f"alert-{int(time.time())}",
                    name=rule["name"],
                    severity=rule["severity"],
                    message=f"触发告警: {rule['name']}",
                    timestamp=datetime.now()
                )
                self.alerts.append(alert)
                
                # 通知处理器
                for handler in self.handlers:
                    handler(alert)
    
    def resolve_alert(self, alert_id: str):
        """解决告警"""
        for alert in self.alerts:
            if alert.id == alert_id and not alert.resolved:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                return True
        return False
    
    def get_active_alerts(self) -> List[Alert]:
        """获取活动告警"""
        return [a for a in self.alerts if not a.resolved]


class MonitoredDeerFlowClient:
    """带监控的 DeerFlow 客户端"""
    
    def __init__(self):
        self.client = DeerFlowClient()
        self.metrics = MetricsCollector()
        self.logger = Logger("deerflow-monitored")
        self.alerts = AlertManager()
        
        # 配置告警规则
        self._setup_alert_rules()
    
    def _setup_alert_rules(self):
        """设置告警规则"""
        # 响应时间告警
        self.alerts.add_rule(
            name="high_latency",
            condition=lambda m: m.get("histograms", {}).get("request_latency", {}).get("avg", 0) > 10,
            severity="high"
        )
        
        # 错误率告警
        self.alerts.add_rule(
            name="high_error_rate",
            condition=lambda m: m.get("counters", {}).get("errors", 0) > 10,
            severity="critical"
        )
    
    def chat(self, message: str, **kwargs) -> str:
        """带监控的对话"""
        start_time = time.time()
        thread_id = kwargs.get("thread_id", "default")
        
        self.logger.info(f"开始对话", {"thread_id": thread_id, "message_length": len(message)})
        
        try:
            response = self.client.chat(message, **kwargs)
            
            # 记录指标
            latency = time.time() - start_time
            self.metrics.record_histogram("request_latency", latency, {"thread_id": thread_id})
            self.metrics.record_counter("requests_total", 1, {"status": "success"})
            
            self.logger.info(f"对话完成", {"thread_id": thread_id, "latency": latency})
            
            return response
            
        except Exception as e:
            # 记录错误
            self.metrics.record_counter("errors", 1, {"type": "chat_error"})
            self.logger.error(f"对话失败: {str(e)}", {"thread_id": thread_id})
            raise
        
        finally:
            # 检查告警
            self.alerts.check_alerts(self.metrics.get_metrics())
    
    def stream(self, message: str, **kwargs):
        """带监控的流式对话"""
        start_time = time.time()
        token_count = 0
        
        for event in self.client.stream(message, **kwargs):
            if event.type == "messages-tuple":
                if event.data.get("content"):
                    token_count += len(event.data["content"].split())
            
            yield event
        
        # 记录指标
        latency = time.time() - start_time
        self.metrics.record_histogram("stream_latency", latency)
        self.metrics.record_gauge("tokens_generated", token_count)
    
    def get_dashboard_data(self) -> Dict:
        """获取监控面板数据"""
        return {
            "metrics": self.metrics.get_metrics(),
            "recent_logs": [
                {
                    "timestamp": l.timestamp.isoformat(),
                    "level": l.level.value,
                    "message": l.message
                }
                for l in self.logger.get_logs(limit=10)
            ],
            "active_alerts": [
                {
                    "id": a.id,
                    "name": a.name,
                    "severity": a.severity,
                    "message": a.message,
                    "timestamp": a.timestamp.isoformat()
                }
                for a in self.alerts.get_active_alerts()
            ]
        }


# 使用示例
def demonstrate_monitoring():
    """演示监控系统"""
    
    print("=" * 60)
    print("DeerFlow 2.0 监控与日志演示")
    print("=" * 60)
    
    # 创建带监控的客户端
    monitored_client = MonitoredDeerFlowClient()
    
    # 模拟一些请求
    print("\n1. 模拟请求")
    for i in range(5):
        try:
            response = monitored_client.chat(f"测试消息 {i+1}", thread_id="demo-thread")
            print(f"请求 {i+1} 完成")
        except Exception as e:
            print(f"请求 {i+1} 失败: {e}")
    
    # 查看指标
    print("\n2. 监控指标")
    dashboard = monitored_client.get_dashboard_data()
    print(json.dumps(dashboard["metrics"], indent=2))
    
    # 查看日志
    print("\n3. 最近日志")
    for log in dashboard["recent_logs"]:
        print(f"[{log['level'].upper()}] {log['message']}")
    
    # 查看告警
    print("\n4. 活动告警")
    if dashboard["active_alerts"]:
        for alert in dashboard["active_alerts"]:
            print(f"[{alert['severity'].upper()}] {alert['name']}: {alert['message']}")
    else:
        print("无活动告警")


if __name__ == "__main__":
    demonstrate_monitoring()
