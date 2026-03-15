# Binary Install

Use this guide when the user asks how to install, repair, or upgrade the packaged `wenwengu-cli` binary.

## Preferred path in OpenClaw

If the user is running this skill through OpenClaw:

1. Prefer the bundled install helper:
   `python ~/.codex/skills/wenwengu-cli/scripts/install_binary.py`
2. The packaged binary should land under:
   `~/.openclaw/tools/wenwengu-cli/runtime/`
3. The wrappers in this skill will auto-discover that path.

```bash
python ~/.codex/skills/wenwengu-cli/scripts/install_binary.py
python ~/.codex/skills/wenwengu-cli/scripts/check_binary.py
python ~/.codex/skills/wenwengu-cli/scripts/upgrade_binary.py
```

Use the same helpers when the user wants a fully manual path outside OpenClaw.

## Default install locations

- OpenClaw layout:
  `~/.openclaw/tools/wenwengu-cli/runtime/`
- Codex layout:
  `~/.codex/tools/wenwengu-cli/runtime/`

## Release source

The installer downloads from GitHub releases:

- repo: `huliux/wenwengu-cli-skill`
- default channel: `releases/latest/download`

Expected asset names:

- `wenwengu-cli-macos-arm64.tar.gz`
- `wenwengu-cli-macos-x86_64.tar.gz`
- `wenwengu-cli-linux-x86_64.tar.gz`
- `wenwengu-cli-windows-x86_64.zip`

## Natural-language routing

Map these requests to the install helpers:

- `把 skill 装好`
- `安装 wenwengu-cli`
- `检查 CLI 装好了没`
- `升级到最新二进制`
- `修一下这个 skill 的本地安装`

## Reporting style

For install and upgrade flows, report:

1. what path was chosen
2. what binary version or release channel was targeted
3. whether the binary is now runnable

Do not ask the user to set `WENWENGU_CLI_BIN` unless auto-discovery failed.
