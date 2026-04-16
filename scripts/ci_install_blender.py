#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Download and cache Blender for CI testing.

Downloads Blender from the official release archive, caches the extraction,
and prints the executable path for use in subsequent CI steps.

Usage:
    python scripts/ci_install_blender.py <version> [<platform>]

Examples:
    python scripts/ci_install_blender.py 4.2.12 linux-x64
    python scripts/ci_install_blender.py 4.5.1 macos-arm64
    python scripts/ci_install_blender.py 5.0.0 windows-x64

Environment variables:
    BLENDER_CACHE_DIR  - Directory to cache downloads (default: .ci_blender_cache)
    GITHUB_ACTIONS     - If set, uses $RUNNER_TEMP for caching

Output:
    Prints the absolute path to the Blender executable to stdout.
    Exit code 0 on success, 1 on failure.
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

# --------------------------------------------------------------------------------------------------
# Blender release archive URL templates
# --------------------------------------------------------------------------------------------------

BLENDER_ARCHIVE_BASE = "https://download.blender.org/release"

# Map (major, minor) patch versions for known releases.
# If the exact patch version is not listed, we'll try to discover it.
KNOWN_PATCHES: dict[str, str] = {
    "4.2": "4.2.12",
    "4.5": "4.5.1",
    "5.0": "5.0.1",
    "5.1": "5.1.0",
}

PLATFORM_MAP: dict[str, dict[str, str]] = {
    "linux-x64": {
        "ext": "tar.xz",
        "executable": "blender",
        "folder_pattern": "blender-{version}-linux-x64",
    },
    "macos-arm64": {
        "ext": "dmg",
        "executable": "Blender.app/Contents/MacOS/Blender",
        "folder_pattern": "Blender.app",
    },
    "macos-x86_64": {
        "ext": "dmg",
        "executable": "Blender.app/Contents/MacOS/Blender",
        "folder_pattern": "Blender.app",
    },
    "windows-x64": {
        "ext": "zip",
        "executable": "blender.exe",
        "folder_pattern": "blender-{version}-windows-x64",
    },
}


def _resolve_full_version(short_version: str) -> str:
    """Resolve a short version like '4.2' to its latest patch e.g. '4.2.12'.

    If the version already has 3 parts (x.y.z), return it as-is.
    Otherwise, look up KNOWN_PATCHES.
    """
    parts = short_version.split(".")
    if len(parts) >= 3:
        return short_version
    if short_version in KNOWN_PATCHES:
        return KNOWN_PATCHES[short_version]
    # Fallback: try .0
    return f"{short_version}.0"


