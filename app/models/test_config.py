from pydantic import BaseModel
from typing import Optional, Dict

class TestConfiguration(BaseModel):
    spec_file_content: str
    api_url_override: Optional[str] = None
    llm_engine: str
    llm_engine_temperature: float
    use_cached_graph: bool
    use_cached_q_tables: bool
    rl_agent_learning_rate: float
    rl_agent_discount_factor: float
    rl_agent_max_exploration: float
    time_duration_seconds: int
    mutation_rate: float

class TestResult(BaseModel):
    status: str
    total_requests: int
    failed_requests: int
    coverage: float
    details: Dict
