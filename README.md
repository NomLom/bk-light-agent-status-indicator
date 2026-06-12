# BK-Light Agent Status Indicator

Turns a BK-Light 32x32 BLE panel into a Hermes Agent status lamp.

What changed from the original Claude Code project:
- the panel runner is still here
- status files can now be written either by a Hermes plugin (hooks fallback) or by a Hermes API/SSE watcher (preferred when you want richer state)
- default status directory is `/tmp/hermes_agent_status`
- config key is now `agent_status:`
- a generic JSON hook script is included for manual tests and other hook-driven agents

States
- idle -> 😴
- thinking -> 🧠
- tool_use -> ⚙️
- permission -> 🔔
- success -> ✅
- failed -> ❌
- cancelled -> ⏹️

How it works
1. Hermes plugin hooks or Hermes API/SSE events observe session/tool/approval lifecycle.
2. The selected bridge writes one state file per active session.
3. `python run.py` watches those files and pushes the corresponding image to the BK-Light panel.
4. Multiple sessions split across the panel as a 2x2 grid.

Requirements
- Python 3.11+
- BK-Light 32x32 panel
- Hermes Agent
- BLE support for the host

Repository layout
- `plugin.yaml` + `__init__.py`: Hermes plugin entrypoint
- `agent_status/hermes_plugin.py`: Hermes hook bridge
- `agent_status/api_bridge.py`: Hermes API/SSE bridge
- `agent_status/runner.py`: panel watcher / renderer
- `scripts/install_hermes_plugin.sh`: symlink this repo into `~/.hermes/plugins/` and enable it
- `scripts/status_file_hook.py`: generic hook-driven JSON -> state-file bridge

Install
```bash
git clone --recurse-submodules <your-repo-url>
cd bk-light-agent-status-indicator

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
bash scripts/install_hermes_plugin.sh
```

If you prefer manual plugin install:
```bash
mkdir -p ~/.hermes/plugins
ln -s /ABS/PATH/TO/bk-light-agent-status-indicator ~/.hermes/plugins/bk-light-status
hermes plugins enable bk-light-status
```

Panel config
Edit `config.local.yaml` or `config.yaml`:
```yaml
device:
  address: "F0:27:3C:1A:8B:C3"

agent_status:
  status_dir: "/tmp/hermes_agent_status"
  stale_threshold: 3600
  statuses:
    idle: "😴"
    thinking: "🧠"
    tool_use: "⚙️"
    permission: "🔔"
    success: "✅"
    failed: "❌"
    cancelled: "⏹️"
```

Run the lamp
```bash
source .venv/bin/activate
python run.py
```

API-first bridge
Use this when you are driving Hermes through its API server and want richer state transitions.

Create a run and mirror its state to the lamp files:
```bash
python3 -m agent_status.api_bridge run \
  --base-url http://127.0.0.1:8642 \
  --api-key "$API_SERVER_KEY" \
  --session-id lamp-demo \
  "Use the terminal tool to run `hostname` and then reply DONE."
```

Attach to an existing run id:
```bash
python3 -m agent_status.api_bridge watch <run_id> \
  --base-url http://127.0.0.1:8642 \
  --api-key "$API_SERVER_KEY" \
  --session-id lamp-demo
```

Find the panel address
```bash
python3 Bk-Light-AppBypass/scripts/scan_macos.py
```

Hermes hook mapping used by the plugin
- `on_session_start` -> idle
- `pre_llm_call` -> thinking
- `pre_tool_call` -> tool_use
- `post_tool_call` -> thinking (or stays tool_use if nested)
- `pre_approval_request` -> permission
- `post_approval_response` -> thinking / tool_use
- `post_llm_call` -> idle
- `on_session_end` -> idle
- `on_session_finalize` / `on_session_reset` -> remove state file

Manual tests
Write a fake state file:
```bash
mkdir -p /tmp/hermes_agent_status
echo thinking > /tmp/hermes_agent_status/test-session-1
```

Test the generic JSON hook script:
```bash
echo '{"hook_event_name":"PreToolUse","session_id":"test-1","tool_name":"Bash"}' \
  | python3 scripts/status_file_hook.py
cat /tmp/hermes_agent_status/test-1
```

Test the Hermes plugin locally without the panel:
```bash
rm -rf /tmp/hermes_agent_status
hermes -z "Use the read_file tool on /etc/hostname and then tell me the hostname." --toolsets file
find /tmp/hermes_agent_status -maxdepth 1 -type f -print -exec cat {} \;
```

Approval test
Run a command that requires approval without `-z`/`--yolo`, for example in interactive Hermes:
```text
run `rm -rf /tmp/definitely-not-real` and deny it
```
The lamp should flip to `permission` while Hermes waits.

Verified API/SSE flow
- `thinking` -> `tool_use` -> `permission` was observed live against a loopback Hermes API server.
- After approval response (`choice=once`), the run completed successfully and returned `DONE`.

Notes
- Hermes one-shot mode (`-z`) auto-bypasses approvals, so it will not exercise `permission` on the hook path.
- The API/SSE bridge can surface richer live states, including `success`, `failed`, and `cancelled`.
- The plugin uses `BK_LIGHT_STATUS_DIR` if you want a different state directory.
- The runner also accepts the legacy `claude_status:` config block for compatibility, but new config should use `agent_status:`.

Troubleshooting
- Plugin not loading: run `hermes plugins list` and confirm `bk-light-status` is enabled.
- No state files: check `~/.hermes/logs/agent.log` for plugin import errors.
- Panel not updating: verify the BLE address and keep the panel powered/on-range.
- Emoji missing on Linux: install `fonts-noto-color-emoji`.

Acknowledgements
Built on top of `Bk-Light-AppBypass` and inspired by `bk-light-claude-code-status-indicator`.
