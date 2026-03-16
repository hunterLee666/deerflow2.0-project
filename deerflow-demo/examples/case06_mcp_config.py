"""
案例 6: DeerFlow 2.0 MCP 配置管理
完整代码示例 - 模型上下文协议配置
"""

from deerflow.client import DeerFlowClient
from typing import Dict, List, Any, Optional
import json
import yaml


class MCPConfigManager:
    """MCP 配置管理器"""
    
    def __init__(self, client: DeerFlowClient = None):
        self.client = client or DeerFlowClient()
    
    def create_mcp_config(
        self,
        name: str,
        server_type: str,
        command: Optional[str] = None,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None,
        url: Optional[str] = None,
        enabled: bool = True
    ) -> Dict[str, Any]:
        """
        创建 MCP 服务器配置
        
        Args:
            name: MCP 服务器名称
            server_type: 服务器类型 (stdio, sse, websocket)
            command: 命令（stdio 类型）
            args: 参数列表
            env: 环境变量
            url: 服务器 URL（sse/websocket 类型）
            enabled: 是否启用
        """
        config = {
            "mcpServers": {
                name: {
                    "type": server_type,
                    "enabled": enabled
                }
            }
        }
        
        if server_type == "stdio":
            config["mcpServers"][name].update({
                "command": command,
                "args": args or [],
                "env": env or {}
            })
        elif server_type in ["sse", "websocket"]:
            config["mcpServers"][name].update({
                "url": url
            })
        
        return config
    
    def save_config(self, config: Dict[str, Any], filepath: str):
        """保存配置到文件"""
        with open(filepath, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        print(f"配置已保存到: {filepath}")
    
    def load_config(self, filepath: str) -> Dict[str, Any]:
        """从文件加载配置"""
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)


# 常用 MCP 服务器配置示例
def create_common_mcp_configs():
    """创建常用 MCP 服务器配置"""
    
    manager = MCPConfigManager()
    
    # 1. 文件系统 MCP 服务器
    filesystem_config = manager.create_mcp_config(
        name="filesystem",
        server_type="stdio",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/dirs"],
        enabled=True
    )
    
    # 2. GitHub MCP 服务器
    github_config = manager.create_mcp_config(
        name="github",
        server_type="stdio",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"},
        enabled=True
    )
    
    # 3. PostgreSQL MCP 服务器
    postgres_config = manager.create_mcp_config(
        name="postgres",
        server_type="stdio",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-postgres", 
                "postgresql://user:pass@localhost/db"],
        enabled=True
    )
    
    # 4. SQLite MCP 服务器
    sqlite_config = manager.create_mcp_config(
        name="sqlite",
        server_type="stdio",
        command="uvx",
        args=["mcp-server-sqlite", "--db-path", "/path/to/database.db"],
        enabled=True
    )
    
    # 5. Brave 搜索 MCP 服务器
    brave_config = manager.create_mcp_config(
        name="brave-search",
        server_type="stdio",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-brave-search"],
        env={"BRAVE_API_KEY": "${BRAVE_API_KEY}"},
        enabled=True
    )
    
    # 6. 远程 SSE MCP 服务器示例
    remote_sse_config = manager.create_mcp_config(
        name="remote-service",
        server_type="sse",
        url="https://api.example.com/mcp/sse",
        enabled=True
    )
    
    # 合并所有配置
    merged_config = {"mcpServers": {}}
    for cfg in [filesystem_config, github_config, postgres_config, 
                sqlite_config, brave_config, remote_sse_config]:
        merged_config["mcpServers"].update(cfg["mcpServers"])
    
    return merged_config


def create_deerflow_config_with_mcp():
    """创建包含 MCP 配置的 DeerFlow 完整配置"""
    
    config = {
        "app": {
            "name": "DeerFlow Demo",
            "version": "2.0.0"
        },
        "model": {
            "default": "gpt-4",
            "fallback": "gpt-3.5-turbo"
        },
        "agents": {
            "lead_agent": {
                "model": "gpt-4",
                "thinking_enabled": True,
                "plan_mode": True
            }
        },
        "mcpServers": {
            "filesystem": {
                "type": "stdio",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", 
                         "/Users/demo/projects"],
                "enabled": True
            },
            "github": {
                "type": "stdio",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"],
                "env": {
                    "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
                },
                "enabled": True
            },
            "brave-search": {
                "type": "stdio",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-brave-search"],
                "env": {
                    "BRAVE_API_KEY": "${BRAVE_API_KEY}"
                },
                "enabled": True
            }
        },
        "skills": {
            "auto_load": True,
            "directories": ["./skills"]
        },
        "sandbox": {
            "type": "local",
            "timeout": 300
        }
    }
    
    return config


def demonstrate_mcp_usage():
    """演示 MCP 配置使用"""
    
    print("=" * 60)
    print("DeerFlow 2.0 MCP 配置管理演示")
    print("=" * 60)
    
    # 1. 创建常用 MCP 配置
    print("\n1. 创建常用 MCP 服务器配置")
    common_configs = create_common_mcp_configs()
    print(json.dumps(common_configs, indent=2, ensure_ascii=False))
    
    # 2. 创建完整 DeerFlow 配置
    print("\n2. 创建包含 MCP 的 DeerFlow 配置")
    full_config = create_deerflow_config_with_mcp()
    print(json.dumps(full_config, indent=2, ensure_ascii=False))
    
    # 3. 保存配置
    print("\n3. 保存配置到文件")
    manager = MCPConfigManager()
    manager.save_config(full_config, "deerflow_config.yaml")
    
    # 4. 使用配置初始化客户端
    print("\n4. 使用配置初始化 DeerFlow 客户端")
    client = DeerFlowClient(config_path="deerflow_config.yaml")
    print("客户端初始化成功，已加载 MCP 配置")
    
    # 5. 列出可用工具
    print("\n5. 可用工具列表（包含 MCP 工具）")
    try:
        tools = client.list_skills()
        for tool in tools.get("skills", []):
            print(f"  - {tool['name']}: {tool.get('description', 'N/A')}")
    except Exception as e:
        print(f"  获取工具列表: {e}")


if __name__ == "__main__":
    demonstrate_mcp_usage()
