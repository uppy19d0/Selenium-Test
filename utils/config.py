from functools import lru_cache
from pathlib import Path

import yaml


DEFAULT_CONFIG = {
    "base_url": "https://plataformavirtual.itla.edu.do",
    "browser": "firefox",
    "headless": False,
    "wait_timeout": 10,
}


@lru_cache()
def load_settings() -> dict:
    """Load YAML config once and merge with sane defaults."""
    config_path = Path(__file__).resolve().parent.parent / "data" / "config.yaml"
    if not config_path.exists():
        return DEFAULT_CONFIG.copy()

    with config_path.open() as stream:
        file_settings = yaml.safe_load(stream) or {}

    merged = {**DEFAULT_CONFIG, **file_settings}
    return merged
