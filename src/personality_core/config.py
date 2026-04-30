from pathlib import Path
import os

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = Path.cwd()

def _asset_dir(env_name: str, dirname: str) -> Path:
    override = os.getenv(env_name)
    if override:
        return Path(override).expanduser()
    cwd_path = REPO_ROOT / dirname
    if cwd_path.exists():
        return cwd_path
    package_path = PACKAGE_ROOT / dirname
    if package_path.exists():
        return package_path
    return cwd_path

DEFAULT_CORES_DIR = _asset_dir("PERSONALITY_CORE_CORES_DIR", "cores")
DEFAULT_PERSONALITIES_DIR = _asset_dir("PERSONALITY_CORE_PERSONALITIES_DIR", "personalities")
DEFAULT_MODEL_PROFILES_DIR = _asset_dir("PERSONALITY_CORE_MODEL_PROFILES_DIR", "model_profiles")
DEFAULT_MODEL = os.getenv("PERSONALITY_CORE_DEFAULT_MODEL", "ollama/gemma4:e4b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "300"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_TIMEOUT = float(os.getenv("OPENAI_TIMEOUT", "300"))
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "")
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "Personality Core")
LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://127.0.0.1:1234/v1")
