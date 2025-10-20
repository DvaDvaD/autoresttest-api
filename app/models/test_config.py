from pydantic import BaseModel
from typing import Optional, Dict


class TestConfiguration(BaseModel):
    spec_file_content: str
    api_url_override: Optional[str] = None
    llm_engine: str = "gemini-2.0-flash-lite"
    llm_engine_temperature: float = 0.1
    use_cached_graph: bool = True
    use_cached_q_tables: bool = True
    rl_agent_learning_rate: float = 0.1
    rl_agent_discount_factor: float = 0.9
    rl_agent_max_exploration: float = 1.0
    time_duration_seconds: int = 5
    mutation_rate: float = 0.2


class TestRunRequest(BaseModel):
    job_id: str
    config: TestConfiguration


class TestResult(BaseModel):
    status: str
    total_requests: int
    failed_requests: int
    coverage: float
    details: Dict


class TestRunResult(BaseModel):
    summary: Dict
    raw_file_urls: Dict
    config: TestConfiguration
