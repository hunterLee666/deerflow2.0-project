"""
案例 21: DeerFlow 2.0 测试策略
完整代码示例 - 单元测试、集成测试、性能测试、Mock
"""

import pytest
import asyncio
import json
import time
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass
import aiohttp
import pytest_asyncio

from deerflow.client import DeerFlowClient, StreamEvent


# ==================== Fixtures ====================

@pytest.fixture
def mock_deerflow_client():
    """Mock DeerFlow 客户端"""
    client = Mock(spec=DeerFlowClient)
    client.chat.return_value = "Mocked response"
    client.stream.return_value = [
        StreamEvent(type="messages-tuple", data={"type": "ai", "content": "Hello"}),
        StreamEvent(type="end", data={})
    ]
    client.list_models.return_value = {
        "models": [{"name": "gpt-4", "supports_thinking": True}]
    }
    client.list_skills.return_value = {
        "skills": [{"name": "web_search", "enabled": True}]
    }
    return client


@pytest.fixture
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ==================== 单元测试 ====================

class TestDeerFlowClient:
    """DeerFlowClient 单元测试"""
    
    def test_chat_basic(self, mock_deerflow_client):
        """测试基本聊天功能"""
        response = mock_deerflow_client.chat("Hello")
        assert response == "Mocked response"
        mock_deerflow_client.chat.assert_called_once_with("Hello")
    
    def test_chat_with_thread_id(self, mock_deerflow_client):
        """测试带 thread_id 的聊天"""
        mock_deerflow_client.chat("Hello", thread_id="test-thread")
        mock_deerflow_client.chat.assert_called_with("Hello", thread_id="test-thread")
    
    def test_stream(self, mock_deerflow_client):
        """测试流式输出"""
        events = list(mock_deerflow_client.stream("Hello"))
        assert len(events) == 2
        assert events[0].type == "messages-tuple"
        assert events[1].type == "end"
    
    def test_list_models(self, mock_deerflow_client):
        """测试模型列表"""
        models = mock_deerflow_client.list_models()
        assert "models" in models
        assert len(models["models"]) == 1
        assert models["models"][0]["name"] == "gpt-4"
    
    def test_list_skills(self, mock_deerflow_client):
        """测试技能列表"""
        skills = mock_deerflow_client.list_skills()
        assert "skills" in skills
        assert skills["skills"][0]["name"] == "web_search"


class TestInputValidation:
    """输入验证测试"""
    
    @pytest.mark.parametrize("input_text,expected_valid", [
        ("Hello, how are you?", True),
        ("What is AI?", True),
        ("", False),  # 空输入
        ("a" * 10001, False),  # 过长输入
        ("<script>alert('xss')</script>", False),  # XSS 尝试
        ("SELECT * FROM users; DROP TABLE users;", False),  # SQL 注入
    ])
    def test_input_validation(self, input_text, expected_valid):
        """参数化输入验证测试"""
        # 简化的验证逻辑
        is_valid = (
            len(input_text) > 0 and
            len(input_text) <= 10000 and
            "<script>" not in input_text.lower() and
            "drop table" not in input_text.lower()
        )
        assert is_valid == expected_valid


# ==================== 集成测试 ====================

@pytest.mark.integration
class TestIntegration:
    """集成测试"""
    
    @pytest_asyncio.fixture
    async def real_client(self):
        """真实客户端（需要环境配置）"""
        # 注意：这些测试需要实际的 DeerFlow 服务
        client = DeerFlowClient()
        yield client
    
    @pytest.mark.asyncio
    async def test_real_chat(self, real_client):
        """测试真实聊天（需要服务）"""
        # 跳过如果没有配置
        pytest.skip("需要实际服务配置")
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: real_client.chat("Hello", thread_id="test")
        )
        assert isinstance(response, str)
        assert len(response) > 0
    
    @pytest.mark.asyncio
    async def test_real_stream(self, real_client):
        """测试真实流式输出"""
        pytest.skip("需要实际服务配置")
        
        events = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: list(real_client.stream("Hello"))
        )
        assert len(events) > 0
        assert any(e.type == "end" for e in events)


# ==================== 性能测试 ====================

