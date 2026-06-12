#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLUGIN_DIR="$HOME/.hermes/plugins/bk-light-status"

mkdir -p "$HOME/.hermes/plugins"
rm -rf "$PLUGIN_DIR"
ln -s "$REPO_ROOT" "$PLUGIN_DIR"

hermes plugins enable bk-light-status

echo "Installed plugin symlink: $PLUGIN_DIR -> $REPO_ROOT"
echo "Status files will be written to: ${BK_LIGHT_STATUS_DIR:-/tmp/hermes_agent_status}"
