#!/usr/bin/env python3
"""Backward-compatible smoke entrypoint; all writes stay in a temporary directory."""
from __future__ import annotations

from test_pipeline import main


if __name__ == "__main__":
    raise SystemExit(main())
