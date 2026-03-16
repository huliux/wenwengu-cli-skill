# Engine Install

Use this guide when the user asks how to install, repair, or upgrade the packaged `wenwengu-cli` valuation engine.

## Preferred path in OpenClaw

If the user is running this skill through OpenClaw:

1. Prefer the bundled install helper:
   `python scripts/install_engine.py`
2. The packaged engine should land under the platform-managed OpenClaw runtime layout.
3. The wrappers in this skill will auto-discover that path.
4. `doctor.py`, `run_valuation.py`, and `run_cli.py` will also try to auto-install the engine on first use.

```bash
python scripts/install_engine.py
python scripts/check_engine.py
python scripts/upgrade_engine.py
```

Use the same helpers when the user wants a fully manual path outside OpenClaw.

## Tushare token setup in OpenClaw

Recommended:

```bash
openclaw config set skills.entries.wenwengu-cli.apiKey "your_tushare_token"
openclaw config set skills.entries.wenwengu-cli.primaryEnv "TUSHARE_TOKEN"
openclaw gateway restart
```

Alternative explicit env binding:

```bash
openclaw config set skills.entries.wenwengu-cli.env.TUSHARE_TOKEN "your_tushare_token"
openclaw gateway restart
```

Fallback:

```bash
echo 'TUSHARE_TOKEN=your_tushare_token' >> ~/.openclaw/.env
openclaw gateway restart
```

## Default install layouts

- OpenClaw runtime layout
- Codex runtime layout

## Release source

The installer downloads from GitHub releases:

- repo: `huliux/wenwengu-cli-skill`
- default channel: `releases/latest/download`
- fallback channel when no stable release exists yet: `releases/download/edge`

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
- `升级到最新估值引擎`
- `修一下这个 skill 的本地安装`

## Reporting style

For install and upgrade flows, report:

1. what path was chosen
2. what release version or channel was targeted
3. whether the engine is now runnable

Do not ask the user to set `WENWENGU_CLI_BIN` unless auto-discovery failed.
