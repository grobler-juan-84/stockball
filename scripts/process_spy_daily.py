"""Backward-compatible wrapper: process SPY via process_tiingo_daily.py.

Prefer:
  .venv\\Scripts\\python.exe scripts\\process_tiingo_daily.py SPY
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

script = Path(__file__).resolve().parent / "process_tiingo_daily.py"
raise SystemExit(subprocess.call([sys.executable, str(script), "SPY", *sys.argv[1:]]))
