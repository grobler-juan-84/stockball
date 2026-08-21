"""Backward-compatible wrapper: download SPY via download_tiingo_daily.py.

Prefer:
  .venv\\Scripts\\python.exe scripts\\download_tiingo_daily.py SPY
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

script = Path(__file__).resolve().parent / "download_tiingo_daily.py"
# Preserve historical SPY request window used for the first raw download.
cmd = [sys.executable, str(script), "SPY", "--start-date", "1993-01-29", *sys.argv[1:]]
raise SystemExit(subprocess.call(cmd))
