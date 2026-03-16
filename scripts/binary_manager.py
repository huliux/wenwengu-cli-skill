#!/usr/bin/env python3
"""Engine install and discovery helpers for the wenwengu-cli skill."""

from __future__ import annotations

import json
import os
import platform
import shutil
import stat
import tarfile
import tempfile
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path


DEFAULT_REPO_SLUG = os.getenv("WENWENGU_RELEASE_SOURCE", "huliux/wenwengu-cli-skill")
DEFAULT_SKILL_KEY = "wenwengu-cli"


@dataclass(frozen=True)
class AssetSpec:
    asset_name: str
    archive_type: str
    binary_name: str
    platform_label: str


@dataclass(frozen=True)
class BinaryCandidate:
    source: str
    path: Path


def resolve_asset_spec(
    system_name: str | None = None,
    machine_name: str | None = None,
) -> AssetSpec:
    system_name = (system_name or platform.system()).strip().lower()
    machine_name = (machine_name or platform.machine()).strip().lower()

    if system_name == "darwin":
        if machine_name in {"arm64", "aarch64"}:
            return AssetSpec(
                asset_name="wenwengu-cli-macos-arm64.tar.gz",
                archive_type="tar.gz",
                binary_name="wenwengu-cli",
                platform_label="macOS arm64",
            )
        if machine_name in {"x86_64", "amd64"}:
            return AssetSpec(
                asset_name="wenwengu-cli-macos-x86_64.tar.gz",
                archive_type="tar.gz",
                binary_name="wenwengu-cli",
                platform_label="macOS x86_64",
            )
    elif system_name == "linux":
        if machine_name in {"x86_64", "amd64"}:
            return AssetSpec(
                asset_name="wenwengu-cli-linux-x86_64.tar.gz",
                archive_type="tar.gz",
                binary_name="wenwengu-cli",
                platform_label="Linux x86_64",
            )
    elif system_name in {"windows", "win32"}:
        if machine_name in {"x86_64", "amd64"}:
            return AssetSpec(
                asset_name="wenwengu-cli-windows-x86_64.zip",
                archive_type="zip",
                binary_name="wenwengu-cli.exe",
                platform_label="Windows x86_64",
            )

    raise SystemExit(
        "Unsupported platform for packaged wenwengu-cli engine: "
        f"{system_name}/{machine_name}"
    )


def default_openclaw_runtime_dir() -> Path:
    return Path.home() / ".openclaw" / "tools" / DEFAULT_SKILL_KEY / "runtime"


def default_codex_runtime_dir() -> Path:
    return Path.home() / ".codex" / "tools" / DEFAULT_SKILL_KEY / "runtime"


def detect_preferred_layout() -> str:
    script_path = Path(__file__).expanduser().resolve()
    script_text = str(script_path)
    if "/.openclaw/" in script_text:
        return "openclaw"
    if "/.codex/" in script_text:
        return "codex"
    if (Path.home() / ".openclaw").exists():
        return "openclaw"
    return "codex"


def build_release_url(
    *,
    repo_slug: str = DEFAULT_REPO_SLUG,
    version: str = "latest",
    asset_name: str,
) -> str:
    if version == "latest":
        return f"https://github.com/{repo_slug}/releases/latest/download/{asset_name}"
    return f"https://github.com/{repo_slug}/releases/download/{version}/{asset_name}"


def resolve_install_dir(layout: str) -> Path:
    normalized = layout.strip().lower()
    if normalized == "openclaw":
        return default_openclaw_runtime_dir()
    if normalized == "codex":
        return default_codex_runtime_dir()
    raise SystemExit(f"Unsupported install layout: {layout}")


def resolve_binary_candidates(
    explicit_path: str | None = None,
) -> list[BinaryCandidate]:
    candidates: list[BinaryCandidate] = []

    if explicit_path:
        candidates.append(
            BinaryCandidate("explicit", Path(explicit_path).expanduser().resolve())
        )

    env_bin = os.getenv("WENWENGU_CLI_BIN")
    if env_bin:
        candidates.append(
            BinaryCandidate(
                "env:WENWENGU_CLI_BIN", Path(env_bin).expanduser().resolve()
            )
        )

    asset_spec = resolve_asset_spec()
    candidates.extend(
        [
            BinaryCandidate(
                "openclaw-runtime",
                default_openclaw_runtime_dir() / asset_spec.binary_name,
            ),
            BinaryCandidate(
                "codex-runtime",
                default_codex_runtime_dir() / asset_spec.binary_name,
            ),
        ]
    )

    return candidates


def find_installed_binary(
    explicit_path: str | None = None,
) -> BinaryCandidate | None:
    for candidate in resolve_binary_candidates(explicit_path):
        if candidate.path.exists():
            return candidate
    return None


