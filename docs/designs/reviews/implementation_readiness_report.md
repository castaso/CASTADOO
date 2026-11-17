# Stage 9 — Implementation Readiness Test

**Target:** `docs/designs/castadoo-rebrand-fork.md` — **DetailedRange, lines 874–1449**
**Reviewers:** `egm-implementation-readiness`, `egm-codebase-details`, `egm-style`
**Context supplied:** `concepts_brief.md`, `change_register.md`, `verified_ground_truth.md`, `anchor_verification.md`
**Date:** 2026-11-17

---

## Verification note — this stage could verify

Stages 5–8 all ran blind on Odoo citations. For Stage 9 the orchestrator populated a sparse checkout at `C:\Users\Yongky\AppData\Local\Temp\opencode\depth17` (`9c58cae5`, 44 paths) and **ran the source checks that reviewer isolation blocks** — reviewers are sandboxed to the bundle and get `permission.rejected: external_directory` on that tree.

Results are on disk in two files, and both reviewers were given them as ground truth:

- **`verified_ground_truth.md`** — 17 citations confirmed exact, 7 contradicted.
- **`anchor_verification.md`** — all ten `inherit_id` parents checked; every `file:line` in the plan's highest-risk items measured.

**Consequence for the consolidated report:** item-level `file:line` citations are no longer "unverified by reviewers." They are measured. Only the ~40 anchors listed in `verified_ground_truth.md`'s closing note remain unmeasured, and that list is now a to-do, not a caveat.

---

## The single most important finding

**B1: no manifest in the plan declares `data` or `assets`, so none of the 23 additive overrides load.**

Two reviewers reached this independently and it is mechanical, not editorial. Item 1 (891–899) and all eight overlay manifests specify `name`, `depends`, `auto_install`, `license`, `author`, `application` — and stop. Item 7 demonstrates the plan knows the manifest is where load behaviour is declared ("changes `__manifest__.py` … to declare `'post_init_hook'`"), which makes the omission deliberate-looking rather than shorthand.

The consequences compound:

- **14 XML view files are inert.** Items 3, 4, 5, 9, 11, 13, 15, 17, 19, 21 all say "Create `<path>.xml`". Odoo loads XML only from files listed in `data`. A file sitting in `views/` is never parsed.
- **`castadoo_user_menu.js` (item 6) is never bundled.** `static/src/**` is served, not loaded. The registry patch needs a `web.assets_backend` entry.
- **The two Owl `t-inherit` files (items 23, 24) never compile** without membership in the POS bundle — and item 23 itself warns (1129–1131) that a wrong parent fails *silently*. The plan names the failure mode and then ships it.

This is the exact failure class the document's thesis exists to prevent: a clean, correctly-built tree that renders unbranded Odoo with no error. Gate 1 counts the files as present. Gate 2 greps them as branded. Nothing loads them.

**Fix:** add a bundle table to item 1 and to each overlay — `'data': ['views/<name>.xml']` per module, `'assets': {'web.assets_backend': [...]}` for item 6, POS bundle names for items 23–25.

---

## 🔴 BLOCKER

### B1. No manifest declares `data` or `assets` — 23 overrides are never loaded
*Scope:* items 1 (891–899), 8, 10, 12, 14, 16, 18, 20, 22 (987–1119), 3–5, 9–21, 6 (950), 23–25.
*Reviewers:* `egm-implementation-readiness` (B2, B3), `egm-codebase-details` (B1), `egm-style` (1.18).

As above. Both reviewers independently confirmed item 1's `application: False` and `license: 'LGPL-3'` are correct for 17.0 — which makes the two missing keys a pure omission, not shorthand.

---

### B2. `web.web_layout` is the wrong `inherit_id` — the tree declares `web.layout`
*Scope:* item 3, line 911. *(Measured: `anchor_verification.md` A1.)*
*Reviewers:* `egm-implementation-readiness` (flagged as likely), orchestrator (confirmed).

`addons/web/views/webclient_templates.xml:17` declares `<template id="web.layout">`. The external id is module `web` + local id `layout` = **`web.layout`**. The design writes `web.web_layout`, doubling the prefix.

The remaining nine parents are correct: `brand_promotion_message` (:89), `login_layout` (:112), `webclient_bootstrap` (:247), `webclient_offline` (:285), `report_layout` (:6), `report_preview_layout` (:39), `mail_notification_layout` (:4), `mail_notification_light` (:114), `OrderReceipt` (:3). **One wrong out of ten.**

