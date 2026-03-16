"""
案例 19: DeerFlow 2.0 安全加固方案
完整代码示例 - 输入验证、输出过滤、PII 保护
"""

from deerflow.client import DeerFlowClient
from typing import Dict, List, Any, Optional
import re
import json
from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityCheck:
    """安全检查结果"""
    passed: bool
    risk_level: RiskLevel
    message: str
    details: Dict = None


class InputValidator:
    """输入验证器"""
    
    # 危险模式
    DANGEROUS_PATTERNS = [
        (r'<script[^>]*>.*?</script>', "XSS attempt detected"),
        (r'javascript:', "JavaScript protocol detected"),
        (r'on\w+\s*=', "Event handler detected"),
        (r'(DROP|DELETE|INSERT|UPDATE)\s+TABLE', "SQL injection attempt"),
        (r'UNION\s+SELECT', "SQL injection attempt"),
        (r'\$\{.*\}', "Template injection attempt"),
        (r'\{\{.*\}\}', "Template injection attempt"),
        (r'__import__\s*\(|eval\s*\(|exec\s*\(', "Code injection attempt"),
        (r'\.\./|\.\.\\', "Path traversal attempt"),
        (r'file://|ftp://|http://', "Suspicious URL scheme"),
    ]
    
    # 敏感关键词
    SENSITIVE_KEYWORDS = [
        'password', 'secret', 'token', 'api_key', 'private_key',
        'credit_card', 'ssn', 'social_security'
    ]
    
    def __init__(self):
        self.max_input_length = 10000
        self.max_prompt_length = 50000
    
    def validate(self, input_text: str) -> SecurityCheck:
        """验证输入"""
        # 1. 长度检查
        if len(input_text) > self.max_input_length:
            return SecurityCheck(
                passed=False,
                risk_level=RiskLevel.MEDIUM,
                message=f"Input too long: {len(input_text)} > {self.max_input_length}"
            )
        
        # 2. 危险模式检查
        for pattern, message in self.DANGEROUS_PATTERNS:
            if re.search(pattern, input_text, re.IGNORECASE):
                return SecurityCheck(
                    passed=False,
                    risk_level=RiskLevel.HIGH,
                    message=message,
                    details={"pattern": pattern}
                )
        
        # 3. 敏感信息检查
        detected_keywords = [
            kw for kw in self.SENSITIVE_KEYWORDS
            if kw.lower() in input_text.lower()
        ]
        
        if detected_keywords:
            return SecurityCheck(
                passed=True,
                risk_level=RiskLevel.MEDIUM,
                message="Sensitive keywords detected",
                details={"keywords": detected_keywords}
            )
        
        return SecurityCheck(
            passed=True,
            risk_level=RiskLevel.LOW,
            message="Input validation passed"
        )
    
    def sanitize(self, input_text: str) -> str:
        """清理输入"""
        # 移除 HTML 标签
        sanitized = re.sub(r'<[^>]+>', '', input_text)
        
        # 规范化空白字符
        sanitized = ' '.join(sanitized.split())
        
        return sanitized


class OutputFilter:
    """输出过滤器"""
    
    # 需要过滤的内容模式
    FILTER_PATTERNS = [
        (r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[CREDIT_CARD]'),  # 信用卡
        (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]'),  # 社保号
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),  # 邮箱
        (r'\b\d{3}-\d{3}-\d{4}\b', '[PHONE]'),  # 电话
        (r'sk-[a-zA-Z0-9]{48}', '[API_KEY]'),  # OpenAI API key
        (r'[a-zA-Z0-9]{32}', '[TOKEN]'),  # 通用 token
    ]
    
    # 不当内容关键词
    INAPPROPRIATE_KEYWORDS = [
        'hack', 'exploit', 'vulnerability', 'bypass',
        'illegal', 'unauthorized', 'breach'
    ]
    
    def filter_pii(self, text: str) -> str:
        """过滤个人身份信息"""
        filtered = text
        for pattern, replacement in self.FILTER_PATTERNS:
            filtered = re.sub(pattern, replacement, filtered)
        return filtered
    
    def check_content_safety(self, text: str) -> SecurityCheck:
        """检查内容安全性"""
        # 检查不当关键词
        detected = [
            kw for kw in self.INAPPROPRIATE_KEYWORDS
            if kw.lower() in text.lower()
        ]
        
        if detected:
            return SecurityCheck(
                passed=False,
                risk_level=RiskLevel.HIGH,
                message="Potentially inappropriate content detected",
                details={"keywords": detected}
            )
        
        return SecurityCheck(
            passed=True,
            risk_level=RiskLevel.LOW,
            message="Content safety check passed"
        )
    
    def filter_output(self, text: str, filter_pii: bool = True) -> str:
        """过滤输出"""
        if filter_pii:
            text = self.filter_pii(text)
        return text


