import os
import yaml
from pathlib import Path

DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "configs" / "amis.yaml"


class Config:
    def __init__(self, config_path: str | Path = None):
        path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
        with open(path) as f:
            raw = yaml.safe_load(f)
        self._raw = raw
        self.paths = ConfigPaths(raw.get("paths", {}))
        self.llm = ConfigLLM(raw.get("llm", {}))
        self.embedding = ConfigEmbedding(raw.get("embedding", {}))
        self.ingestion = ConfigIngestion(raw.get("ingestion", {}))
        self.analysis = ConfigAnalysis(raw.get("analysis", {}))

    @property
    def content_dir(self) -> Path:
        return Path(self.paths.content_dir)

    @property
    def db_path(self) -> str:
        return str(self.paths.db_path)


class ConfigPaths:
    def __init__(self, data: dict):
        self.content_dir = data.get("content_dir", "content/posts")
        self.db_path = data.get("db_path", "database/sqlite.db")
        self.chroma_dir = data.get("chroma_dir", "chroma")
        self.graph_dir = data.get("graph_dir", "graph")
        self.campaigns_dir = data.get("campaigns_dir", "campaigns")
        self.analytics_dir = data.get("analytics_dir", "analytics")
        self.generated_dir = data.get("generated_dir", "generated")
        self.logs_dir = data.get("logs_dir", "logs")


class ConfigLLM:
    def __init__(self, data: dict):
        self.provider = data.get("provider", "ollama")
        self.model = data.get("model", "llama3.1:8b")
        self.base_url = data.get("base_url", "http://localhost:11434")
        self.temperature = data.get("temperature", 0.3)
        self.max_tokens = data.get("max_tokens", 4096)


class ConfigEmbedding:
    def __init__(self, data: dict):
        self.provider = data.get("provider", "sentence-transformers")
        self.model = data.get("model", "all-MiniLM-L6-v2")


class ConfigIngestion:
    def __init__(self, data: dict):
        self.batch_size = data.get("batch_size", 10)
        self.overwrite_existing = data.get("overwrite_existing", True)
        self.extract_images = data.get("extract_images", True)
        self.extract_code_blocks = data.get("extract_code_blocks", True)


class ConfigAnalysis:
    def __init__(self, data: dict):
        self.parallel_scoring = data.get("parallel_scoring", True)
        self.confidence_threshold = data.get("confidence_threshold", 0.7)
        self.max_retries = data.get("max_retries", 2)
