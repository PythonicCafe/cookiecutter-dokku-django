import os

import pytest


def pytest_collect_file(filename, parent):
    """Hook to intercept pytest file collect"""
    config = str(os.environ.get("PYTEST_DEBUG_COLLECT") or "").strip().lower()
    if config in ("true", "on", "1"):
        print(f"Collecting tests from {file_path}")

    return None  # Will continue the regular collect mechanism
