from pydantic import BaseModel

class AgentConfig(BaseModel):
    name: str
    role: str
    tools: list[str]
    memory_config: dict | None = None
    max_iterations: int = 10