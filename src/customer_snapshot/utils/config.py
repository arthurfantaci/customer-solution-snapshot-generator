"""
Configuration management for Customer Snapshot Generator.
"""
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

class Config:
    """Application configuration with secure defaults."""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            env_file: Path to .env file (optional)
        """
        # Load environment variables
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        # Base directories
        self.base_dir = Path(__file__).parent.parent.parent.parent
        self.src_dir = self.base_dir / "src"
        self.data_dir = self.base_dir / "data"
        self.input_dir = self.data_dir / "input"
        self.output_dir = self.data_dir / "output"
        self.templates_dir = self.data_dir / "templates"
        
        # Create directories if they don't exist
        self._ensure_directories()
        
        # API Keys
        self.anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
        self.voyage_api_key: Optional[str] = os.getenv("VOYAGEAI_API_KEY")
        self.tavily_api_key: Optional[str] = os.getenv("TAVILY_API_KEY")
        
        # Model settings
        self.default_model = os.getenv("DEFAULT_MODEL", "claude-3-5-sonnet-20240620")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "4000"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.0"))
        
        # File processing settings
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE", str(50 * 1024 * 1024)))  # 50MB
        self.allowed_extensions = os.getenv("ALLOWED_EXTENSIONS", ".vtt,.txt,.md").split(",")
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "500"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "100"))
        
        # Logging settings
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # Security settings
        self.enable_file_validation = os.getenv("ENABLE_FILE_VALIDATION", "true").lower() == "true"
        self.sanitize_filenames = os.getenv("SANITIZE_FILENAMES", "true").lower() == "true"
        
        # NLP settings
        self.spacy_model = os.getenv("SPACY_MODEL", "en_core_web_sm")
        self.min_entity_frequency = int(os.getenv("MIN_ENTITY_FREQUENCY", "2"))
        self.min_entity_length = int(os.getenv("MIN_ENTITY_LENGTH", "3"))
    
    def _ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        directories = [
            self.data_dir,
            self.input_dir,
            self.output_dir,
            self.templates_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> None:
        """Validate required configuration."""
        errors = []
        
        if not self.anthropic_api_key:
            errors.append("ANTHROPIC_API_KEY is required")
        
        if self.max_tokens <= 0:
            errors.append("MAX_TOKENS must be positive")
        
        if self.temperature < 0 or self.temperature > 1:
            errors.append("TEMPERATURE must be between 0 and 1")
        
        if self.max_file_size <= 0:
            errors.append("MAX_FILE_SIZE must be positive")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding sensitive data)."""
        return {
            "default_model": self.default_model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "max_file_size": self.max_file_size,
            "allowed_extensions": self.allowed_extensions,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "log_level": self.log_level,
            "debug": self.debug,
            "spacy_model": self.spacy_model,
            "min_entity_frequency": self.min_entity_frequency,
            "min_entity_length": self.min_entity_length,
            "api_keys_configured": {
                "anthropic": bool(self.anthropic_api_key),
                "voyage": bool(self.voyage_api_key),
                "tavily": bool(self.tavily_api_key)
            }
        }
    
    @classmethod
    def from_env_file(cls, env_file: str) -> 'Config':
        """Create configuration from specific .env file."""
        return cls(env_file=env_file)
    
    @classmethod
    def get_default(cls) -> 'Config':
        """Get default configuration."""
        return cls()