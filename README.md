# wenwengu-cli-skill

Public distribution repository for the `wenwengu-cli` skill.

This repository is intentionally minimal. It contains:

- the publishable `wenwengu-cli` skill
- installation and usage references
- ready-to-edit `request.json` templates
- GitHub Releases with packaged `wenwengu-cli` valuation engines

Release assets are built in CI and then published into this repository.

## Install

### OpenClaw

Install the skill, then either run the bundled installer or let the first real
command auto-install the valuation engine into the OpenClaw runtime layout:

```bash
python scripts/install_engine.py
python scripts/check_engine.py
```

The installer downloads the latest packaged engine from this repository's
GitHub Releases and places it into the platform-managed runtime layout by
default.

### Manual

You can also install with the bundled helper script:

```bash
python scripts/install_engine.py
python scripts/check_engine.py
```

## Release assets

Expected asset names:

- `wenwengu-cli-macos-arm64.tar.gz`
- `wenwengu-cli-macos-x86_64.tar.gz`
- `wenwengu-cli-linux-x86_64.tar.gz`
- `wenwengu-cli-windows-x86_64.zip`

## Notes

- Runtime configuration is provided at runtime.
- The public CLI is valuation-only and can read from a user-configured database or Tushare.
- The packaged valuation engine is not embedded in the skill files themselves; it is distributed via GitHub Releases.

## Database Setup (OpenClaw)

Recommended setup:

```bash
openclaw config set skills.entries.wenwengu-cli.primaryEnv "DATABASE_URL"
openclaw config set skills.entries.wenwengu-cli.env.DATABASE_URL "postgresql://user:password@host:5432/dbname"
openclaw config set skills.entries.wenwengu-cli.env.DATA_SOURCE "postgres"
openclaw gateway restart
```

Alternative Tushare setup:

```bash
openclaw config set skills.entries.wenwengu-cli.env.TUSHARE_TOKEN "your_tushare_token"
openclaw config set skills.entries.wenwengu-cli.env.DATA_SOURCE "tushare"
openclaw gateway restart
```

Fallback for shell/service environments:

```bash
echo 'DATABASE_URL=postgresql://user:password@host:5432/dbname' >> ~/.openclaw/.env
echo 'DATA_SOURCE=postgres' >> ~/.openclaw/.env
openclaw gateway restart
```

After changing skill env or `~/.openclaw/.env`, start a new OpenClaw session
to avoid stale environment snapshots.

## Templates

Starter valuation templates live under:

- `templates/request/base_request.json`
- `templates/request/conservative_request.json`
- `templates/request/sensitivity_wacc_exit_standard.json`
- `templates/request/ui_full_example.json`

Copy one of these, adjust the stock code and assumptions, then run:

```bash
python scripts/run_valuation.py --request-file ./templates/request/base_request.json --output json --save-json ./outputs/result.json
```

## OpenClaw Agent Quick Prompts

In OpenClaw chat, users can directly say:

- `先检查一下这个估值 skill 能不能跑`
- `给这只股票跑一个标准估值`
- `给这只股票按高增长口径做 DCF，并做敏感性分析`
- `比较一下基准和保守结果`

`<ts_code>` is a placeholder in docs/examples. Replace it with a real stock code before execution.

The skill will translate natural language into wrapper commands and return
analysis-first summaries by default.
