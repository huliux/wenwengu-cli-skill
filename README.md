# wenwengu-cli-skill

Public distribution repository for the `wenwengu-cli` skill.

This repository is intentionally minimal. It contains:

- the publishable `wenwengu-cli` skill
- installation and usage references
- GitHub Releases with packaged `wenwengu-cli` binaries

The implementation source and CLI build pipeline live in a separate private repository.
Release assets are built upstream and then published into this repository.

## Install

### OpenClaw

Install the skill, then run the bundled installer so the binary lands in the
OpenClaw runtime layout:

```bash
python scripts/install_binary.py
python scripts/check_binary.py
```

The installer downloads the latest packaged binary from this repository's
GitHub Releases and places it under `~/.openclaw/tools/wenwengu-cli/runtime/`
by default.

### Manual

You can also install with the bundled helper script:

```bash
python scripts/install_binary.py
python scripts/check_binary.py
```

## Release assets

Expected asset names:

- `wenwengu-cli-macos-arm64.tar.gz`
- `wenwengu-cli-macos-x86_64.tar.gz`
- `wenwengu-cli-linux-x86_64.tar.gz`
- `wenwengu-cli-windows-x86_64.zip`

## Notes

- Runtime configuration such as `TUSHARE_TOKEN`, database credentials, and LLM API keys are still provided at runtime via environment variables or `.env`.
- The packaged binary is not embedded in the skill files themselves; it is distributed via GitHub Releases.
