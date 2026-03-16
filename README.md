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

- Runtime configuration such as `TUSHARE_TOKEN` is provided at runtime.
- The public CLI is valuation-only and uses Tushare as its data source.
- The packaged valuation engine is not embedded in the skill files themselves; it is distributed via GitHub Releases.

## Tushare Token Setup (OpenClaw)

Recommended setup:

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

Fallback for shell/service environments:

```bash
echo 'TUSHARE_TOKEN=your_tushare_token' >> ~/.openclaw/.env
openclaw gateway restart
```

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