def install_binary(
    *,
    version: str = "latest",
    repo_slug: str = DEFAULT_REPO_SLUG,
    layout: str = "openclaw",
    archive_file: str | None = None,
    asset_url: str | None = None,
    force: bool = False,
) -> dict[str, str]:
    asset_spec = resolve_asset_spec()
    target_dir = resolve_install_dir(layout)
    target_dir.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="wenwengu-binary-install-") as temp_root:
        temp_root_path = Path(temp_root)
        archive_path = temp_root_path / asset_spec.asset_name

        if archive_file:
            source_archive = Path(archive_file).expanduser().resolve()
            if not source_archive.exists():
                raise SystemExit(f"Archive file not found: {source_archive}")
            shutil.copy2(source_archive, archive_path)
            source_url = f"file://{source_archive}"
        else:
            source_url = asset_url or build_release_url(
                repo_slug=repo_slug,
                version=version,
                asset_name=asset_spec.asset_name,
            )
            source_url = download_release_archive(
                repo_slug=repo_slug,
                version=version,
                asset_name=asset_spec.asset_name,
                explicit_url=asset_url,
                destination=archive_path,
            )

        extracted_dir = temp_root_path / "extracted"
        extracted_dir.mkdir(parents=True, exist_ok=True)
        extract_archive(
            archive_path=archive_path,
            archive_type=asset_spec.archive_type,
            target_dir=extracted_dir,
        )

        binary_path = extracted_dir / asset_spec.binary_name
        if not binary_path.exists():
            raise SystemExit(
                f"Installed archive did not contain expected engine executable: {asset_spec.binary_name}"
            )

        if os.name != "nt":
            binary_path.chmod(
                binary_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
            )

        if force and target_dir.exists():
            shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        final_binary_path = target_dir / asset_spec.binary_name
        shutil.copy2(binary_path, final_binary_path)
        if os.name != "nt":
            final_binary_path.chmod(
                final_binary_path.stat().st_mode
                | stat.S_IXUSR
                | stat.S_IXGRP
                | stat.S_IXOTH
            )

        metadata_path = target_dir / "install-metadata.json"
        metadata_path.write_text(
            json.dumps(
                {
                    "repo_slug": repo_slug,
                    "version": version,
                    "asset_name": asset_spec.asset_name,
                    "source_url": source_url,
                    "platform": asset_spec.platform_label,
                    "binary_path": str(final_binary_path),
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

    return {
        "binary_path": str(final_binary_path),
        "layout": layout,
        "platform": asset_spec.platform_label,
        "asset_name": asset_spec.asset_name,
        "source_url": source_url,
    }


def download_archive(url: str, destination: Path) -> None:
    request = urllib.request.Request(
        url, headers={"User-Agent": "wenwengu-cli-skill-installer"}
    )
    try:
        with (
            urllib.request.urlopen(request) as response,
            destination.open("wb") as handle,
        ):
            shutil.copyfileobj(response, handle)
    except Exception as exc:
        raise SystemExit(
            f"Failed to download engine package from {url}: {exc}"
        ) from exc


def download_release_archive(
    *,
    repo_slug: str,
    version: str,
    asset_name: str,
    explicit_url: str | None,
    destination: Path,
) -> str:
    if explicit_url:
        download_archive(explicit_url, destination)
        return explicit_url

    candidate_urls = [
        build_release_url(repo_slug=repo_slug, version=version, asset_name=asset_name)
    ]
    if version == "latest":
        candidate_urls.append(
            build_release_url(
                repo_slug=repo_slug, version="edge", asset_name=asset_name
            )
        )

    last_error: SystemExit | None = None
    for candidate_url in candidate_urls:
        try:
            download_archive(candidate_url, destination)
            return candidate_url
        except SystemExit as exc:
            last_error = exc

    if last_error is not None:
        raise last_error
    raise SystemExit(
        "Failed to resolve a release download URL for the valuation engine."
    )


def extract_archive(*, archive_path: Path, archive_type: str, target_dir: Path) -> None:
    if archive_type == "zip":
        with zipfile.ZipFile(archive_path) as archive:
            for member in archive.infolist():
                member_path = _safe_target_path(target_dir, member.filename)
                if member.is_dir():
                    member_path.mkdir(parents=True, exist_ok=True)
                    continue
                member_path.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member) as src, member_path.open("wb") as dst:
                    shutil.copyfileobj(src, dst)
        return

    if archive_type == "tar.gz":
        with tarfile.open(archive_path, "r:gz") as archive:
            for member in archive.getmembers():
                member_path = _safe_target_path(target_dir, member.name)
                if member.isdir():
                    member_path.mkdir(parents=True, exist_ok=True)
                    continue
                if member.issym() or member.islnk():
                    raise SystemExit(
                        "Refusing to extract archive with symlink entries."
                    )
                member_path.parent.mkdir(parents=True, exist_ok=True)
                extracted = archive.extractfile(member)
                if extracted is None:
                    continue
                with extracted, member_path.open("wb") as dst:
                    shutil.copyfileobj(extracted, dst)
        return

    raise SystemExit(f"Unsupported archive type: {archive_type}")


def _safe_target_path(root_dir: Path, member_name: str) -> Path:
    candidate = (root_dir / member_name).resolve()
    root = root_dir.resolve()
    if candidate != root and root not in candidate.parents:
        raise SystemExit(f"Refusing to extract path outside target dir: {member_name}")
    return candidate
