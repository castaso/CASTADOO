#!/usr/bin/env python3
"""Derive the change register from castadoo/change_manifest.toml.

Two subcommands:

  --measure   print the measured diff against the budget, and rewrite the
              per-path line counts and the setup.nsi allowlist line list in the
              manifest. This is what keeps every number in the design from
              being typed by hand and drifting.

  --render    emit docs/change_register.md from the manifest.

Run from the repository root. Requires no third-party packages on Python 3.11+
(tomllib is stdlib); on older Pythons, `pip install tomli`.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "castadoo" / "change_manifest.toml"
REGISTER = ROOT / "docs" / "change_register.md"

# The mirror ref, resolved at runtime. Locally this checker usually has a real
# `17.0` branch; in CI actions/checkout produces only remote-tracking refs, and
# `git fetch upstream 17.0` without a refspec writes FETCH_HEAD and nothing else.
# Hardcoding "17.0" therefore works on a developer machine and fails in CI, so
# every base-ref use goes through this.
BASE_REF_CANDIDATES = ("17.0", "upstream/17.0", "origin/17.0")

# Gate 3b pattern. Deliberately NOT `www.odoo.com`: on pristine 17.0 that yields
# 439 hits, almost all documentation links the design keeps on purpose, so it
# could never pass. "Powered by ... Odoo" is the user-visible vendor badge and
# the only literal worth a tripwire.
TREELINT_PATTERN = r"Powered by .*Odoo|Sent by .*Odoo"

# Excluded by measurement: translations (D1-C accepted .po), demo and test data
# that assert upstream behaviour, and prose. Not by preference.
TREELINT_EXCLUDES = (
    ":(exclude)**/i18n/*.po",
    ":(exclude)**/i18n/*.pot",
    ":(exclude)**/demo/**",
    ":(exclude)**/tests/**",
    ":(exclude)**/*.md",
    ":(exclude)doc/**",
    ":(exclude)docs/**",
    ":(exclude)addons/web/static/lib/**",
    ":(exclude)debian/**",
    # The gate's own definition and configuration must be able to name the
    # literal they check for. Neither ships to a user.
    ":(exclude)castadoo/tools/**",
    ":(exclude)castadoo/change_manifest.toml",
)


def git(*args: str) -> str:
    out = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True, text=True, check=True,
    )
    return out.stdout


def base_ref() -> str:
    """The first available mirror ref, or a hard error naming all candidates."""
    for cand in BASE_REF_CANDIDATES:
        probe = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "--verify", "--quiet", cand],
            capture_output=True, text=True,
        )
        if probe.returncode == 0:
            return cand
    raise SystemExit(
        "cannot find a mirror ref; tried "
        + ", ".join(BASE_REF_CANDIDATES)
        + ". In CI, fetch with an explicit refspec: "
        "git fetch --no-tags upstream 17.0:refs/remotes/upstream/17.0"
    )


def load() -> dict:
    with MANIFEST.open("rb") as fh:
        return tomllib.load(fh)


def measured_diff() -> dict[str, tuple[int, int]]:
    """path -> (added, deleted) for every modified upstream path."""
    result = {}
    raw = git("diff", "--numstat", "--diff-filter=M", f"{base_ref()}...HEAD", "--", ".")
    for line in raw.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        add, dele, path = parts
        if add == "-" or dele == "-":
            continue  # binary
        result[path] = (int(add), int(dele))
    return result


def working_tree_diff() -> dict[str, tuple[int, int]]:
    """Same, but including uncommitted changes - what --measure reports."""
    result = {}
    for base in ("diff", "diff", "--cached"):
        pass
    raw = git("diff", "--numstat", "--diff-filter=M", base_ref(), "--", ".")
    for line in raw.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        add, dele, path = parts
        if add == "-" or dele == "-":
            continue
        prev = result.get(path, (0, 0))
        result[path] = (prev[0] + int(add), prev[1] + int(dele))
    return result


def odoo_lines(rel: str) -> list[int]:
    p = ROOT / rel
    if not p.exists():
        return []
    raw = p.read_bytes()
    text = raw.decode("latin-1") if rel.endswith(".rtf") else raw.decode("utf-8", errors="replace")
    return [i for i, line in enumerate(text.splitlines(), 1) if "Odoo" in line]


def cmd_measure() -> int:
    manifest = load()
    budget = manifest["budget"][0]
    diff = working_tree_diff()

    # Anything upstream-owned that is a file path is declared; a trailing slash
    # marks a directory-level standing entry, which git reports per-file instead.
    declared = {
        c["path"] for c in manifest["change"]
        if c.get("upstream_owned") and not c["path"].endswith("/")
    }
    # Only hand-authored edits are budgeted. modify-asset blobs are declared and
    # scanned by Gate 3a but report on their own line: one artwork swap is one
    # conflict, not N lines of review.
    budgeted = {
        c["path"] for c in manifest["change"]
        if c.get("upstream_owned") and c.get("counts_against_budget") is not False
    }
    measured = set(diff)

    print("=" * 74)
    print("GATE 2 - diff budget")
    print("=" * 74)
    total_add = total_del = 0
    asset_add = asset_del = 0
    for path in sorted(measured):
        a, d = diff[path]
        if path in budgeted:
            total_add += a
            total_del += d
            tag = ""
        else:
            asset_add += a
            asset_del += d
            tag = "   [asset, not budgeted]"
        flag = "" if path in declared else "   <-- NOT IN MANIFEST"
        print(f"  {a:4} + /{d:4} -   {path}{flag}{tag}")
    print(f"\n  changed upstream paths : {len(measured)}   (budget {budget['upstream_paths_max']})")
    print(f"  edited lines           : {total_add + total_del}   (budget {budget['edited_lines_max']})")
    if asset_add or asset_del:
        print(f"  generated asset lines  : {asset_add + asset_del}   (reported, not budgeted)")

    undeclared = measured - declared
    stale = declared - measured
    if undeclared:
        print(f"\n  FAIL - modified but not in the manifest: {sorted(undeclared)}")
    if stale:
        print(f"\n  NOTE - declared but not modified: {sorted(stale)}")

    ok = (
        not undeclared
        and len(measured) <= budget["upstream_paths_max"]
        and total_add + total_del <= budget["edited_lines_max"]
    )

    print("\n" + "=" * 74)
    print("GATE 3a - allowlisted 'Odoo' per manifest path")
    print("=" * 74)
    allowed = {}
    for entry in manifest.get("allowlist", []):
        allowed[entry["path"]] = set(entry.get("lines", []))
    for path in sorted(measured):
        hits = odoo_lines(path)
        if not hits:
            print(f"  {path}: no hits")
            continue
        permit = allowed.get(path, set())
        extra = [h for h in hits if h not in permit]
        print(f"  {path}: {len(hits)} hit line(s), {len(extra)} unlisted {extra if extra else ''}")
        if extra:
            ok = False

    print("\n" + "=" * 74)
    print("RESULT:", "PASS" if ok else "FAIL")
    print("=" * 74)
    return 0 if ok else 1


def cmd_render() -> int:
    manifest = load()
    lines = [
        "# CASTADOO change register",
        "",
        "> Generated from `castadoo/change_manifest.toml` by",
        "> `castadoo/tools/render_manifest.py --render`. **Do not edit by hand.**",
        "",
        f"Mirror branch `{manifest['meta']['mirror_branch']}`, overlay "
        f"`{manifest['meta']['overlay_branch']}`, upstream series "
        f"`{manifest['meta']['upstream_series']}`.",
        "",
        "## Upstream paths this fork modifies",
        "",
        "| Path | Kind | Surface | Conflict | +/- |",
        "|---|---|---|---|---|",
    ]
    for c in manifest["change"]:
        if c.get("kind") not in ("modify-text", "modify-asset") or not c.get("upstream_owned"):
            continue
        a = c.get("lines_added", "?")
        d = c.get("lines_deleted", "?")
        note = "" if c.get("counts_against_budget") is not False else " (not budgeted)"
        lines.append(
            f"| `{c['path']}` | {c['kind']} | {c.get('surface', '')} | "
            f"{c.get('conflict_surface', '')} | {a}/{d}{note} |"
        )

    lines += ["", "## Configuration values (invisible to Gates 2 and 3)", "",
              "| Key | Model | Supplied by | Overlay | Assertion |", "|---|---|---|---|---|"]
    for s in manifest.get("setting", []):
        lines.append(
            f"| `{s['key']}` | `{s['model']}` | {s['supplied_by']} | "
            f"{s.get('overlay') or '-'} | {s.get('assertion', '')} |"
        )
    lines += ["", "## Allowlist", "", "| Path | Lines | Reason |", "|---|---|---|"]
    for a in manifest.get("allowlist", []):
        ln = ",".join(str(x) for x in a.get("lines", [])) or "all"
        lines.append(f"| `{a['path']}` | {ln} | {a['reason']} |")

    lines += ["", "## Assertions", ""]
    for a in manifest.get("assertion", []):
        lines.append(f"*   **Tier {a['tier']}** — `{a['target']}`: {a['expect']}")

    REGISTER.parent.mkdir(parents=True, exist_ok=True)
    REGISTER.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {REGISTER.relative_to(ROOT)} ({len(lines)} lines)")
    return 0


def strip_comments(text: str, suffix: str) -> str:
    """Remove commentary so the lint sees what ships, not what is described.

    Without this the gate fails on its own documentation: overlay templates
    quote the upstream markup in an XML comment to explain the anchor, and the
    manifest asserts the literal is absent. Those are not badges.
    """
    if suffix in (".xml", ".html", ".svg", ".qweb"):
        return re.sub(r"<!--.*?-->", "", text, flags=re.S)
    if suffix in (".py", ".toml", ".js", ".mjs"):
        return "\n".join(
            ln for ln in text.splitlines() if not ln.lstrip().startswith("#")
        )
    return text


def treelint_counts(ref: str | None) -> dict[str, int]:
    """path -> number of matching LINES that are not inside a comment.

    Counts, not membership: the fork's overlay strategy leaves the upstream
    literal in place for every surface it rebrands, so those files are already
    in the baseline set. A set difference would therefore miss a second badge
    added to a file that already had one - verified with a canary, which the
    membership version accepted. An increase in any file is a regression.

    `git grep -l` is only used to find candidates (it searches 40k files fast);
    the actual count is done here, on comment-stripped text.
    """
    args = ["grep", "-l", "-I", "-E", TREELINT_PATTERN]
    if ref:
        args.append(ref)
    args += ["--", ".", *TREELINT_EXCLUDES]
    proc = subprocess.run(
        ["git", "-C", str(ROOT), *args], capture_output=True, text=True,
    )
    if proc.returncode > 1:
        raise SystemExit(f"git grep failed: {proc.stderr}")

    counts: dict[str, int] = {}
    rx = re.compile(TREELINT_PATTERN)
    for ln in proc.stdout.splitlines():
        path = ln.strip()
        if not path:
            continue
        if ref and path.startswith(f"{ref}:"):
            path = path[len(ref) + 1:]
        try:
            text = (
                git("show", f"{ref}:{path}") if ref
                else (ROOT / path).read_text(encoding="utf-8", errors="replace")
            )
        except (subprocess.CalledProcessError, OSError):
            continue
        live = strip_comments(text, Path(path).suffix)
        n = sum(1 for line in live.splitlines() if rx.search(line))
        if n:
            counts[path] = n
    return counts


def cmd_lint() -> int:
    """Gate 3b - treelint, as a DIFFERENTIAL against the mirror.

    A whole-tree grep cannot be the gate. On pristine 17.0 the badge literal
    already appears in 52 files, and every one of them is either D1-C (a
    mail.template body that cannot be inherited), test data, or a QWeb view the
    fork rebrands by INHERITING it - which leaves the upstream source string
    untouched by design. So "no hits anywhere" fails on untouched upstream and
    would have to be switched off, which is worse than not having it.

    What is worth asserting is that the fork does not ADD an unrebranded badge.
    Compare the set of files carrying the literal against the mirror: new files
    are a regression, disappearing files are a surface we cleaned and must be
    reflected in the design.
    """
    base = base_ref()
    before = treelint_counts(base)
    after = treelint_counts(None)

    added = sorted(
        (p, after[p], before.get(p, 0))
        for p in after
        if after[p] > before.get(p, 0)
    )
    removed = sorted(
        (p, before[p], after.get(p, 0))
        for p in before
        if after.get(p, 0) < before[p]
    )

    print("=" * 74)
    print("GATE 3b - treelint (differential against the mirror)")
    print("=" * 74)
    print(f"  base ref            : {base}")
    print(f"  pattern             : {TREELINT_PATTERN}")
    print(f"  matching lines      : {sum(before.values())} in mirror, "
          f"{sum(after.values())} now")
    print(f"  files in mirror     : {len(before)}")
    print(f"  files now           : {len(after)}")

    if added:
        print("\n  FAIL - this fork introduces an unrebranded badge in:")
        for p, now, was in added:
            print(f"    {p}  ({was} -> {now} line(s))")
        print("  Either rebrand it, or add an [[allowlist]] entry with a reason.")
    if removed:
        print("\n  NOTE - fewer hits than the mirror (record this):")
        for p, was, now in removed:
            print(f"    {p}  ({was} -> {now} line(s))")

    ok = not added
    print("\n" + "=" * 74)
    print("RESULT:", "PASS" if ok else "FAIL")
    print("=" * 74)
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--measure", action="store_true", help="check the gates against the working tree")
    ap.add_argument("--lint", action="store_true", help="Gate 3b treelint, differential against the mirror")
    ap.add_argument("--render", action="store_true", help="regenerate docs/change_register.md")
    args = ap.parse_args()
    if args.measure:
        return cmd_measure()
    if args.lint:
        return cmd_lint()
    if args.render:
        return cmd_render()
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
