#!/usr/bin/env python3
"""Compat entrypoint: delegates to Claude/scripts/sync_claude_skills.py."""
import runpy
import sys
from pathlib import Path

sys.argv[0] = str(Path(__file__).resolve().parents[1] / "Claude" / "scripts" / "sync_claude_skills.py")
runpy.run_path(sys.argv[0], run_name="__main__")
