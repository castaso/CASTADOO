#!/usr/bin/env python3
"""Verify the Windows installer by actually compiling it, then asserting identity.

Why this exists
---------------
`setup/win32/setup.nsi` is the largest single file the fork edits (92 added / 49
deleted lines) and it is the one surface where a mistake is silent: a wrong
!define produces a working installer that brands the wrong thing, and nothing in
the tree notices. Reading the diff by eye does not establish that the script
still COMPILES, and `makensis` is not part of a normal checkout.

What it does
------------
1. Finds makensis (PATH, or $NSISDIR, or --makensis).
2. Copies setup/win32 into a scratch dir and substitutes the four third-party
   plugins Odoo's own build provisions but does not vendor (Nsis7z,
   AccessControl, NScurl, nsisunz). It also retargets the two posbox SSL `File`
   lines, which point at `odo_addons/point_of_sale` - a layout that does not
   exist in a git checkout of 17.0, upstream or fork. Both substitutions are
   reported, and the REAL setup.nsi is never modified.
3. Compiles. A compile failure is a real failure: it means a define, macro,
   Section or LangString is broken.
4. Runs makensis again with /PPO and asserts the RESOLVED identity: the
   Add/Remove key is CASTADOO, the legacy Odoo key is still read and deleted,
   the service name and config filenames are unchanged, and no define of ours
   survived unsubstituted.

What it does NOT prove
----------------------
Plugin behaviour, payload contents, and the run-time UI. Those need the real
build environment. This asserts the identity chain, which is what the fork
changed.

Usage
-----
    python castadoo/tools/verify_installer.py
    python castadoo/tools/verify_installer.py --makensis "C:/NSIS/makensis.exe"
    python castadoo/tools/verify_installer.py --json

Exit codes: 0 pass, 1 fail, 2 makensis not found (reported as SKIP, not fail).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "setup" / "win32"

# Third-party plugins upstream provisions in its own build and does not vendor.
MISSING_PLUGINS = ("Nsis7z", "AccessControl", "NScurl", "nsisunz")

# Upstream references `..\..\odoo\addons\point_of_sale\...`, which assumes the
# repo is checked out as `odoo/` AND that point_of_sale is under odoo/addons.
# In 17.0 it lives at the top-level addons/. Byte-identical to pristine 17.0, so
# this is upstream breakage, not the fork's.
SSL_LINES = (
    r'File "..\..\odoo\addons\point_of_sale\tools\posbox\overwrite_after_init'
    r'\etc\ssl\certs\nginx-cert.crt"',
    r'File "..\..\odoo\addons\point_of_sale\tools\posbox\overwrite_after_init'
    r'\etc\ssl\private\nginx-cert.key"',
)

DEFINES = {
    "MAJOR_VERSION": "17",
    "MINOR_VERSION": "0",
    "REVISION_VERSION": "0",
}

STUB_DIRS = (
    "WinPy64/python-3.10.11.amd64",
    "nssm-2.24/win64",
    "server",
    "vcredist",
    "wkhtmltopdf",
)
STUB_FILES = ("server/i18n_bundle.7z", "vcredist/vc_redist.x64.exe")


def find_makensis(explicit: str | None) -> Path | None:
    if explicit:
        p = Path(explicit)
        return p if p.exists() else None
    if os.environ.get("NSISDIR"):
        p = Path(os.environ["NSISDIR"]) / "Bin" / ("makensis.exe" if os.name == "nt" else "makensis")
        if p.exists():
            return p
    for name in ("makensis.exe", "makensis"):
        w = shutil.which(name)
        if w:
            return Path(w)
    for cand in (
        r"C:\Program Files (x86)\NSIS\makensis.exe",
        r"C:\Program Files\NSIS\makensis.exe",
        "/usr/bin/makensis",
        "/usr/local/bin/makensis",
    ):
        if Path(cand).exists():
            return Path(cand)
    return None


def stub_tools(tools: Path) -> None:
    for rel in STUB_DIRS:
        d = tools.joinpath(*rel.split("/"))
        d.mkdir(parents=True, exist_ok=True)
        (d / "_stub.txt").write_text("stub\n")
    for rel in STUB_FILES:
        f = tools.joinpath(*rel.split("/"))
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(b"stub")


def prepare(work: Path) -> tuple[Path, list[str]]:
    """Copy setup/win32 to the scratch dir and apply the two documented edits."""
    shutil.copytree(SRC, work / "win32")
    script = work / "win32" / "setup.nsi"
    text = script.read_bytes().decode("latin-1", errors="replace")
    notes: list[str] = []

    count = 0
    out_lines = []
    for line in text.splitlines(keepends=True):
        m = re.match(r"^\s*(\w+)::(\w+)", line)
        if m and m.group(1) in MISSING_PLUGINS:
            indent = line[: len(line) - len(line.lstrip())]
            out_lines.append(
                f'{indent}DetailPrint "STUBBED {m.group(1)}::{m.group(2)}"\n',
            )
            count += 1
        else:
            out_lines.append(line)
    if count:
        notes.append(f"stubbed {count} third-party plugin call(s)")
    text = "".join(out_lines)

    for ssl in SSL_LINES:
        if ssl in text:
            text = text.replace(ssl, r'File "conf\nginx\nginx.conf"')
            notes.append("retargeted a posbox SSL File line (upstream path is broken)")
    script.write_bytes(text.encode("latin-1"))
    return script, notes


def makensis(mk: Path, args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(mk), *args], cwd=str(cwd), capture_output=True,
        text=True, errors="replace",
    )


def compile_and_assert(mk: Path, work: Path, tools: Path) -> tuple[bool, list[tuple[str, bool, str]], str]:
    script, notes = prepare(work)
    common = [f"/DTOOLSDIR={tools}"] + [f"/D{k}={v}" for k, v in DEFINES.items()]

    # --- compile -----------------------------------------------------------
    comp = makensis(mk, ["/V2", *common, script.name], script.parent)
    if comp.returncode != 0:
        tail = (comp.stdout or "")[-2000:] + (comp.stderr or "")[-2000:]
        return False, [("compiles", False, tail.strip()[-800:])], "compile failed"

    # --- preprocess, for resolved identity ---------------------------------
    ppo = work / "setup.pp.nsi"
    pp = makensis(mk, ["/V1", "/PPO", f"/O{ppo}", *common, script.name], script.parent)
    if pp.returncode != 0 or not ppo.exists():
        return False, [("preprocesses", False, (pp.stderr or "")[-400:])], "PPO failed"

    raw = ppo.read_bytes()
    if raw[:2] == b"\xff\xfe":
        text = raw.decode("utf-16-le")
    elif raw[:2] == b"\xfe\xff":
        text = raw.decode("utf-16-be")
    else:
        text = raw.decode("latin-1", errors="replace")
    lines = text.splitlines()
    checks: list[tuple[str, bool, str]] = []

    def hits(pat: str) -> list[str]:
        rx = re.compile(pat)
        return [ln.strip() for ln in lines if rx.search(ln)]

    def check(name: str, ok, detail: str = "") -> None:
        checks.append((name, bool(ok), detail))

    cur = hits(r'Uninstall\\CASTADOO 17\.0" "Publisher" "CASTASOFT"')
    check("Add/Remove key resolves to 'CASTADOO 17.0', publisher CASTASOFT",
          cur, cur[0] if cur else "not found")

    leg_read = hits(r"ReadRegStr.*Uninstall\\Odoo 17\.0")
    check("legacy Odoo Add/Remove key is READ (existing install is found)",
          leg_read, leg_read[0] if leg_read else "not found")

    leg_del = hits(r"DeleteRegKey.*Uninstall\\Odoo 17\.0")
    check("legacy Odoo Add/Remove key is DELETED (same $INSTDIR only)",
          leg_del, leg_del[0] if leg_del else "not found")

    svc = hits(r"odoo-server-17\.0")
    check("FROZEN: service name stays odoo-server-17.0", svc,
          f"{len(svc)} resolved occurrence(s)")

    srv = hits(r'Uninstall\\Odoo Server 17\.0')
    check("FROZEN: server uninstall key stays 'Odoo Server 17.0'", srv,
          srv[0] if srv else "not found")

    for frozen in ("odoo.conf", "odoo-bin", "odoo.log"):
        h = hits(re.escape(frozen))
        check(f"FROZEN: {frozen} survives", h, f"{len(h)} occurrence(s)")

    pg = hits(r"PostgreSQL_For_Odoo")
    check("FROZEN: PostgreSQL service stays PostgreSQL_For_Odoo", pg,
          f"{len(pg)} occurrence(s)")

    cap = hits(r'Caption "CASTADOO 17\.0 Setup"')
    check("Caption resolves to 'CASTADOO 17.0 Setup'", cap, cap[0] if cap else "")

    brand = hits(r"BrandingText\s+'CASTADOO 17\.0'")
    check("BrandingText resolves to 'CASTADOO 17.0'", brand,
          brand[0] if brand else "")

    site = hits(r"castasoft\.yukreasi\.id")
    check("support/help URLs point at castasoft.yukreasi.id", site,
          f"{len(site)} occurrence(s)")

    # Only OUR defines matter. ${LANG_English} and ${SectionOdoo_Server} are
    # MUI2's and NSIS's own generated identifiers and appear by design.
    src_text = (SRC / "setup.nsi").read_bytes().decode("latin-1", errors="replace")
    our = set(re.findall(r"^\s*!define\s+([A-Za-z_][A-Za-z0-9_]*)", src_text, re.MULTILINE))
    leftover = []
    for ln in lines:
        s = ln.strip()
        if s.startswith(("!", "#", ";")):
            continue
        if any(f"${{{n}}}" in ln for n in our):
            leftover.append(ln.strip())
    check(f"none of the script's {len(our)} defines left unresolved",
          not leftover, "\n          ".join(leftover[:5]))

    return True, checks, "; ".join(notes)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--makensis", help="path to makensis (else PATH or $NSISDIR)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    mk = find_makensis(args.makensis)
    if mk is None:
        msg = ("makensis not found. Install NSIS (winget install NSIS.NSIS, or apt "
               "install nsis) or pass --makensis. The installer is compile-verified "
               "only when this runs.")
        if args.json:
            print(json.dumps({"status": "skip", "reason": msg}, indent=2))
        else:
            print("SKIP:", msg)
        return 2

    with tempfile.TemporaryDirectory(prefix="castadoo-nsi-") as td:
        tmp = Path(td)
        tools = tmp / "odoobuild"
        stub_tools(tools)
        work = tmp / "work"
        work.mkdir()
        ok, checks, note = compile_and_assert(mk, work, tools)

    if args.json:
        print(json.dumps({
            "status": "pass" if ok and all(c[1] for c in checks) else "fail",
            "makensis": str(mk),
            "notes": note,
            "checks": [{"name": n, "ok": o, "detail": d} for n, o, d in checks],
        }, indent=2))
    else:
        print("=" * 74)
        print(f"WINDOWS INSTALLER - compiled with {mk}")
        print("=" * 74)
        if note:
            for part in note.split("; "):
                print(f"  note: {part}")
            print()
        for name, good, detail in checks:
            print(f"  {'PASS' if good else 'FAIL'}  {name}")
            if detail:
                print(f"          {detail}")
        fails = sum(1 for _, g, _ in checks if not g)
        print("\n" + "=" * 74)
        print(f"RESULT: {'PASS' if fails == 0 else 'FAIL'}  "
              f"({len(checks) - fails}/{len(checks)})")
        print("=" * 74)

    return 0 if ok and all(c[1] for c in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
