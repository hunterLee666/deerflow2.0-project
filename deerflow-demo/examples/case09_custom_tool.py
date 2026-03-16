"""
案例 9: DeerFlow 2.0 自定义工具开发
完整代码示例 - 创建自定义技能
"""

from deerflow.client import DeerFlowClient
from typing import Dict, List, Any, Optional
import json
import os
from dataclasses import dataclass


@dataclass
class ToolDefinition:
    """工具定义"""
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Any


class CustomToolRegistry:
    """自定义工具注册表"""
    
    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}
    
    def register(self, tool: ToolDefinition):
        """注册工具"""
        self.tools[tool.name] = tool
        print(f"已注册工具: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """获取工具"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[Dict]:
        """列出所有工具"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for tool in self.tools.values()
        ]


# ==================== 自定义工具实现 ====================

def weather_tool(location: str, days: int = 1) -> str:
    """
    天气查询工具（模拟）
    """
    # 实际实现应该调用天气 API
    weather_data = {
        "北京": {"temp": 25, "condition": "晴", "humidity": 45},
        "上海": {"temp": 28, "condition": "多云", "humidity": 65},
        "广州": {"temp": 32, "condition": "雷阵雨", "humidity": 80},
    }
    
    data = weather_data.get(location, {"temp": 22, "condition": "未知", "humidity": 50})
    
    return f"""{location}天气:
- 温度: {data['temp']}°C
- 天气: {data['condition']}
- 湿度: {data['humidity']}%
- 预报天数: {days}天
"""


def calculator_tool(expression: str) -> str:
    """
    计算器工具
    """
    try:
        # 安全计算 - 只允许基本运算符
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            return "错误: 表达式包含非法字符"
        
        result = eval(expression)
        return f"计算结果: {expression} = {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"


def file_manager_tool(action: str, path: str, content: str = None) -> str:
    """
    文件管理工具
    """
    try:
        if action == "read":
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif action == "write":
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content or "")
            return f"文件已写入: {path}"
        
        elif action == "list":
            files = os.listdir(path)
            return "\n".join(files)
        
        elif action == "exists":
            return "存在" if os.path.exists(path) else "不存在"
        
        else:
            return f"未知操作: {action}"
    
    except Exception as e:
        return f"错误: {str(e)}"


def translation_tool(text: str, target_language: str = "en") -> str:
    """
    翻译工具（模拟）
    """
    # 实际实现应该调用翻译 API
    translations = {
        "en": {
            "你好": "Hello",
            "谢谢": "Thank you",
            "再见": "Goodbye"
        },
        "ja": {
            "你好": "こんにちは",
            "谢谢": "ありがとう",
            "再见": "さようなら"
        }
    }
    
    lang_dict = translations.get(target_language, translations["en"])
    translated = lang_dict.get(text, f"[翻译: {text} -> {target_language}]")
    
    return translated


def code_analyzer_tool(code: str, language: str = "python") -> str:
    """
    代码分析工具
    """
    analysis = []
    
    # 基础统计
    lines = code.split('\n')
    analysis.append(f"代码行数: {len(lines)}")
    analysis.append(f"字符数: {len(code)}")
    
    # 简单分析
    if language == "python":
        imports = [line for line in lines if line.strip().startswith('import') or line.strip().startswith('from')]
        functions = [line for line in lines if line.strip().startswith('def ')]
        classes = [line for line in lines if line.strip().startswith('class ')]
        
        analysis.append(f"导入语句: {len(imports)}")
        analysis.append(f"函数定义: {len(functions)}")
        analysis.append(f"类定义: {len(classes)}")
        
        if functions:
            analysis.append("\n函数列表:")
            for func in functions[:5]:  # 最多显示5个
                analysis.append(f"  - {func.strip()}")
    
    return "\n".join(analysis)


# ==================== 注册工具 ====================

def create_custom_tools() -> CustomToolRegistry:
    """创建并注册自定义工具"""
    
    registry = CustomToolRegistry()
    
    # 注册天气工具
    registry.register(ToolDefinition(
        name="weather",
        description="查询指定城市的天气信息",
        parameters={
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "城市名称，如'北京'、'上海'"
                },
                "days": {
                    "type": "integer",
                    "description": "预报天数",
                    "default": 1
                }
            },
            "required": ["location"]
        },
        function=weather_tool
    ))
    
    # 注册计算器工具
    registry.register(ToolDefinition(
        name="calculator",
        description="执行数学计算",
        parameters={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "数学表达式，如'2 + 2'、'10 * 5'"
                }
            },
            "required": ["expression"]
        },
        function=calculator_tool
    ))
    
    # 注册文件管理工具
    registry.register(ToolDefinition(
        name="file_manager",
        description="管理文件系统",
        parameters={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["read", "write", "list", "exists"],
                    "description": "操作类型"
                },
                "path": {
                    "type": "string",
                    "description": "文件或目录路径"
                },
                "content": {
                    "type": "string",
                    "description": "写入的内容（write操作需要）"
                }
            },
            "required": ["action", "path"]
        },
        function=file_manager_tool
    ))
    
    # 注册翻译工具
    registry.register(ToolDefinition(
        name="translation",
        description="翻译文本",
        parameters={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "要翻译的文本"
                },
                "target_language": {
                    "type": "string",
                    "enum": ["en", "ja", "fr", "de"],
                    "description": "目标语言代码",
                    "default": "en"
                }
            },
            "required": ["text"]
        },
        function=translation_tool
    ))
    
    # 注册代码分析工具
    registry.register(ToolDefinition(
        name="code_analyzer",
        description="分析代码结构和统计信息",
        parameters={
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "代码内容"
                },
                "language": {
                    "type": "string",
                    "enum": ["python", "javascript", "java", "cpp"],
                    "default": "python"
                }
            },
            "required": ["code"]
        },
        function=code_analyzer_tool
    ))
    
    return registry


# ==================== 使用示例 ====================

def demonstrate_custom_tools():
    """演示自定义工具使用"""
    
    print("=" * 60)
    print("DeerFlow 2.0 自定义工具演示")
    print("=" * 60)
    
    # 创建工具注册表
    registry = create_custom_tools()
    
    # 列出所有工具
    print("\n1. 可用工具列表:")
    for tool_info in registry.list_tools():
        print(f"  - {tool_info['name']}: {tool_info['description']}")
    
    # 测试各个工具
    print("\n2. 测试天气工具:")
    weather_tool_def = registry.get_tool("weather")
    if weather_tool_def:
        result = weather_tool_def.function(location="北京", days=3)
        print(result)
    
    print("\n3. 测试计算器工具:")
    calc_tool_def = registry.get_tool("calculator")
    if calc_tool_def:
        result = calc_tool_def.function(expression="(100 + 200) * 3 / 4")
        print(result)
    
    print("\n4. 测试代码分析工具:")
    code_tool_def = registry.get_tool("code_analyzer")
    if code_tool_def:
        sample_code = """
def hello():
    print("Hello")

class MyClass:
    def method(self):
        pass
"""
        result = code_tool_def.function(code=sample_code, language="python")
        print(result)
    
    print("\n5. 测试翻译工具:")
    trans_tool_def = registry.get_tool("translation")
    if trans_tool_def:
        result = trans_tool_def.function(text="你好", target_language="en")
        print(f"翻译结果: {result}")
    
    # 工具调用格式示例
    print("\n6. 工具调用格式示例 (OpenAI Function Calling 格式):")
    tool_schemas = []
    for tool_def in registry.tools.values():
        tool_schemas.append({
            "type": "function",
            "function": {
                "name": tool_def.name,
                "description": tool_def.description,
                "parameters": tool_def.parameters
            }
        })
    
    print(json.dumps(tool_schemas, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    demonstrate_custom_tools()
