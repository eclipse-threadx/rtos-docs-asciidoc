#!/usr/bin/env python3
"""Update the global Security Updates page with rows generated from the
GitHub security advisories of every Eclipse ThreadX component.

The script fetches advisories via the GitHub API (same auth and component
list as `fetch-security-advisories.py`) and injects one table row per
advisory into the existing `security-updates.adoc` page.

Managed rows live between two marker comments:

    // <<< BEGIN auto-generated rows (update-security-updates-page.py) >>>
    ...
    // <<< END auto-generated rows >>>

Anything outside those markers is preserved verbatim — this is how the
pre-Eclipse Microsoft-era CVEs already on the page survive across runs.

Usage:
    python scripts/update-security-updates-page.py
    python scripts/update-security-updates-page.py --dry-run
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _advisory_common import (  # noqa: E402
    COMPONENTS, DISPLAY_NAME, fetch_advisories, resolve_token,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
PAGE_PATH = (
    REPO_ROOT
    / "rtos-docs" / "home" / "modules" / "ROOT" / "pages" / "security-updates.adoc"
)

BEGIN_MARKER = "// <<< BEGIN auto-generated rows (update-security-updates-page.py) >>>"
END_MARKER = "// <<< END auto-generated rows >>>"

HEADER_ROW_RE = re.compile(
    r"^\|\s*Release Date\s*\|\s*CVE\s*\|\s*Severity\s*\|.*$", re.IGNORECASE
)

NBSP_HYPHEN = "\u2011"


# --------------------------------------------------------------------------- #
# Row building
# --------------------------------------------------------------------------- #

def _nowrap(s: str) -> str:
    """Keep CVE IDs and dates on a single line in rendered HTML."""
    return (s or "").replace("-", NBSP_HYPHEN)


def _iso_date(iso: str) -> str:
    """Keep only the YYYY-MM-DD portion of an ISO 8601 timestamp."""
    return (iso or "")[:10]


def _join_ranges(advisory: dict, field: str) -> str:
    """Join version ranges across all vulnerable packages in an advisory."""
    vulns = advisory.get("vulnerabilities") or []
    parts: list[str] = []
    for v in vulns:
        value = (v.get(field) or "").strip()
        if value and value not in parts:
            parts.append(value)
    return "; ".join(parts) if parts else ""


def _cve_link(advisory: dict) -> str:
    cve = advisory.get("cve_id")
    if cve:
        return f"https://cve.mitre.org/cgi-bin/cvename.cgi?name={cve}[{_nowrap(cve)}]"
    ghsa = advisory.get("ghsa_id", "")
    html_url = advisory.get("html_url", "")
    if html_url and ghsa:
        return f"{html_url}[{_nowrap(ghsa)}]"
    return _nowrap(ghsa or "—")


def _sort_key(row: tuple) -> tuple:
    """Sort rows newest-first by ISO date, then by CVE/GHSA for stability."""
    _component_display, published_iso, cve_or_ghsa, *_ = row
    return (published_iso or "0000-00-00", cve_or_ghsa)


def build_rows(advisories_by_component: dict[str, list[dict]]) -> list[str]:
    """Return a list of AsciiDoc row blocks, newest first."""
    tuples: list[tuple] = []
    for component, advisories in advisories_by_component.items():
        display = DISPLAY_NAME[component]
        for adv in advisories:
            published_iso = (adv.get("published_at") or "")[:10]
            cve_or_ghsa = adv.get("cve_id") or adv.get("ghsa_id", "")
            tuples.append((
                display,
                published_iso,
                cve_or_ghsa,
                adv,
            ))

    tuples.sort(key=_sort_key, reverse=True)

    blocks: list[str] = []
    for display, published_iso, _key, adv in tuples:
        severity = (adv.get("severity") or "unknown").capitalize()
        affected = _join_ranges(adv, "vulnerable_version_range") or "—"
        patched = _join_ranges(adv, "patched_versions") or "—"
        blocks.append(
            f"| {_nowrap(_iso_date(published_iso))}\n"
            f"| {_cve_link(adv)}\n"
            f"| {severity}\n"
            f"| {display}\n"
            f"| {affected}\n"
            f"| {patched}"
        )
    return blocks


# --------------------------------------------------------------------------- #
# Page rewriting
# --------------------------------------------------------------------------- #

def _splice_between_markers(text: str, new_body: str) -> str:
    """Replace the content between BEGIN/END markers with ``new_body``."""
    pattern = re.compile(
        re.escape(BEGIN_MARKER) + r".*?" + re.escape(END_MARKER),
        flags=re.DOTALL,
    )
    replacement = f"{BEGIN_MARKER}\n{new_body}\n{END_MARKER}"
    return pattern.sub(replacement, text, count=1)


def _insert_markers_after_header(text: str, new_body: str) -> str:
    """First-run path: inject the marker block right after the header row."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if HEADER_ROW_RE.match(line):
            insertion = [
                "",
                BEGIN_MARKER,
                new_body,
                END_MARKER,
            ]
            lines[i + 1:i + 1] = insertion
            return "\n".join(lines)
    sys.exit(
        f"error: could not find the table header row in {PAGE_PATH}. "
        "Expected a line starting with `| Release Date | CVE | Severity |`."
    )