class TestPerformance:
    """性能测试"""
    
    @pytest.mark.benchmark
    def test_chat_latency(self, mock_deerflow_client, benchmark):
        """测试聊天延迟"""
        def chat():
            return mock_deerflow_client.chat("Hello")
        
        result = benchmark(chat)
        assert result == "Mocked response"
    
    @pytest.mark.benchmark
    def test_throughput(self, benchmark):
        """测试吞吐量"""
        def process_batch():
            # 模拟批处理
            return [f"Response {i}" for i in range(100)]
        
        result = benchmark(process_batch)
        assert len(result) == 100
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """测试并发请求"""
        async def mock_request(i: int) -> str:
            await asyncio.sleep(0.01)  # 模拟延迟
            return f"Response {i}"
        
        start = time.time()
        tasks = [mock_request(i) for i in range(50)]
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start
        
        assert len(results) == 50
        assert elapsed < 1.0  # 应该在1秒内完成


# ==================== Mock 测试 ====================

class TestWithMocking:
    """使用 Mock 的测试"""
    
    @pytest.mark.asyncio
    async def test_async_chat_with_mock(self):
        """测试异步聊天（使用 Mock）"""
        with patch('deerflow.client.DeerFlowClient') as MockClient:
            # 配置 Mock
            instance = MockClient.return_value
            instance.chat.return_value = "Mocked async response"
            
            # 使用 Mock
            client = DeerFlowClient()
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.chat("Hello")
            )
            
            assert response == "Mocked async response"
            instance.chat.assert_called_once()
    
    def test_external_api_mock(self):
        """测试外部 API Mock"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # 配置 Mock 响应
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json.return_value = asyncio.Future()
            mock_response.json.return_value.set_result({"status": "ok"})
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # 测试代码会使用这个 Mock
            # async with aiohttp.ClientSession() as session:
            #     async with session.get("http://api.example.com") as resp:
            #         data = await resp.json()
            
            mock_get.assert_not_called()  # 因为我们没有实际调用
    
    def test_stream_mock(self):
        """测试流式 Mock"""
        def mock_stream():
            for i in range(5):
                yield StreamEvent(
                    type="messages-tuple",
                    data={"type": "ai", "content": f"Chunk {i}"}
                )
            yield StreamEvent(type="end", data={})
        
        with patch.object(DeerFlowClient, 'stream', mock_stream):
            client = DeerFlowClient()
            events = list(client.stream("Hello"))
            
            assert len(events) == 6
            assert events[-1].type == "end"


# ==================== 端到端测试 ====================

@pytest.mark.e2e
class TestEndToEnd:
    """端到端测试"""
    
    @pytest.fixture
    def test_app(self):
        """创建测试应用"""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        
        app = FastAPI()
        
        @app.post("/api/chat")
        async def chat(request: Dict[str, Any]):
            client = DeerFlowClient()
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.chat(request.get("message"))
            )
            return {"response": response}
        
        return TestClient(app)
    
    def test_api_endpoint(self, test_app):
        """测试 API 端点"""
        response = test_app.post("/api/chat", json={"message": "Hello"})
        
        # 注意：如果没有实际服务，这会失败
        # 这里只是演示结构
        # assert response.status_code == 200
        # assert "response" in response.json()


# ==================== 测试工具类 ====================

class DeerFlowTestHelper:
    """DeerFlow 测试辅助类"""
    
    @staticmethod
    def create_mock_client(responses: Dict[str, str] = None) -> Mock:
        """创建 Mock 客户端"""
        client = Mock(spec=DeerFlowClient)
        
        def side_effect(message, **kwargs):
            if responses and message in responses:
                return responses[message]
            return f"Mock response for: {message[:20]}..."
        
        client.chat.side_effect = side_effect
        return client
    
    @staticmethod
    def assert_chat_called_with(client: Mock, expected_message: str):
        """验证聊天调用"""
        client.chat.assert_called()
        call_args = client.chat.call_args
        assert call_args[0][0] == expected_message
    
    @staticmethod
    async def run_async_test(coro):
        """运行异步测试"""
        return await coro


# 测试覆盖率检查
def check_test_coverage():
    """检查测试覆盖率"""
    import subprocess
    
    result = subprocess.run(
        ["pytest", "--cov=deerflow", "--cov-report=html", "-v"],
        capture_output=True,
        text=True
    )
    
    print("测试覆盖率报告:")
    print(result.stdout)
    
    if result.returncode != 0:
        print("测试失败:")
        print(result.stderr)


# 运行测试
if __name__ == "__main__":
    # 运行所有测试
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--ignore=case17_distributed.py",  # 忽略分布式测试
    ])
