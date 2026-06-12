#!/usr/bin/env python3
"""Backward-compatible wrapper for the generic status-file hook.

Kept so old docs or local shell snippets do not break immediately.
New installs should use scripts/status_file_hook.py.
"""

from status_file_hook import main

if __name__ == "__main__":
    main()