Still a Blocker: a wrong `inherit_id` raises `External ID not found` at install, and the register (`change_register.md` S1.01) already says `web.layout` — so the design contradicts the artefact Gate 1 reads.

---

### B3. Item 2 imports a package no item creates — `ImportError` on first install
*Scope:* item 2 (901–905), items 1–47.
*Reviewers:* all three.

`__init__.py` "Imports `models` (for `res_company` defaults if used) and `hooks`". No item creates `castadoo_branding/models/`, and §Data and configuration model (447–451) explicitly decides *not* to ship company defaults — so the parenthetical defends a file the plan never creates. `from . import models` on a non-existent subpackage raises at addon import: the base addon fails to load and every overlay that `depends` on it is unusable.

Compounding: the eight overlay directories each get `__manifest__.py` and **no `__init__.py`**. Odoo's loader requires it; without it the module never appears in the apps list. **Eight missing files that the footnote's arithmetic does not count.**

The plan tells the implementer to run `odoo-bin -i castadoo_branding` at 1378 — the command that fails first.

---

### B4. Gate 1 cannot pass on the tree the plan describes
*Scope:* items 35–40, item 43, item 46 (1351–1364), footnote (1413–1443), G5 (119–122).
*Reviewers:* all three, from three different angles.

Three independent arithmetic failures, each sufficient on its own:

1. **`git diff --stat` counts added files.** The plan creates ~28 files outside upstream (`castadoo/` ×24, items 44–47). "File count ≤ 37" fails on the first push, before an upstream file is touched.
2. **`--stat` counts a one-line replacement as `+1/-1` = 2 diff lines.** The register's "94 edit lines" therefore appears as ~188. "Changed-line count ≤ 94" is unreachable by roughly 2×.
3. **The register is a coverage list, not a diff list.** It counts 13 upstream view files the plan only *inherits* — those paths will not differ after the overlay. Comparing a diff count against a coverage count, and the footnote at 1440–1443 asserts the register "counts upstream paths that differ after the overlay", which its own table contradicts.

Plus a membership gap: items 43–47 change `README.md`, `CONTRIBUTING.md`, `docs/`, `.github/` — none of which the register lists, so "every changed path appears in the register" also fails.

**The plan's own footnote already knows:** 54 files in the plan, 49 must exist, 37 in the register. Stage 8's diagnosis holds — the register's best paragraph (351–357) argues count is the wrong metric, and the design shipped count anyway.

---

### B5. Items 11, 17, 19 and 24 instruct code shapes the tree does not have
*Scope:* items 11 (1016–1026), 17 (1063–1073), 19 (1081–1098), 24 (1133–1138). *(Measured: A3, A6, A7, A8.)*

Four separate defects, all confirmed against source:

**Item 11** — "The same file also hardcodes `#875A7B` … those are inside the same template region, so replacing all four occurrences is a **single inheritance edit** rather than two." Measured: `reset_password_email` (`:3`) carries `:36` and `:81`; `alert_login_new_device` (`:88`) carries `:122` and `:143`. **Four sites in two separate templates.** One `<xpath>` cannot span two `inherit_id`s. The instruction is not merely vague — it describes something impossible.

**Item 17** — "One inherited record on `hr_expense_template_register_no_user`", then requires the button at line 31. Measured: line 49 is in `hr_expense_template_register_no_user` (`:35`); **line 31 is in `hr_expense_template_register` (`:11`)** — a different template. Worse, the register lists **only** line 49 for `hr_expense` (S4.06), so Gate 1's allowlist does not cover the line-31 edit the plan mandates.

**Item 19** — "`digest.digest_mail_main` (template spans lines 270–447)", then cites lines 14 and 147. Measured: `digest_mail_main` is at `:270` and `digest_mail_layout` at `:5`; **lines 14, 58, 87 and 147 are all inside `digest_mail_layout`**. The range is also 270–451, not 270–447. The design's *conclusion* is right — `company.email_secondary_color` genuinely drives it — but the anchors point at a different template.

**Item 24** — names the file and "line 84" but never states the parent `t-name`, in an item whose own text warns that a wrong name fails silently. Measured: line 84 sits inside `point_of_sale.CustomerFacingDisplayOrder` (`:43`).

