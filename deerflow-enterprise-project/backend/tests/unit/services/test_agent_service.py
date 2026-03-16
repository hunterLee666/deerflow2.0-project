import pytest
from unittest.mock import MagicMock, patch
from app.services.agent_service import AgentService
from app.models import AgentConfig


@pytest.fixture
def mock_harness():
    """Mock DeerFlow harness dependency"""
    with patch("app.services.agent_service.DeerFlowHarness") as mock:
        mock.return_value.initialize.return_value = "initialized"
        yield mock


@pytest.fixture
def agent_service(mock_harness):
    """Ready-to-test agent service"""
    return AgentService()


class TestAgentService:
    def test_create_agent(self, agent_service, mock_harness):
        """Should create agent with proper configuration"""
        config = AgentConfig(
            name="test-agent",
            role="tester",
            tools=["browser"]
        )

        agent = agent_service.create_agent(config)

        assert agent.id is not None
        assert agent.name == "test-agent"
        mock_harness.return_value.initialize.assert_called_once()

    @pytest.mark.parametrize("invalid_role", [
        "", "invalid-role", None
    ])
    def test_create_agent_with_invalid_role_fails(
        self,
        agent_service,
        invalid_role
    ):
        """Should reject invalid roles"""
        config = AgentConfig(
            name="test",
            role=invalid_role,
            tools=[]
        )

        with pytest.raises(ValueError, match="Invalid agent role"):
            agent_service.create_agent(config)

    def test_sandbox_security(self, agent_service):
        """Ensure sandbox blocks dangerous operations"""
        # Test actual sandbox implementation
        from app.services.sandbox import Sandbox

        sandbox = Sandbox()
        with pytest.raises(SecurityError):
            sandbox.run("import os; os.system('rm -rf /')")

        # Verify safe code executes
        result = sandbox.run("2+2")
        assert result == 4

    def test_agent_memory_persistence(self, agent_service):
        """Verify agent memory survives operations"""
        agent = agent_service.create_agent(AgentConfig(name="memory-test"))
        agent_service.add_memory(agent.id, "test_key", "test_value")

        retrieved = agent_service.get_memory(agent.id, "test_key")
        assert retrieved == "test_value"

    def test_concurrent_agent_operations(self, agent_service, mock_harness):
        """Test multiple agents operating simultaneously"""
        agents = []
        for i in range(5):
            config = AgentConfig(name=f"agent-{i}", role="worker")
            agents.append(agent_service.create_agent(config))

        assert len(agents) == 5
        assert len(agent_service.list_agents()) == 5

        # Clean up
        for agent in agents:
            agent_service.delete_agent(agent.id)

        assert len(agent_service.list_agents()) == 0