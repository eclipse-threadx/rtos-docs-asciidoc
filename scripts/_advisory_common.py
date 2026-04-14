"""Shared helpers for the security-advisory scripts.

Keeps the component list, auth resolution, and GitHub API pagination in one
place so `fetch-security-advisories.py` and `update-security-updates-page.py`
agree on what to pull.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

GITHUB_API = "https://api.github.com"

# Component slug (matches rtos-docs/<slug>) -> GitHub owner/repo.
COMPONENTS: dict[str, str] = {
    "threadx":  "eclipse-threadx/threadx",
    "netx-duo": "eclipse-threadx/netxduo",
    "usbx":     "eclipse-threadx/usbx",
    "filex":    "eclipse-threadx/filex",
    "levelx":   "eclipse-threadx/levelx",
    "guix":     "eclipse-threadx/guix",
}

DISPLAY_NAME: dict[str, str] = {
    "threadx":  "ThreadX",
    "netx-duo": "NetX Duo",
    "usbx":     "USBX",
    "filex":    "FileX",
    "levelx":   "LevelX",
    "guix":     "GUIX",
}


def resolve_token() -> str:
    """Find a GitHub token via `gh auth token`, then env vars."""
    gh = shutil.which("gh") or shutil.which("gh.exe")
    if gh:
        try:
            out = subprocess.run(
                [gh, "auth", "token"],
                capture_output=True, text=True, check=True,
            )
            token = out.stdout.strip()
            if token:
                return token
        except subprocess.CalledProcessError:
            pass

    for var in ("GH_TOKEN", "GITHUB_TOKEN"):
        token = os.environ.get(var, "").strip()
        if token:
            return token

    sys.exit(
        "error: no GitHub token available.\n"
        "  run `gh auth login`, or set GH_TOKEN / GITHUB_TOKEN."
    )


def _next_link(link_header: str) -> str | None:
    for part in link_header.split(","):
        m = re.match(r'\s*<([^>]+)>\s*;\s*rel="next"', part)
        if m:
            return m.group(1)
    return None


def fetch_advisories(owner_repo: str, token: str) -> list[dict]:
    """Return all published advisories for a repo, following pagination."""
    url = f"{GITHUB_API}/repos/{owner_repo}/security-advisories?state=published&per_page=100"
    results: list[dict] = []
    while url:
        req = urllib.request.Request(url, headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "threadx-docs-advisory-fetcher",
        })
        try:
            with urllib.request.urlopen(req) as resp:
                results.extend(json.loads(resp.read()))
                url = _next_link(resp.headers.get("Link", ""))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            sys.exit(f"error: GitHub API {e.code} for {owner_repo}: {body}")
    return results