---

### B6. D7 is undecided, and three items plus the verification plan cannot be written without it
*Scope:* D7 (400–414), items 1 (894–899), 7 (971–978), 44 (1336–1342), verification (1380).
*Reviewers:* `egm-implementation-readiness` (B6), `egm-style` (2).

D7 says the plan "needs an answer before the Detailed Implementation Plan can be executed" (207) and then claims it "is written so that any of the three can be applied to the same file set" (413). Both cannot hold:

- **Option C** folds `depends` into item 1 and **deletes items 8, 10, 12, 14, 16, 18, 20, 22 entirely**.
- **Option B** adds item 7 and a `post_init_hook` key to item 1.
- **Option A** removes item 7 and item 2's `hooks` import.

Three options, three file sets. And `egm-style` adds the sequencing defect: D7 blocks items 7, 44 and half the verification plan, yet the plan executes.

Also: item 2's `hooks` import is conditional **in prose only**. Under A or C the file does not exist, so an unconditional `from . import hooks` is an `ImportError`.

---

### B7. Item 42 edits a file that does not exist, and item 44 modifies one that does
*Scope:* item 42 (1313–1322), item 44 (1336–1342), placement decision (881–887). *(Measured: A13.)*

**Item 42** presumes an existing `odoo.conf` at repo root. Measured root listing: `README.md`, `CONTRIBUTING.md`, `LICENSE`, `COPYRIGHT`, `SECURITY.md`, `ruff.toml`, `setup.cfg`, `setup.py`, `MANIFEST.in`, `odoo-bin`, `.gitignore`, `.weblate.json` — **no `odoo.conf`**. The only ones are `debian/odoo.conf` and the POS box config. Item 42 is therefore a `Create`, not a `Modify`, which changes the 37/38 upstream-path arithmetic and contradicts Tier 4's definition ("The only files with a recurring conflict surface") — the item's own body says "**Not** modified in the repo."

**Item 44** says "Create — fork-specific" for `CONTRIBUTING.md`, which **exists at root**. It is a `Modify` of an upstream file: it adds an unlisted upstream path to the diff, changes the "49 files that must exist" count, and brings the LGPL dating obligation with it.

---

## 🟠 MAJOR

### M1. Item 38 is not implementable: 87 replacements, six named
*Scope:* item 38 (1253–1283). *Reviewers:* all three.

"The 87 replacements" then names `PUBLISHER` (44), `PRODUCT_NAME` (74), `SERVICENAME` (67), `UNINSTALL_REGISTRY_KEY_SERVER` (80), contacts (423–426), `MUI_FINISHPAGE_LINK_LOCATION` (160) and "the French block (around 203–236)". **81 of 87 are unnamed.**

Measured (`X1`, `X2`): the file is 729 lines; 89 lines contain `Odoo`, 114 occurrences, 119 lines contain `odoo` any-case. **87 is not reproducible as any of those.** And "87" is used as three units — occurrences, replacements, and (1282) a superset containing the French block. The French block is 31 `LANG_FRENCH` lines that need **translation**, not substitution: whether `CASTADOO` is invariant in French is a copywriting decision the plan never makes.

`egm-style` adds: "plus three decisions that must not be made twice" is followed by **six** bullets.

**Understated opportunity:** lines 134–139 are `MUI_ICON`, `MUI_WELCOMEFINISHPAGE_BITMAP`, `MUI_UNWELCOMEFINISHPAGE_BITMAP`, `MUI_HEADERIMAGE_BITMAP` — **file paths, not strings**. Item 33 preserves those filenames, so a blanket replace breaks the installer's image references while gaining nothing. They must be listed as do-not-touch.

---

### M2. Item 39's arithmetic is wrong: 9 lines, not 8
*Scope:* item 39 (1285–1294). *(Measured: A11.)*

"8 occurrences, of which two must not change" then enumerates **nine** line numbers (2, 50, 54, 78, 83, 257, 269, 270, 323). Measured case-sensitive: **9 lines**.

The real split is not 8/2 either: only **:323** (`Odoo Bot <info@odoo.com>` in the Debian changelog) is genuinely user-visible. Lines 2, 50, 54, 78, 83, 269, 270 are licence header, exception class names and internal log/error text. `egm-style` also flags that no maintainer identity is supplied, and Debian changelog format requires `Name <email>`.

