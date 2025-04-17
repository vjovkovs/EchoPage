# echopage/utils.py

import os
import re
import time
from pathlib import Path
from typing import List, Callable, Any, Dict
from dotenv import load_dotenv

load_dotenv()

def ensure_dir(path: Path) -> None:
    """
    Ensure that a directory exists.
    Usage: call before writing any files there.
    """
    path.mkdir(parents=True, exist_ok=True)


def sanitize_filename(name: str, max_length: int = 100) -> str:
    """
    Turn an arbitrary string into a filesystem‑safe filename.
    - Strips invalid chars, collapses whitespace, truncates if needed.
    """
    # Remove path separators and illegal chars
    name = re.sub(r'[\\/:"*?<>|]+', "", name)
    # Collapse whitespace
    name = re.sub(r"\s+", "_", name).strip("_")
    return name[:max_length]


def chunk_text(text: str, max_chars: int = 4500) -> List[str]:
    """
    Split a long text into chunks no longer than max_chars, breaking on sentence boundaries.
    Helps avoid TTS service limits on input size.
    """
    sentences = re.split(r'(?<=[.?!])\s+', text)
    chunks: List[str] = []
    current: List[str] = []
    length = 0

    for sent in sentences:
        if length + len(sent) + 1 > max_chars:
            chunks.append(" ".join(current))
            current, length = [], 0
        current.append(sent)
        length += len(sent) + 1

    if current:
        chunks.append(" ".join(current))
    return chunks


def load_env_vars(required: List[str]) -> Dict[str, str]:
    """
    Validates that all required ENV vars are set; returns a dict of their values.
    Throws a RuntimeError listing any that are missing.
    """
    missing = [var for var in required if not os.getenv(var)]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")
    return {var: os.getenv(var) for var in required}


def timed(fn: Callable) -> Callable:
    """
    Decorator to measure and log execution time of functions.
    Usage:
        @timed
        def my_func(...):
            ...
    """
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.time()
        result = fn(*args, **kwargs)
        end = time.time()
        print(f"[TIMING] {fn.__name__} took {end - start:.2f}s")
        return result
    return wrapper
