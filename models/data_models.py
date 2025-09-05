"""
models/data_models.py
Complete data models and configuration classes
"""
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from urllib.parse import urlparse
from pathlib import Path

class PhaseStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class DataProduct:
    """Represents a data product in the backlog"""
    id: str
    name: str
    description: str
    priority: str
    business_value: str
    data_sources: List[str]
    stakeholders: List[str]
    requirements: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

@dataclass
class DataLineage:
    """Represents data lineage information"""
    source_table: str
    target_table: str
    transformation_logic: str
    dependencies: List[str]
    last_updated: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

@dataclass
class DataQualityMetrics:
    """Data quality assessment metrics"""
    table_name: str
    completeness: float
    accuracy: float
    consistency: float
    validity: float
    uniqueness: float
    timeliness: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

@dataclass
class ExecutionResult:
    """Represents execution result of a phase or task"""
    phase: str
    status: PhaseStatus
    start_time: datetime
    end_time: Optional[datetime]
    output: str
    metrics: Dict[str, Any]
    errors: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

class PlatformConfig:
    """Configuration for the platform"""
    
    def __init__(self):
        # Default DB URLs (only valid SQLite URIs will be kept)
        default_urls = "sqlite:///databases/ecommerce_db.db"
        raw_urls = os.getenv("DATABASE_URLS", default_urls).split(",")
        
         # Filter valid sqlite:/// URIs with .db suffix
        self.database_urls = [
            u.strip() for u in raw_urls
            if u.startswith("sqlite:///") and Path(urlparse(u).path).suffix == ".db"
        ]
        
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        self.data_catalog_path = os.getenv("DATA_CATALOG_PATH", "./data_catalog")
        self.results_path = os.getenv("RESULTS_PATH", "./results")
        self.cache_enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        self.max_concurrent_tasks = int(os.getenv("MAX_CONCURRENT_TASKS", "5"))
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Data quality thresholds
        self.quality_thresholds = {
            "completeness": float(os.getenv("COMPLETENESS_THRESHOLD", "0.95")),
            "accuracy": float(os.getenv("ACCURACY_THRESHOLD", "0.98")),
            "consistency": float(os.getenv("CONSISTENCY_THRESHOLD", "0.95")),
            "validity": float(os.getenv("VALIDITY_THRESHOLD", "0.99")),
            "uniqueness": float(os.getenv("UNIQUENESS_THRESHOLD", "0.95")),
            "timeliness": float(os.getenv("TIMELINESS_THRESHOLD", "0.90"))
        }
        
        # Performance settings
        self.query_timeout = int(os.getenv("QUERY_TIMEOUT", "300"))
        self.cache_ttl = int(os.getenv("CACHE_TTL", "3600"))
        self.batch_size = int(os.getenv("BATCH_SIZE", "1000"))
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "database_urls": self.database_urls,
            "data_catalog_path": self.data_catalog_path,
            "results_path": self.results_path,
            "cache_enabled": self.cache_enabled,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "log_level": self.log_level,
            "quality_thresholds": self.quality_thresholds,
            "query_timeout": self.query_timeout,
            "cache_ttl": self.cache_ttl,
            "batch_size": self.batch_size
        }