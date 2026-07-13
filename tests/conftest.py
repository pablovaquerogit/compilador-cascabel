"""Configuración común para las pruebas del compilador Cascabel."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMPILER_DIR = PROJECT_ROOT / "CascabelCompilator_v1.1"

if str(COMPILER_DIR) not in sys.path:
    sys.path.insert(0, str(COMPILER_DIR))
