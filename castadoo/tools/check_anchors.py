#!/usr/bin/env python3
"""Resolve every castadoo inheritance anchor against the real parent template.

Odoo applies QWeb inheritance with lxml (`ir.ui.view.apply_inheritance_specs`)
and, for the static XML assets in the point of sale, at
`odoo/addons/base/models/assetsbundle.py` via the same function. It registers a
custom XPath `hasclass()` function, so a verifier without it rejects valid
expressions. Both are reproduced here.

Two semantics are easy to get wrong and are the reason this script exists:

1.  `//x` is an **absolute** path: `/descendant-or-self::node()/x`, evaluated
    from the document root. Odoo hands the single parent template to lxml as its
    own document, so `//x` sees only that template. Evaluating against the whole
    source *file* would also count matching nodes in sibling templates and turn
    a correct one-match anchor into a false multi-match. Each parent is therefore
    copied into its own document first.

2.  Owl/POS templates are identified by `t-name`, not `id`, and a bare id is
    module-qualified (`id="layout"` inside `web` is `web.layout`). Both keys are
    indexed, with the module prefix Odoo applies.

An anchor must resolve to **exactly one** node. Zero or many raises at install,
not at build, which is why this runs in CI.

Requires lxml; exits non-zero on any problem.
"""
from __future__ import annotations

import sys
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).resolve().parents[2]
TREE = ROOT / "castadoo"

# Template container names in QWeb files. `<t>` is used by Owl asset templates.
CONTAINERS = ("template", "t")


def _hasclass(context, *cls):
    """`hasclass(node, 'a', 'b')` - all classes present, as Odoo defines it."""
    node_classes = set(context.context_node.attrib.get("class", "").split())
    return node_classes.issuperset(cls)


etree.FunctionNamespace(None)["hasclass"] = _hasclass


PARENTS: dict[str, tuple[Path, object]] = {}


def module_of(path: Path) -> str | None:
    for base in (ROOT / "addons", ROOT / "odoo" / "addons"):
        try:
            return path.relative_to(base).parts[0]
        except ValueError:
            continue
    return None


def index_parents() -> None:
    """Index every upstream template by view id and by Owl t-name."""
    sources = list((ROOT / "addons").rglob("*.xml"))
    sources += list((ROOT / "odoo" / "addons").rglob("*.xml"))
    for path in sources:
        try:
            raw = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        # Cheap pre-filter: parsing 15k XML files in CI is otherwise slow.
        if "<template" not in raw and "t-name" not in raw:
            continue
        try:
            tree = etree.parse(
                str(path), parser=etree.XMLParser(recover=True, ns_clean=True),
            )
        except etree.XMLSyntaxError:
            continue
        mod = module_of(path)
        for el in tree.iter():
            if not isinstance(el.tag, str):
                continue
            if etree.QName(el).localname not in CONTAINERS:
                continue
            tid = el.get("id")
            if tid:
                key = tid if "." in tid or not mod else f"{mod}.{tid}"
                PARENTS.setdefault(key, (path, el))
            tname = el.get("t-name")
            if tname:
                key = tname if "." in tname or not mod else f"{mod}.{tname}"
                PARENTS.setdefault(key, (path, el))


def isolate(parent):
    """Copy the parent template into its own document, as Odoo effectively does."""
    return etree.fromstring(etree.tostring(parent))


def iter_inheriting_templates(tree):
    for tpl in tree.iter():
        if not isinstance(tpl.tag, str):
            continue
        inherit = tpl.get("inherit_id") or tpl.get("t-inherit")
        if inherit:
            yield tpl, inherit


def main() -> int:
    if not TREE.exists():
        print(f"no castadoo tree at {TREE}")
        return 1

    index_parents()
    print(f"indexed {len(PARENTS)} upstream templates")

    files = sorted(TREE.rglob("*.xml"))
    print(f"scanning {len(files)} castadoo XML files")

    total = 0
    problems: list[str] = []

    for path in files:
        tree = etree.parse(str(path), parser=etree.XMLParser(recover=True))
        rel = path.relative_to(ROOT)
        for tpl, inherit in iter_inheriting_templates(tree):
            where = PARENTS.get(inherit)
            if not where:
                # A parent outside addons/ and odoo/addons/, or a typo. Either way
                # the inheritance is dead: Odoo raises on install.
                problems.append(f"{rel}: parent {inherit!r} not found")
                print(f"  {rel}\n    MISSING PARENT {inherit!r}")
                continue

            ppath, parent = where
            doc = isolate(parent)
            seen_here = 0
            for xp in tpl.iter():
                if not isinstance(xp.tag, str):
                    continue
                if etree.QName(xp).localname != "xpath":
                    continue
                expr = xp.get("expr")
                pos = xp.get("position", "")
                seen_here += 1
                total += 1
                try:
                    nodes = doc.xpath(expr)
                except etree.XPathError as exc:
                    problems.append(f"{rel} [{pos}] {expr}: {exc}")
                    print(f"  {rel} [{pos}] XPath ERROR {expr}: {exc}")
                    continue
                if len(nodes) != 1:
                    problems.append(
                        f"{rel} [{pos}] {expr} -> {len(nodes)} matches "
                        f"(parent {inherit})",
                    )
                    print(f"  {rel} [{pos}] {len(nodes)} MATCHES {expr}")
            if seen_here:
                print(
                    f"  ok  {rel} -> {inherit} "
                    f"({ppath.relative_to(ROOT)}), {seen_here} xpath",
                )

    print(f"\nchecked {total} xpath expressions across {len(files)} files")
    if problems:
        print("\nPROBLEMS:")
        for p in problems:
            print("  " + p)
        return 1

    print("every anchor resolves to exactly one node")
    return 0


if __name__ == "__main__":
    sys.exit(main())