def _detect_platform() -> str:
    """Detect the current platform string."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    if system == "linux":
        return "linux-x64"
    elif system == "darwin":
        return "macos-arm64" if machine == "arm64" else "macos-x86_64"
    elif system == "windows":
        return "windows-x64"
    raise RuntimeError(f"Unsupported platform: {system} {machine}")


def _build_archive_url(version: str, platform_str: str) -> tuple[str, str]:
    """Build the download URL and expected archive filename.

    Returns:
        Tuple of (url, archive_filename)
    """
    plat_info = PLATFORM_MAP[platform_str]
    ext = plat_info["ext"]
    major_minor = ".".join(version.split(".")[:2])

    if platform_str.startswith("macos"):
        # macOS archives have a different naming convention
        if platform_str == "macos-arm64":
            filename = f"blender-{version}-macos-arm64.dmg"
        else:
            filename = f"blender-{version}-macos-x86_64.dmg"
    else:
        filename = f"blender-{version}-{platform_str.replace('-', '-', 1)}.{ext}"

    url = f"{BLENDER_ARCHIVE_BASE}/Blender{major_minor}/{filename}"
    return url, filename


def _find_blender_executable(install_dir: Path, platform_str: str, version: str) -> Path:
    """Find the Blender executable after extraction.

    Args:
        install_dir: Directory where Blender was extracted
        platform_str: Platform identifier
        version: Blender version string

    Returns:
        Path to the Blender executable

    Raises:
        FileNotFoundError: If executable not found
    """
    plat_info = PLATFORM_MAP[platform_str]
    executable_name = plat_info["executable"]

    # Try common extraction directory structures
    candidates = [
        install_dir / f"blender-{version}-{platform_str.replace('-', '-', 1)}" / executable_name,
        install_dir / f"blender-{version}-linux-x64" / executable_name,
    ]

    # For macOS, look inside .app bundles
    if platform_str.startswith("macos"):
        candidates.extend(
            [
                install_dir / "Blender.app" / "Contents" / "MacOS" / "Blender",
                install_dir / f"blender-{version}-macos-arm64" / "Blender.app" / "Contents" / "MacOS" / "Blender",
            ]
        )

    # For Windows, try the folder pattern
    if platform_str == "windows-x64":
        candidates.extend(
            [
                install_dir / f"blender-{version}-windows-x64" / executable_name,
            ]
        )

    # Also try a glob search as fallback
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()

    # Last resort: search recursively
    for p in install_dir.rglob(executable_name if platform_str != "windows-x64" else executable_name):
        if p.is_file():
            return p.resolve()

    raise FileNotFoundError(
        f"Could not find Blender executable in {install_dir}. Searched for: {[str(c) for c in candidates]}"
    )


def _extract_dmg(dmg_path: Path, install_dir: Path) -> None:
    """Extract a macOS .dmg file.

    Uses hdiutil to attach, copy, and detach.
    """
    mount_point = install_dir / "_dmg_mount"
    mount_point.mkdir(exist_ok=True)

    try:
        # Attach DMG
        subprocess.run(
            ["hdiutil", "attach", str(dmg_path), "-mountpoint", str(mount_point)],
            check=True,
            capture_output=True,
        )

        # Copy Blender.app
        app_src = mount_point / "Blender.app"
        if not app_src.exists():
            # Try finding any .app in the mount
            apps = list(mount_point.glob("*.app"))
            if apps:
                app_src = apps[0]
            else:
                raise FileNotFoundError(f"No .app found in {mount_point}")

        app_dst = install_dir / "Blender.app"
        shutil.copytree(app_src, app_dst, dirs_exist_ok=True)

    finally:
        # Detach DMG
        subprocess.run(
            ["hdiutil", "detach", str(mount_point)],
            check=False,
            capture_output=True,
        )


def _download_with_progress(url: str, dest: Path) -> None:
    """Download a file with progress reporting."""
    print(f"  Downloading: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "blender-mcp-ci/1.0"})
    with urllib.request.urlopen(req) as response, dest.open("wb") as out_file:
        total_size = int(response.headers.get("Content-Length", 0))
        downloaded = 0
        last_pct = -1
        chunk_size = 1024 * 256  # 256 KB
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            out_file.write(chunk)
            downloaded += len(chunk)
            if total_size > 0:
                pct = int(downloaded * 100 / total_size)
                if pct != last_pct and pct % 10 == 0:
                    print(f"  Download: {pct}% ({downloaded // 1024 // 1024}MB / {total_size // 1024 // 1024}MB)")
                    last_pct = pct


def install_blender(version: str, platform_str: str | None = None) -> Path:
    """Download, extract, and return path to Blender executable.

    Args:
        version: Blender version (e.g. '4.2', '4.2.12', '5.0')
        platform_str: Target platform. Auto-detected if None.

    Returns:
        Absolute path to the Blender executable.

    Raises:
        RuntimeError: If download or extraction fails.
    """
    full_version = _resolve_full_version(version)
    if platform_str is None:
        platform_str = _detect_platform()

    if platform_str not in PLATFORM_MAP:
        raise ValueError(f"Unsupported platform: {platform_str}. Choose from: {list(PLATFORM_MAP)}")

    # Determine cache directory
    cache_dir = Path(os.environ.get("BLENDER_CACHE_DIR", ".ci_blender_cache"))
    if os.environ.get("GITHUB_ACTIONS"):
        runner_temp = os.environ.get("RUNNER_TEMP", "")
        if runner_temp:
            cache_dir = Path(runner_temp) / "blender_cache"

    cache_dir.mkdir(parents=True, exist_ok=True)
    install_dir = cache_dir / f"blender-{full_version}-{platform_str}"
    marker_file = install_dir / ".installed"

    if marker_file.exists():
        print(f"Using cached Blender {full_version} at {install_dir}")
        try:
            exe = _find_blender_executable(install_dir, platform_str, full_version)
            print(f"Executable: {exe}")
            return exe
        except FileNotFoundError:
            print("Cache marker exists but executable not found, re-installing...")
            shutil.rmtree(install_dir, ignore_errors=True)

    url, archive_name = _build_archive_url(full_version, platform_str)
    archive_path = cache_dir / archive_name

    if not archive_path.exists():
        try:
            _download_with_progress(url, archive_path)
        except Exception as e:
            archive_path.unlink(missing_ok=True)
            raise RuntimeError(f"Failed to download Blender {full_version}: {e}") from e
    else:
        print(f"Using cached archive: {archive_path}")

    print(f"Extracting {archive_name}...")
    install_dir.mkdir(parents=True, exist_ok=True)

    try:
        if archive_path.suffix == ".xz":
            # .tar.xz — Linux
            with tarfile.open(archive_path, "r:xz") as tar:
                tar.extractall(path=install_dir, filter="data")
        elif archive_path.suffix == ".zip":
            # .zip — Windows
            with zipfile.ZipFile(archive_path) as zf:
                zf.extractall(install_dir)
        elif archive_path.suffix == ".dmg":
            # .dmg — macOS
            _extract_dmg(archive_path, install_dir)
        else:
            raise RuntimeError(f"Unknown archive format: {archive_path.suffix}")
    except Exception as e:
        shutil.rmtree(install_dir, ignore_errors=True)
        raise RuntimeError(f"Failed to extract Blender: {e}") from e

    exe = _find_blender_executable(install_dir, platform_str, full_version)

    if platform_str != "windows-x64":
        exe.chmod(exe.stat().st_mode | 0o755)

    print(f"Verifying Blender at {exe}...")
    try:
        result = subprocess.run(
            [str(exe), "--version"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        first_line = result.stdout.strip().split("\n")[0] if result.stdout.strip() else "(no output)"
        print(f"  {first_line}")
    except (subprocess.TimeoutExpired, OSError) as e:
        raise RuntimeError(f"Blender verification failed: {e}") from e

    marker_file.write_text(f"{full_version}\n{platform_str}\n{exe}\n")

    print(f"Blender {full_version} installed successfully: {exe}")
    return exe


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python ci_install_blender.py <version> [<platform>]")
        print(f"  Supported platforms: {list(PLATFORM_MAP)}")
        print(f"  Known versions: {list(KNOWN_PATCHES)}")
        return 1

    version = sys.argv[1]
    platform_str = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        exe = install_blender(version, platform_str)
        print(exe)
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
