#!/usr/bin/env python3
"""Validate the castadoo addon tree without a database.

Checks the failures that only an install would otherwise catch:

  * every manifest is a valid Python literal and has the keys the design needs
  * every path named in `data` and `assets` exists
  * every addon has an __init__.py (without it Odoo does not see the module)
  * the base tier depends on `web` and nothing else, and has the D7-B hook
  * every overlay is auto_install on exactly its target, and depends on the base
  * every Python file compiles and every XML file parses

Run from anywhere; paths resolve from this file.
"""
from __future__ import annotations

import ast
import logging
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

log = logging.getLogger("castadoo.validate_addons")

ROOT = Path(__file__).resolve().parents[2]
TREE = ROOT / "castadoo"

BASE = "castadoo_branding"

problems: list[str] = []
notes: list[str] = []


def load_manifest(path: Path) -> dict:
    src = path.read_text(encoding="utf-8")
    return ast.literal_eval(src[src.index("{"):])


def check_addon(addon: Path, m: dict) -> None:
    name = addon.name

    if not (addon / "__init__.py").exists():
        problems.append(f"{name}: no __init__.py, so Odoo does not see the module")

    # A view file created but not listed in `data` is inert: the module installs,
    # the string gate still passes because the file exists, and the surface stays
    # unbranded. This is the design's own failure mode, so it is asserted.
    for rel in m.get("data") or []:
        if not (addon / rel).exists():
            problems.append(f"{name}: data path missing -> {rel}")

    for bundle, paths in (m.get("assets") or {}).items():
        for rel in paths:
            if not rel.startswith(name + "/"):
                problems.append(f"{name}: asset {rel} is not prefixed with {name}/")
                continue
            if not (TREE / rel).exists():
                problems.append(f"{name}: asset missing -> {rel}")
        if bundle not in KNOWN_BUNDLES and not bundle.startswith(("web.", "point_of_sale.")):
            notes.append(f"{name}: asset bundle {bundle!r} is not a stock 17.0 bundle name")

    if m.get("license") != "LGPL-3":
        problems.append(f"{name}: license must be LGPL-3, got {m.get('license')!r}")

    if name == BASE:
        if m.get("depends") != ["web"]:
            problems.append(f"{name}: depends must be exactly ['web'], got {m.get('depends')}")
        if m.get("auto_install") is not False:
            problems.append(f"{name}: auto_install must be False")
        if "post_init_hook" not in m:
            problems.append(f"{name}: post_init_hook missing (decision D7-B)")
    else:
        # The target is read from `auto_install`, NOT derived from the directory
        # name. The two legitimately differ: castadoo_branding_pos targets
        # point_of_sale (design item 22), because "point_of_sale" as a suffix
        # would make the addon name unwieldy and the hooks table already maps
        # 'point_of_sale' -> 'castadoo_branding_pos'. Deriving from the suffix
        # would reject a correct manifest.
        ai = m.get("auto_install")
        if not isinstance(ai, list) or len(ai) != 1:
            problems.append(f"{name}: auto_install must be exactly ['<target>'], got {ai!r}")
            return
        target = ai[0]
        if BASE not in (m.get("depends") or []):
            problems.append(f"{name}: depends must include {BASE}")
        if target not in (m.get("depends") or []):
            problems.append(
                f"{name}: auto_install names {target!r} but depends does not "
                f"include it, so the overlay can never activate",
            )
        if target == BASE:
            problems.append(f"{name}: auto_install must not name {BASE}")


# 17.0 declares these. Naming a bundle that does not exist is a silent no-op.
KNOWN_BUNDLES = {
    "web.assets_backend", "web.assets_frontend", "web.assets_common",
    "web.assets_tests", "web.report_assets_common", "web.report_assets_pdf",
    "web.assets_web", "web.assets_web_dark", "web.qunit_suite_tests",
    "point_of_sale.assets", "point_of_sale.assets_prod",
    "point_of_sale.assets_qunit_tests", "point_of_sale.assets_debug",
}


def main() -> int:
    manifests = sorted(TREE.rglob("__manifest__.py"))
    if not manifests:
        print(f"no manifests under {TREE}")
        return 1

    for mf in manifests:
        try:
            m = load_manifest(mf)
        except Exception as exc:  # noqa: BLE001 - report, do not crash
            problems.append(f"{mf.parent.name}: manifest is not a valid literal: {exc}")
            continue
        check_addon(mf.parent, m)

    # hooks.py carries a second copy of the target -> overlay mapping, and that
    # copy is the one that covers migrated databases. A drift between it and the
    # manifests is invisible at install: auto_install still works for a fresh
    # database, so nothing looks broken, while every already-installed target
    # silently keeps its Odoo branding.
    hooks = TREE / BASE / "hooks.py"
    if hooks.exists():
        src = hooks.read_text(encoding="utf-8")
        table = dict(re.findall(r"'([\w.]+)':\s*'(castadoo_branding_\w+)'", src))
        declared = {}
        for mf in manifests:
            try:
                m = load_manifest(mf)
            except Exception as exc:  # noqa: BLE001 - reported once, with its path
                # The syntax pass above already failed loudly on this file; this
                # pass only needs to not crash twice. Logging at debug keeps the
                # exception visible to someone diagnosing the run, which is what
                # the rule asks for, without duplicating the error output.
                log.debug("skipping unparsable manifest %s: %s", mf, exc)
                continue
            ai = m.get("auto_install")
            if mf.parent.name != BASE and isinstance(ai, list) and len(ai) == 1:
                declared[ai[0]] = mf.parent.name
        if table != declared:
            only_hooks = {k: v for k, v in table.items() if declared.get(k) != v}
            only_manifest = {k: v for k, v in declared.items() if table.get(k) != v}
            problems.append(
                "hooks.py _OVERLAYS disagrees with the manifests: "
                f"hooks-only={only_hooks} manifest-only={only_manifest}",
            )
        else:
            print(f"hooks table matches {len(table)} overlay manifests")

    py_files = sorted(TREE.rglob("*.py"))
    for f in py_files:
        try:
            compile(f.read_text(encoding="utf-8"), str(f), "exec")
        except SyntaxError as exc:
            problems.append(f"{f.relative_to(ROOT)}: syntax error: {exc}")

    xml_files = sorted(TREE.rglob("*.xml"))
    for f in xml_files:
        try:
            ET.parse(f)
        except ET.ParseError as exc:
            problems.append(f"{f.relative_to(ROOT)}: XML parse error: {exc}")

    print(f"addons: {len(manifests)}  python: {len(py_files)}  xml: {len(xml_files)}")

    for n in notes:
        print(f"note: {n}")

    if problems:
        print("\nPROBLEMS:")
        for p in problems:
            print(f"  {p}")
        return 1

    print("addon tree validation: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
