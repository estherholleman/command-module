#!/usr/bin/env python3
"""Compatibility entry point: report only; automatic clock closure is retired."""
# CLOCK_CHECK_REPORT_ONLY: old cron/manual callers are non-destructive too.
import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("clock-check.py")), run_name="__main__")
