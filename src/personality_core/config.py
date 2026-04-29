from pathlib import Path
import os

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = Path.cwd()
DEFAULT_CORES_DIR = REPO_ROOT / "cores"
DEFAULT_PERSONALITIES_DIR = REPO_ROOT / "personalities"
DEFAULT_MODEL_PROFILES_DIR = REPO_ROOT / "model_profiles"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
