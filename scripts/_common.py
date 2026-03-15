#!/usr/bin/env python3
"""Shared helpers for wenwengu-cli skill wrappers."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence

from binary_manager import find_installed_binary
from result_summary import summarize_payload


def normalize_cli_args(raw_args: Sequence[str]) -> list[str]:
    args = list(raw_args)
    if args and args[0] == "--":
        return args[1:]
    return args


def ensure_output(cli_args: Sequence[str], default_output: str = "json") -> list[str]:
    args = list(cli_args)
    if get_output_mode(args) is not None:
        return args
    return [*args, "--output", default_output]


def ensure_json_output(cli_args: Sequence[str]) -> list[str]:
    args = list(cli_args)
    output_mode = get_output_mode(args)
    if output_mode is None:
        return [*args, "--output", "json"]
    if output_mode != "json":
        raise SystemExit("--summarize requires JSON output. Omit --output or use --output json.")
    return args


def get_output_mode(cli_args: Sequence[str]) -> str | None:
    args = list(cli_args)
    for index, arg in enumerate(args):
        if arg == "--output" and index + 1 < len(args):
            return args[index + 1]
        if arg.startswith("--output="):
            return arg.split("=", 1)[1]
    return None


def resolve_repo_root(explicit_repo: str | None, *, required: bool = True) -> Path | None:
    repo_hint = explicit_repo or os.getenv("WENWENGU_CLI_REPO")
    if repo_hint:
        repo_root = Path(repo_hint).expanduser().resolve()
        assert_wenwengu_repo(repo_root)
        return repo_root

    current = Path.cwd().resolve()
    for candidate in [current, *current.parents]:
        pyproject = candidate / "pyproject.toml"
        if not pyproject.exists():
            continue
        try:
            content = pyproject.read_text(encoding="utf-8")
        except OSError:
            continue
        if 'name = "wenwengu"' in content:
            return candidate

    if required:
        raise SystemExit(
            "Unable to locate the wenwengu repository. Pass --repo /path/to/"
            "stock_vale_valuation_3.0 or set WENWENGU_CLI_REPO."
        )
    return None


def resolve_binary(explicit_bin: str | None) -> Path | None:
    candidate = find_installed_binary(explicit_path=explicit_bin)
    if candidate is None:
        if explicit_bin or os.getenv("WENWENGU_CLI_BIN"):
            binary_hint = explicit_bin or os.getenv("WENWENGU_CLI_BIN")
            raise SystemExit(
                "Configured wenwengu-cli binary was not found: "
                f"{Path(str(binary_hint)).expanduser().resolve()}"
            )
        return None
    return candidate.path


def run_wenwengu_cli(
    cli_args: Sequence[str],
    *,
    explicit_repo: str | None = None,
    explicit_bin: str | None = None,
) -> int:
    command, cwd = build_wenwengu_command(
        cli_args,
        explicit_repo=explicit_repo,
        explicit_bin=explicit_bin,
    )
    completed = subprocess.run(command, cwd=cwd, check=False)
    return completed.returncode


def capture_wenwengu_cli(
    cli_args: Sequence[str],
    *,
    explicit_repo: str | None = None,
    explicit_bin: str | None = None,
) -> subprocess.CompletedProcess[str]:
    command, cwd = build_wenwengu_command(
        cli_args,
        explicit_repo=explicit_repo,
        explicit_bin=explicit_bin,
    )
    return subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )


def run_with_optional_summary(
    subcommand: str,
    cli_args: Sequence[str],
    *,
    expected_kind: str,
    summarize: bool,
    explicit_repo: str | None = None,
    explicit_bin: str | None = None,
) -> int:
    if not summarize:
        return run_wenwengu_cli(
            [subcommand, *ensure_output(cli_args, default_output="json")],
            explicit_repo=explicit_repo,
            explicit_bin=explicit_bin,
        )

    completed = capture_wenwengu_cli(
        [subcommand, *ensure_json_output(cli_args)],
        explicit_repo=explicit_repo,
        explicit_bin=explicit_bin,
    )
    return emit_summary_from_completed(completed, expected_kind=expected_kind)


def emit_summary_from_completed(
    completed: subprocess.CompletedProcess[str],
    *,
    expected_kind: str,
) -> int:
    if completed.stderr:
        sys.stderr.write(completed.stderr)

    if completed.returncode != 0:
        if completed.stdout:
            sys.stdout.write(completed.stdout)
        return completed.returncode

    payload = parse_json_payload(completed.stdout)
    print(summarize_payload(payload, kind=expected_kind))
    return 0


def parse_json_payload(raw_output: str):
    cleaned_output = raw_output.strip()
    if not cleaned_output:
        raise SystemExit("The CLI returned no JSON output to summarize.")

    try:
        return json.loads(cleaned_output)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Failed to parse CLI JSON output: {exc}") from exc


def split_override(item: str) -> tuple[str, str]:
    if "=" not in item:
        raise SystemExit(f"Invalid override '{item}'. Expected KEY=VALUE.")
    key, value = item.split("=", 1)
    key = key.strip()
    if not key:
        raise SystemExit(f"Invalid override '{item}'. Empty key.")
    return key, value.strip()


def parse_override_value(raw_value: str):
    lowered = raw_value.lower()
    if lowered in {"true", "false", "null"}:
        return json.loads(lowered)

    try:
        return json.loads(raw_value)
    except json.JSONDecodeError:
        return raw_value


def set_nested_value(payload: dict, dotted_key: str, value) -> None:
    current = payload
    parts = dotted_key.split(".")
    for part in parts[:-1]:
        existing = current.get(part)
        if not isinstance(existing, dict):
            existing = {}
            current[part] = existing
        current = existing
    current[parts[-1]] = value


def validate_request_payload(
    payload: dict,
    *,
    explicit_repo: str | None = None,
) -> dict:
    repo_root = resolve_repo_root(explicit_repo, required=True)
    command = [
        "uv",
        "run",
        "--project",
        str(repo_root),
        "python",
        "-c",
        (
            "import json, sys; "
            "from src.api.models import StockValuationRequest; "
            "payload = json.load(sys.stdin); "
            "request = StockValuationRequest.model_validate(payload); "
            "print(request.model_dump_json(indent=2, exclude_none=False))"
        ),
    ]
    completed = subprocess.run(
        command,
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        input=json.dumps(payload, ensure_ascii=False),
    )
    if completed.returncode != 0:
        error_output = completed.stderr.strip() or completed.stdout.strip()
        raise SystemExit(f"Request validation failed: {error_output}")
    return parse_json_payload(completed.stdout)


def materialize_default_request(
    ts_code: str,
    *,
    explicit_repo: str | None = None,
) -> dict:
    return validate_request_payload({"ts_code": ts_code}, explicit_repo=explicit_repo)


def create_temp_request_file(payload: dict) -> Path:
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        prefix="wenwengu-request-",
        delete=False,
        encoding="utf-8",
    ) as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
        return Path(handle.name)


def build_wenwengu_command(
    cli_args: Sequence[str],
    *,
    explicit_repo: str | None = None,
    explicit_bin: str | None = None,
) -> tuple[list[str], Path]:
    binary_path = resolve_binary(explicit_bin)
    repo_root = resolve_repo_root(explicit_repo, required=binary_path is None)
    cwd = repo_root or Path.cwd()

    if binary_path is not None:
        command = [str(binary_path), *cli_args]
    else:
        if repo_root is None:
            raise SystemExit(
                "Unable to locate a packaged wenwengu-cli binary or repo checkout. "
                "If you are using OpenClaw, install the binary into "
                "~/.openclaw/tools/wenwengu-cli/runtime/ via the Skills UI or "
                "run scripts/install_binary.py."
            )
        command = ["uv", "run", "--project", str(repo_root), "wenwengu-cli", *cli_args]

    return command, cwd


def assert_wenwengu_repo(repo_root: Path) -> None:
    pyproject = repo_root / "pyproject.toml"
    if not pyproject.exists():
        raise SystemExit(f"pyproject.toml not found under {repo_root}")

    try:
        content = pyproject.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"Unable to read {pyproject}: {exc}") from exc

    if 'name = "wenwengu"' not in content:
        raise SystemExit(f"{repo_root} does not look like the wenwengu repository")
