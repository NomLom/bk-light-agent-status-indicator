from __future__ import annotations


class SessionWatcher:
    """No-op watcher for Hermes mode.

    Claude Code needed a side watcher because ESC could bypass hooks.
    Hermes exposes explicit session-end hooks, so the lamp bridge does not
    need to tail debug logs.
    """

    def sync(self, active_ids: set[str]) -> None:
        del active_ids

    def stop_all(self) -> None:
        return