*(Confirmed good: `ruff.toml` **does** exist at root, so the plan's ruff claim is right.)*

---

### M3. `web.web_app_name`, favicon and the company fields are assigned to "deployment" and produced by nothing
*Scope:* 426–427, CUJ 4 (254–266), item 37 (1247), verification (1387).
*Reviewers:* `egm-codebase-details` (B5), `egm-style` (via 5).

Item 37 correctly does *not* edit `webmanifest.py:48` (measured exact: `get_param('web.web_app_name', 'Odoo')`). But no item sets the parameter, and the fallback is `'Odoo'`. **A fresh install from the branded tree ships `name: "Odoo"`** — the exact surface CUJ 4 promises, and the assertion at 1387 fails on a clean test DB.

Odoo's own idiom is a data record — `<record model="ir.config_parameter"><field name="value">CASTADOO</field></record>` under `noupdate="1"`. One new file, zero upstream edits, zero conflict surface — strictly cheaper than the deployment step the plan mandates, and the same record type the plan already ships 22 of.

`website.favicon` genuinely needs an uploaded Binary, so the deployment step is defensible there. `res.company.name`/`logo` likewise. **`web.web_app_name` is not.**

---

### M4. Item 4 declares two records and describes three
*Scope:* item 4 (926–937). *Reviewers:* `egm-implementation-readiness` (M2), `egm-style` (5), register S1.07–S1.09.

"The two inherited records" then lists three sites: `<img alt>` at :330, the paragraph at :332, and the `<style>` block at :293–326 with two purples at :317/:319. The register carries all three as separate items. The `<style>` rewrite cannot share an anchor with either text node, and the preferred option ("append a new `<style>` rule") is a fourth distinct xpath.

Measured: `:317` `background-color: #714B67`, `:319` `border: 1px solid #714B67`, `:326` `</style>`, `:330` `alt="Odoo logo"`, `:332` paragraph — all exact. The anchors are right; the count is wrong.

---

### M5. Item 3's `<title>` fallback does not control the browser tab
*Scope:* item 3 (911–912), CUJ 1 (211–222), verification (1386). *(Measured: A2.)*

`webclient_templates.xml:22` is `<title t-esc="title or 'Odoo'"/>`. The fallback fires only when `title` is falsy; most `/web` routes set `title` from data. Measured: `webclient_offline` sets `<t t-set="title">Offline</t>` at :288; the test templates set their own at :218/:233.

Keeping the inheritance is correct — it fixes the empty-title case. **The assertion at 1386 is wrong**: "tab reads CASTADOO" cannot pass on a deployment whose company is named anything else. Move the assertion to `title == company.name`; if CASTADOO-in-tab is a hard requirement, say so and pick a different mechanism.

---

### M6. Item 30 replaces text files while claiming the binary mechanism
*Scope:* item 30 (1187–1190), item 26's `odoo-icon.svg`, Tier 3 preamble (1167–1169).
*Reviewer:* `egm-codebase-details` (B6).

`odoo_logo.svg`, `odoo_logo_dark.svg` and `odoo-icon.svg` are XML **text**. Git diffs them line-by-line and merges can conflict inside them. Tier 3's premise — "git records a changed binary, not a hunk … whole-file replacement rather than a merge conflict" — is false for these three, and the register's `BIN` row inherits the error.

**3 of the 16 "no conflict surface" items have conflict surface.** The "wordmark with text outlined" instruction guarantees a whole-file single-line-token diff that conflicts if upstream re-saves the SVG.

*(Also resolved: the two `odoo_logo` files are the same byte size but **different SHA256** — genuinely distinct, so the register's suspicious "1,571 B each" is a coincidence, not a copy-paste error.)*

---

### M7. `Registry.remove` exists — item 6's `?` is unnecessary, and it conflates key with id
*Scope:* item 6 (950–966). *(Measured: A9.)*

`addons/web/static/src/core/registry.js:122` defines `remove(key)`. Write the concrete call.

Measured in `user_menu_items.js` (129 lines): `:12` `documentationURL = "https://www.odoo.com/documentation/17.0"` ✓; `:91` `id: "account"`; `:92` `description: _t("My Odoo.com account")` ✓; `:100` `browser.open("https://accounts.odoo.com/account", "_blank")` ✓; `:128` `.add("odoo_account", odooAccountItem)`.

**The item's id is `account`; `odoo_account` is the registry *key*.** The design conflates them (954 vs 958). `remove("odoo_account")` is correct — but the prose calling `odoo_account` "the item's id" will mislead.

---

### M8. Item 32 spends a binary overwrite on a file no module references
*Scope:* item 32 (1197–1200). *(Measured: X3, M9.)*
*Reviewers:* `egm-codebase-details` (M9), orchestrator.

`addons/website_links/static/img/default_favicon.png` **exists**, but `git grep -i favicon` across the module returns only `i18n/*.po` `msgid "Icon"` hits, and `website_links_template.xml` contains no favicon or logo reference. The design's "Default link-preview icon" role is unsupported by the module it names.

Either cite the actual consumer (a `website` controller fallback, or the link-tracker preview path) or move it beside item 34 as a documented non-change — which changes 16 → 15 binaries.

---

### M9. Item 7's hook has no signature, no API and no failure policy
*Scope:* item 7 (968–978). *Reviewers:* `egm-implementation-readiness` (M13), `egm-style` (1.3).

"Must be idempotent, must not raise if an overlay is missing from the path, and must log what it installed" — three properties, no code. Missing: `post_init_hook(env)` signature (17.0 takes `env`, not `cr, registry`), the manifest key literal, the module→addon mapping, and the registry-reload hazard (`button_immediate_install()` reloads the registry while the base module's own install transaction is open).

---

### M10. Item 46's patterns and allowlist exist nowhere
*Scope:* item 46 (1351–1364), item 45 (1344–1349). *Reviewers:* `egm-style` (1.4), `egm-implementation-readiness` (B8).

"grep the tree for the **enumerated patterns**" — no pattern list appears in the document or the register. The allowlist is "by reason" with four strings, but no file path, no key schema, and no statement of how CI parses a markdown register. Also `--stat` is not "changed-line count" (see B4), and the workflow cannot assert `git rev-parse 17.0 == upstream/17.0` without fetching both refs.

`egm-codebase-details` adds: item 43's `#875A7B` in `README.md` has **no truthful allowlist category** among the four (internal identifier / D1-C / licence notice / not user-visible). A hex colour in a README needs a fifth reason or prose rewrite.

---

### M11. The verification plan names no harness and one command is vacuous
*Scope:* 1376–1411. *Reviewers:* `egm-implementation-readiness` (M9), `egm-codebase-details` (M11).

- **`odoo-bin --test-tags /castadoo_branding` (1395)** — **no item creates a `tests/` directory or a single test file.** The tag selects nothing and exits 0. It is also not manifest validation; that happens at module load.
- **`--addons-path` is omitted** from the 1378 command, which is the very thing item 42 exists to supply.
- **`--version` does not list modules** (1381); that needs a DB query.
- **1382's "must show all 9 addons"** conflicts with item 22 being called optional and item 7 being conditional. The pass condition is 8, 9, or 10 depending on D7 and the optionality decision.
- **No assertion exists for items 6, 35–42** except a diff count — the user menu, release description, db-manager strings and installer are unverified.
- **The suite is not hermetic**: `res.company.name`, `email_secondary_color` and `web_app_name` are deployment data the plan says it will not ship (M3). The colour and name assertions cannot pass on a clean DB.

**Odoo 17.0 already provides what the plan reinvents:** `HttpCase` for the two GET assertions; an existing `addons/web/tests/test_webmanifest.py` that already exercises exactly the `name`/`background_color`/`theme_color`/`icons` fields asserted at 1387; `browser_js` for the computed-style assertion at 1389 (unmeasurable server-side otherwise); `MailCase`/`assertEmailSent`/`_render_template` for the rendered-email assertion at 1390. The PDF assertion (1391) needs text extraction and trailer parsing, neither of which is an Odoo test dependency — restate it at the HTML layer or declare the dependency.

---

### M12. D1-C compares the wrong mechanism
*Scope:* 153–156, 700–712, 854–858. *Reviewer:* `egm-codebase-details` (M12); corroborates Stage 5 M9.

Alternative K and the Future Improvements entry evaluate a `post_init` hook that **mutates `body_html` in place** — the variant with the rollback hazard — and reject D1-C on that basis. Odoo's own extension point is the model layer: subclass `mail.template` and override `_render_template()`, applying at render time. No data record, no `noupdate` row touched, no migration to roll back, gone on uninstall.

Measured support: `auth_signup/data/mail_template_data.xml:3` is `<data noupdate="1">` containing `set_password_email` (:5), `mail_template_data_unregistered_users` (:101), `mail_template_user_signup_account_created` (:153) — the `noupdate` premise is real. But the document rejects *one implementation* of the middle path and calls it the middle path.

---

### M13. Item 41, Open Question 2 and item 42 give three incompatible dispositions for phone-home
*Scope:* item 41 (1304–1311), OQ2 (541–543), item 42 (1313–1322).
*Reviewer:* `egm-codebase-details` (M7).

Item 41 makes it a source edit. OQ2's shapes say it decides "whether the shipped `odoo.conf` template carries one extra commented line". Item 42 says `odoo.conf` is "**Not** modified in the repo", so the "shipped template" does not exist. One decision, three mechanisms, two mutually exclusive.

The cheapest reading — a config key in the operator's file — removes item 41 from the diff entirely. The plan should say so rather than leave it conditional.

---

### M14. Three unranked superlatives and a framing claim that is false
*Scope:* 878–879, 932, 1006, 1229. *Reviewer:* `egm-style`.

"the most fragile item in the whole register" (932), "the single highest-value change in the email surface" (1006), "the single most important non-change in the plan" (1229) — three unfalsifiable rankings in one section.

And the opening: **"the pseudocode and shapes are what the implementer needs to make no further decisions."** There is no pseudocode anywhere in 874–1449, and at least eleven items hand a decision back. `egm-style`'s diagnosis is exact: *"A work order that opens by asserting it contains no open decisions trains the reader to stop looking for them."*

The heading vocabulary is also uncontrolled — eight status qualifiers (`Create`, `Create — conditional on D7`, `Create — optional`, `Modify — binary`, `Modify — conditional on Open Question 2`, `Modify — deployment artefact, not a repo file`, `Create — tooling, optional`, `— excluded`) means a build list cannot be derived without reading every body. Recommend two fields: **Action** (Create/Modify/None) and **Gate** (none/D7/OQ2), dropping "optional" as a status.

---

### M15. Item 26 remains filed in the wrong tier
*Scope:* item 26 (1149–1163), Tier 3 heading (1165). *Reviewers:* all three, and Stage 8.

Under "Tier 1 — base addon `castadoo_branding`", item 26's own text says "These are **not** new files in `castadoo/`. They are overwrites of upstream blobs" — and `### Tier 3 — binary replacements at existing paths` begins immediately after. Nothing in item 26 belongs to the addon. A reader building the addon tree from Tier 1 creates six paths that should be overwrites.

---

## 🟡 MINOR

| # | Finding | Scope | Reviewer |
|---|---|---|---|
| m1 | Item 35's replacement string is absent — the entire item is one literal that is not given | 1224 | all three |
| m2 | Item 5's fallback literal unspecified: `'CASTADOO Report'` or `'CASTADOO'`? | 946, 948 | style 1.6 |
| m3 | Three CASTASOFT hrefs with no URL; only `https://castasoft.yukreasi.id` appears, once at line 14 | 915, 916, 1281 | style 1.7 |
| m4 | Item 4's paragraph replacement text absent entirely | 929 | style 1.8 |
| m5 | Optionality stated three incompatible ways: item 22 "second optional" (1121), item 25 "the two optional files" (1145), footnote "3 optional (items 25 and 47)" (1434) | 1121, 1145, 1434 | readme N2, style 5 |
| m6 | Item 25 is self-cancelling — "can be skipped … because the image it renders is `logo2.png`, which is replaced in place" | 1140–1147 | readme M5, style |
| m7 | "23 additive items" is computed from defective record counts; corrected items 4/11/17 give 27 | 120, 656, 1419–1432 | codebase M4 |
| m8 | Item 43 claims items 27 and 9 fix README prose; neither can reach `README.md` | 1332–1334 | codebase M6 |
| m9 | Item 40 is self-contradictory: "Keep the LGPL-3 text verbatim. Add the CASTASOFT copyright line" | 1296–1302 | readme N4 |
| m10 | Item 42's cross-reference still says "(see item 35)"; item 35 is `release.py` | 882 | ALL |
| m11 | `addons_path` must be **first**; item 42 says only "one entry". Also `--addons-path` on the command line *replaces* the config, making the entry inert for the plan's own test command | 881–887, 1316 | codebase M10 |
| m12 | Item 33's BMP geometry unspecified; NSIS MUI bitmaps have fixed pixel expectations | 1205–1207 | readme N7, style 1.19 |
| m13 | Item 3's `src` instruction is redundant — the filename is preserved by item 26 | 913–915 | readme N9 |
| m14 | Item 21 cites "lines 67–70" and item 9 "103–109"/"177–183"; an xpath cannot target a range | 998, 1004, 1110 | readme N3, N4 |
| m15 | 1409's "conflict count must be zero or confined to `setup.nsi`" has no bound; 1255 admits 87 there | 1409 | style 2 |

---

## 🟢 NIT

| # | Finding | Scope |
|---|---|---|
| n1 | Item 2's "if used" defends a file the plan never creates | 904 |
| n2 | Item 45's "moves" ambiguous — does the root register remain? | 1347 |
| n3 | Item 40 needs the copyright symbol's RTF encoding guidance | 1299–1302 |
| n4 | 1378's command omits `--addons-path` | 1378 |
| n5 | Sync rehearsal (1408–1411) is conditional on OQ1; mark it blocked or the "design done" gate never satisfies | 1408–1411 |
| n6 | Item 37 is the model the other in-place edits should follow — two lines, two literals, no ranking | 1247 |
| n7 | ~40 cited anchors remain unmeasured; listed in `verified_ground_truth.md`'s closing note | passim |

---

## Count table — every quantity with more than one value

Built from `egm-style`'s audit of 874–1449, cross-checked against the measured tree.

| Quantity | Values | Where | Resolved by |
|---|---|---|---|
| Total files in plan | 54, 49, 47, 37 | 1432, 1436, 1434, 1355 | B4 — four different scopes |
| Committed binaries | 16, 11, 15 | 1425, 800, (M8 would make it 15) | Item 26 = 6 + items 27–33 = 10 → **16** |
| `setup.nsi` units | 87 strings, 87 replacements, 87 lines, 89 lines, 114 occurrences | 1255, 1256, 34, 120, 638 | Measured: **89 lines / 114 occurrences**; 87 reproducible as neither |
| `package.py` occurrences | 8, 9 | 1288 vs measured | **9**, of which 1 user-visible |
| Additive items | 23, 22, 27 | 34/120, 811, (m7) | Requires the corrected record counts |
| Inherited records: item 4 | 2, 3 | 926 | **3** |
| Inherited records: item 11 | 1, 2, 4 | 1019, 1026 | **4 across 2 templates** |
| Inherited records: item 17 | 1, 2 | 1066 | **2 across 2 templates** |
| Digest range | 270–447, 270–451 | 1085 | **270–451**, and colour lines are in `digest_mail_layout` |
| Optional files | 2, 3 | 1145, 1434 | Author decision |
| Addons in verification | 9 | 1382 | 8, 9 or 10 depending on D7 |
| In-place edit sites | 4, 6 | 815, items 35–40 | **6** |
| Entries | 47 | 1415, 1432 | Consistent ✓ |

---

## What the four stages agree on

Every stage independently reached the same conclusion about the same artefact: **the plan is specified at the level of intent and not at the level of execution.** Stage 5 said the gates are the wrong mechanism. Stage 7 said every load-bearing quantity is hand-typed. Stage 8 said the metric contradicts the register's own best paragraph. Stage 9 measured it and found the manifests do not load the files, the gate cannot compute its own numbers, and four items describe code shapes the tree does not have.

Stage 8's repair sequence stands unchanged, and Stage 9's findings are what it predicted:

1. **Decide Surface 5** — it determines whether a third of the document needs to exist.
2. **One declarative change manifest** — derive the register, the budget, the allowlist and the file table from it.
3. **Name the two missing artefacts** — the deployment checklist and the rendered-output assertion suite.

Stage 9 adds a fourth, which is mechanical and cheap:

4. **Add `data` and `assets` to every manifest, give item 2 a real `__init__.py`, and add eight overlay `__init__.py` files.** Without this, none of the rest of the plan has any effect.

---

**Totals: 7 Blocker · 15 Major · 15 Minor · 7 Nit.**