CVE_RE = re.compile(r"CVE[\u2011\-]\d{4}[\u2011\-]\d+")


def _collect_cves(text: str) -> set[str]:
    """All CVE IDs found in ``text``, normalized to ASCII hyphens."""
    return {m.group(0).replace(NBSP_HYPHEN, "-") for m in CVE_RE.finditer(text)}


def _strip_duplicates_outside_markers(text: str, generated_cves: set[str]) -> str:
    """Drop hand-written 6-line rows whose CVE is already in the generated block.

    A row block is six consecutive ``| …`` lines. When a row is dropped we
    also consume the single blank separator line that follows it so the
    surrounding table layout stays clean.
    """
    if not generated_cves:
        return text

    begin = text.index(BEGIN_MARKER)
    end = text.index(END_MARKER) + len(END_MARKER)
    before, managed, after = text[:begin], text[begin:end], text[end:]

    def scrub(chunk: str) -> str:
        lines = chunk.split("\n")
        out: list[str] = []
        i = 0
        while i < len(lines):
            # Detect a 6-line row starting with `|`.
            if (
                lines[i].startswith("|")
                and i + 5 < len(lines)
                and all(lines[i + k].startswith("|") for k in range(6))
            ):
                row = "\n".join(lines[i:i + 6])
                row_cves = {
                    m.group(0).replace(NBSP_HYPHEN, "-")
                    for m in CVE_RE.finditer(row)
                }
                if row_cves & generated_cves:
                    i += 6
                    # Swallow a single trailing blank separator line.
                    if i < len(lines) and lines[i] == "":
                        i += 1
                    continue
            out.append(lines[i])
            i += 1
        return "\n".join(out)

    return scrub(before) + managed + scrub(after)


DATATABLE_ATTR = '[role="datatable"]'


def _ensure_datatable_attribute(text: str) -> str:
    """Ensure the table has a ``[role="datatable"]`` attribute line so the
    supplemental UI's DataTables init can target it."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line.strip() == "|===":
            prev = lines[i - 1].strip() if i > 0 else ""
            if DATATABLE_ATTR in prev:
                return text
            # If there's an existing attribute block directly above, add the
            # role there; otherwise insert a fresh attribute line.
            if prev.startswith("[") and prev.endswith("]"):
                if "role=" not in prev:
                    lines[i - 1] = prev[:-1] + ', role="datatable"]'
                return "\n".join(lines)
            lines.insert(i, DATATABLE_ATTR)
            return "\n".join(lines)
    return text


US_DATE_CELL_RE = re.compile(r"^\|\s*(\d{1,2})/(\d{1,2})/(\d{4})\s*$")


def _migrate_us_dates(text: str) -> str:
    """Rewrite any ``| M/D/YYYY`` cell to ``| YYYY-MM-DD`` (with U+2011) so the
    whole table sorts lexicographically under DataTables.

    Runs across the entire page — the BEGIN/END block is regenerated from
    scratch each run, so this pass effectively targets the hand-written rows
    that pre-date the script.
    """
    def repl(match: re.Match) -> str:
        mo, day, year = match.group(1), match.group(2), match.group(3)
        iso = f"{year}-{int(mo):02d}-{int(day):02d}"
        return f"| {_nowrap(iso)}"

    return "\n".join(
        US_DATE_CELL_RE.sub(repl, line) for line in text.split("\n")
    )


def update_page(text: str, rows: list[str]) -> str:
    body = "\n\n".join(rows) if rows else "// (no advisories fetched)"
    if BEGIN_MARKER in text and END_MARKER in text:
        updated = _splice_between_markers(text, body)
    else:
        updated = _insert_markers_after_header(text, body)

    begin = updated.index(BEGIN_MARKER)
    end = updated.index(END_MARKER) + len(END_MARKER)
    generated_cves = _collect_cves(updated[begin:end])
    updated = _strip_duplicates_outside_markers(updated, generated_cves)
    updated = _migrate_us_dates(updated)
    updated = _ensure_datatable_attribute(updated)
    return updated


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    p.add_argument("--dry-run", action="store_true",
                   help="Print the updated page to stdout instead of writing.")
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    if not PAGE_PATH.is_file():
        sys.exit(f"error: {PAGE_PATH} does not exist.")

    token = resolve_token()
    advisories_by_component: dict[str, list[dict]] = {}
    total = 0
    for component, repo in COMPONENTS.items():
        print(f"[{DISPLAY_NAME[component]}] fetching from {repo} ...")
        adv = fetch_advisories(repo, token)
        advisories_by_component[component] = adv
        total += len(adv)
        print(f"  got {len(adv)} advisory record(s)")

    rows = build_rows(advisories_by_component)
    original = PAGE_PATH.read_text(encoding="utf-8")
    updated = update_page(original, rows)

    if args.dry_run:
        sys.stdout.write(updated)
        print(f"\n[dry-run] {total} advisory row(s) prepared; no file written.",
              file=sys.stderr)
        return 0

    if updated == original:
        print(f"\nNo changes needed in {PAGE_PATH}.")
        return 0

    with open(PAGE_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(updated)
    print(f"\nUpdated {PAGE_PATH} with {total} advisory row(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