class PIIDetector:
    """PII 检测器"""
    
    PII_PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b\d{3}-\d{3}-\d{4}\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "credit_card": r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        "ip_address": r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
        "api_key": r'(sk-[a-zA-Z0-9]{48}|api[_-]?key[_-]?[a-zA-Z0-9]{16,})',
    }
    
    def detect(self, text: str) -> Dict[str, List[str]]:
        """检测 PII"""
        detected = {}
        
        for pii_type, pattern in self.PII_PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                detected[pii_type] = matches
        
        return detected
    
    def has_pii(self, text: str) -> bool:
        """检查是否包含 PII"""
        return len(self.detect(text)) > 0


class SecureDeerFlowClient:
    """安全的 DeerFlow 客户端"""
    
    def __init__(self, client: DeerFlowClient = None):
        self.client = client or DeerFlowClient()
        self.input_validator = InputValidator()
        self.output_filter = OutputFilter()
        self.pii_detector = PIIDetector()
        
        # 安全策略
        self.security_policy = {
            "validate_input": True,
            "filter_output_pii": True,
            "check_content_safety": True,
            "log_security_events": True
        }
    
    def chat(self, message: str, **kwargs) -> str:
        """安全的对话"""
        # 1. 输入验证
        if self.security_policy["validate_input"]:
            check = self.input_validator.validate(message)
            if not check.passed and check.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                raise SecurityError(f"Input validation failed: {check.message}")
            
            # 清理输入
            message = self.input_validator.sanitize(message)
        
        # 2. 检查 PII
        pii_detected = self.pii_detector.detect(message)
        if pii_detected:
            print(f"[Security Warning] PII detected in input: {list(pii_detected.keys())}")
        
        # 3. 执行请求
        response = self.client.chat(message, **kwargs)
        
        # 4. 输出过滤
        if self.security_policy["filter_output_pii"]:
            response = self.output_filter.filter_output(response)
        
        # 5. 内容安全检查
        if self.security_policy["check_content_safety"]:
            safety_check = self.output_filter.check_content_safety(response)
            if not safety_check.passed:
                print(f"[Security Warning] {safety_check.message}")
        
        return response
    
    def get_security_report(self) -> Dict:
        """获取安全报告"""
        return {
            "policy": self.security_policy,
            "validators": {
                "dangerous_patterns": len(self.input_validator.DANGEROUS_PATTERNS),
                "sensitive_keywords": len(self.input_validator.SENSITIVE_KEYWORDS)
            },
            "filters": {
                "pii_patterns": len(self.output_filter.FILTER_PATTERNS),
                "inappropriate_keywords": len(self.output_filter.INAPPROPRIATE_KEYWORDS)
            }
        }


class SecurityError(Exception):
    """安全错误"""
    pass


# 使用示例
def demonstrate_security():
    """演示安全功能"""
    
    print("=" * 60)
    print("DeerFlow 2.0 安全加固演示")
    print("=" * 60)
    
    # 创建安全客户端
    secure_client = SecureDeerFlowClient()
    
    # 1. 输入验证测试
    print("\n1. 输入验证测试")
    
    test_inputs = [
        "正常输入",
        "<script>alert('xss')</script>",
        "DROP TABLE users;",
        "密码是 secret123",
    ]
    
    for input_text in test_inputs:
        check = secure_client.input_validator.validate(input_text)
        print(f"输入: {input_text[:30]}...")
        print(f"  结果: {'通过' if check.passed else '失败'}")
        print(f"  风险: {check.risk_level.value}")
        print(f"  消息: {check.message}")
        print()
    
    # 2. PII 检测测试
    print("2. PII 检测测试")
    
    test_text = """
    联系信息:
    邮箱: user@example.com
    电话: 123-456-7890
    API Key: sk-abcdefghijklmnopqrstuvwxyz1234567890abcdef
    """
    
    pii_detected = secure_client.pii_detector.detect(test_text)
    print(f"检测到的 PII: {json.dumps(pii_detected, indent=2)}")
    
    # 3. 输出过滤测试
    print("\n3. 输出过滤测试")
    filtered = secure_client.output_filter.filter_pii(test_text)
    print(f"过滤后:\n{filtered}")
    
    # 4. 安全报告
    print("\n4. 安全报告")
    report = secure_client.get_security_report()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    demonstrate_security()
