# Consolidated Review Report

**Target:** `docs/designs/castadoo-rebrand-fork.md` (1,449 lines, 86,225 bytes)
**Reviewed against:** Odoo 17.0 @ `9c58cae5d6e3cf91ac1cca7df39fb21f68ca6e15`
**Stages run:** 5 (Initial Zoom Out) → 6 (Comprehension) → 7 (Critic) → 8 (Intermediate Zoom Out) → 9 (Implementation Readiness)
**Reviewers:** 12 persona runs across 8 distinct Goldfish personas
**Date:** 2026-11-17

---

## Executive summary

The document is **structurally sound and evidentially better than most designs of its size**, and it is **not executable as written**. Both statements are true and they are not in tension.

Five independent review stages converged on one diagnosis that no single reviewer produced alone:

> **The design specifies every load-bearing quantity in prose and never in an artefact, so nothing can recompute it, and the three enforcement mechanisms built on those quantities all fail.**

The consequences are specific and mechanical:

- **Nothing loads.** No manifest in the plan declares `data` or `assets`. All 14 XML view files, the JS user-menu patch and the two Owl templates are created and never executed. A perfectly built tree renders unbranded Odoo with no error — the exact failure the design exists to prevent.
- **The budget cannot be computed.** `git diff --stat` counts added files and counts a one-line edit as two. Gate 1 fails on the plan's own first commit.
- **The configuration tier is unreachable.** Four of five branded values are "Set by: deployment" and produced by no item. Neither gate can see a database.
- **Four items instruct code shapes the tree does not contain.** Four sites across two templates called "a single inheritance edit"; one record spanning two templates; a parent `t-name` never named; a wrong `inherit_id`.

**The document is repairable by targeted edits, not a rewrite.** Two reviewers said so explicitly and independently. The section ordering, the mechanism taxonomy, the alternatives analysis and the measurement work are all worth keeping — the Stage 8 reviewer's words were *"better than most designs of this size, and the ordering is load-bearing. Do not restructure the document."*

**What must change is where intent is stored**, not what the intent is: one declarative change manifest from which the register, the budget, the gate allowlist and the file table are all derived.

**Raw findings:** 178 across five reports (19 Blocker, 90 Major, 25 Minor, 44 Nit).
**After deduplication:** 34 consolidated action items (9 Blocker, 14 Major, 11 Nit). The 144 → 34 reduction is almost entirely cross-stage convergence: the same defect seen from strategic, naive-reader, architectural, editorial and executional angles.

---

## The four root causes

Every Blocker resolves to one of four causes. This matters because fixing them individually buys one clean revision; fixing the causes makes the defects unexpressible.

### RC1 — Intent lives in prose, so nothing recomputes it (11 items)

The budget, the register's line numbers, the gate allowlist, the D7 file set, the config values and the count of every inventory are hand-typed. Four revisions produced four fresh crops of count contradictions — eight found in Stage 6, ten in Stage 7, thirteen distinct quantities disagreeing in Stage 9. **A hand-typed count drifts by construction.**

Stage 8's sharpest observation: the register's own best paragraph (351–357) argues that count is the wrong metric — `setup.nsi` is 86% of the volume but a low conflict *rate* — and then the design shipped count as Goal G5, as Gate 1, as the effort estimate and as the difficulty narrative. **The document found the right answer and did not adopt it.**

### RC2 — The plan specifies structure but not wiring (6 items)

Items say "Create `<path>`". They do not say how the path is loaded. This is the difference between a design and a work order, and the document claims to be both ("the implementer needs to make no further decisions").

### RC3 — Decisions are left open while the plan presents itself as closed (5 items)

D7 has three options, "two options, and the implementer must pick one" (933), "needs a decision at implementation time" (1240), "either repoint … or remove" (962), three toolchain pairs. Each is a decision the plan was supposed to make. The opening claim that no decisions remain *trains the reader to stop looking for them*.

### RC4 — The cheapest tier is outside the artefact entirely (3 items)

Configuration is the only mechanism that is genuinely zero-conflict — and it lives in a database that no gate, no diff and no register can inspect. A correctly built tree deploys unbranded with no error, and the design concedes this only in Future Work.

---

## 🔴 BLOCKER — 9 consolidated items

### A1. Decide whether the fork is justified, before anything else

*Sources:* S8-B1 · S7-B3 · S5-M5 · S7-M20 · S9-…
*Scope:* Non-Goals 165–166; Technical Plan 344–414; sync procedure 486–531; Alternatives 563–614.

The fork exists for exactly one reason and the document never states it: **`setup.nsi` cannot be reached from `addons_path`.** Every other in-tree file is one, two or four lines:

| File | Lines |
|---|---|
| `release.py` | 1 |
| `webmanifest.py` | 2 |
| `database_manager.qweb.html` | 4 strings |
| `setup/package.py` | 8 |
| `License.rtf` | 1 |
| `setup.nsi` | 87 (measured: 89 lines) |

Surface 5 is 87 of the 94 in-place lines. **The Non-Goals state that no installer will be built, and CUJ 5 requires building one.** If Surface 5 is out of scope, the in-tree diff is ~7 lines and the correct artefact is a patch file plus a separate addon repository — and G1–G3, D2, the sync procedure and Alternatives A–F should be deleted. A fork with a 7-line overlay and a `--no-ff` merge ritual is answering a question nobody is asking.

**Three genuinely viable alternatives are missing from 15** (S7-M20): a separate branding repo on `addons_path` (23 of 37 items never touch upstream); don't fork at all; defer Surface 5.

**Decision required from you.** This single answer determines whether a third of the document survives.

---

### A2. No manifest declares `data` or `assets` — 23 overrides never load

*Sources:* S9-B1 · S9-B3 · S6-B5 · S7-…
*Scope:* items 1 (891–899), 2 (901–905), 8–22, 3–5, 9–21, 6 (950), 23–25.

Item 1 and all eight overlay manifests specify `name`, `depends`, `auto_install`, `license`, `author`, `application` — and stop. Item 7 proves the plan knows the manifest is where load behaviour is declared.

- **14 XML view files are inert.** Odoo loads XML only from files listed in `data`.
- **`castadoo_user_menu.js` is never bundled.** `static/src/**` is served, not loaded. Needs a `web.assets_backend` entry.
- **The two Owl `t-inherit` files never compile** without POS bundle membership — and item 23 itself warns that a wrong parent fails silently.
- **Item 2 imports `models`, which no item creates** → `ImportError` at module load. The base addon never installs.
- **Eight overlay directories get no `__init__.py`** → modules never appear in the apps list.

**Fix:** `'data': ['views/<name>.xml']` per module; `'assets': {'web.assets_backend': [...]}` for item 6; POS bundle names for items 23–25; item 2 becomes `from . import hooks  # only under D7-B`; add eight `__init__.py` files (one item covering all eight).

---

### A3. Gate 1 cannot pass on the tree the plan describes

*Sources:* S7-B1 · S6-B2 · S9-B4 · S8-M3 · S5-M1
*Scope:* G5 (119–122), Gate 1 (495–499), item 46 (1351–1364), footnote (1413–1443).

Three independent arithmetic failures, each sufficient:

1. **`--stat` counts added files.** ~28 new files outside upstream. "≤ 37 files" fails before an upstream file is touched.
2. **`--stat` counts a replacement as `+1/-1`.** 94 edit lines appear as ~188. "≤ 94" is unreachable by 2×.
3. **The register is a coverage list, not a diff list.** It counts 13 upstream view files the plan only *inherits* — those paths never differ.

Plus: items 43–47 change `README.md`, `CONTRIBUTING.md`, `docs/`, `.github/` — none in the register.

Items 39 and 40 add 9 lines the register's own 94 excludes — real in-place volume is **103**, not 94.

**Fix:** the metric must exclude additions by construction (`--diff-filter=M`, path-scoped exclusions), and the budget must be re-derived from a manifest rather than typed. G5's quantity should also change: budget `lines × upstream-touch-frequency`, not raw count (A5).

---

### A4. The configuration tier is produced by nothing and invisible to both gates

*Sources:* S7-B2 · S6-#17 · S5-M7 · S9-M3
*Scope:* rank 1 (332–334), data model (416–451), CUJ 1/4, item 37 (1247), verification (1387).

`res.company.name`, `.logo`, `.email_secondary_color`, `web.web_app_name`, `website.favicon` are all "Set by: deployment". **No item produces them.** Gate 2 greps the tree; Gate 1 diffs paths. Neither can see a database.

Consequence: a branded tree on a fresh DB yields a blank logo, `name` = "YourCompany", unset `web_app_name` (**stock fallback `'Odoo'`** — measured exact at `webmanifest.py:48`) and unset `email_secondary_color`. CUJ 1 passes on the inherited footer alone.

**Three of the five are shippable as `noupdate="1"` module data** — `web.web_app_name`, favicon default, email colour. `res.company.name`/`logo` genuinely belong to deployment.

**Fix:** seed the three; add a third assertion tier for post-deploy rendered output; keep company name/logo as deployment with a written checklist.

---

### A5. The budget measures the wrong quantity, and the register says so

*Sources:* S8-M3 · S9-B4 · S7-B1
*Scope:* G5, 58–61, register 351–357.

The register argues `setup.nsi` is "86% of the in-place edit volume by count, but it is a leaf file that upstream touches once or twice a year… `webmanifest.py` is 2 lines and upstream touches it most years — that is a higher conflict *rate* per line… **Ranking by count would put the effort in the wrong place.**"

Three lines later the design adopts count as Goal G5, as Gate 1, as the effort estimate, and as the difficulty narrative. **The document's best paragraph contradicts its headline goal, and the goal won.** No earlier stage caught this; Stage 8 did.

**Fix:** budget `lines × upstream-touch-frequency-per-release`, or budget only paths upstream touched in the last N point releases. Report `setup.nsi` as volume-with-low-rate.

---

### A6. Four items instruct code shapes the tree does not contain

*Sources:* S9-B5 · S9-B2 · S5-… (all measured by the orchestrator)

**Item 3** — `inherit_id="web.web_layout"`. Measured: `webclient_templates.xml:17` declares `id="layout"`, so the external id is **`web.layout`**. Doubling the prefix raises `External ID not found` at install. The register already says `web.layout` — so the design contradicts the artefact Gate 1 reads. *(9 of 10 other parents are correct.)*

**Item 11** — "four occurrences … a **single** inheritance edit". Measured: `reset_password_email` `:3` carries `:36`/`:81`; `alert_login_new_device` `:88` carries `:122`/`:143`. **Four sites, two separate templates.** One xpath cannot span two `inherit_id`s — the instruction describes something impossible.

**Item 17** — "one inherited record on `hr_expense_template_register_no_user`", then requires the button at line 31. Measured: `:49` is in `_no_user` (`:35`); **`:31` is in `hr_expense_template_register` (`:11`)** — a different template, and **not in the register** (S4.06 lists only line 49), so Gate 1 would pass a tree still carrying the `#9E588B` button.

**Item 19** — "`digest_mail_main` (270–447)", citing lines 14 and 147. Measured: `digest_mail_main` is at `:270` (ends 451); `digest_mail_layout` at `:5`. **Lines 14, 58, 87, 147 are all inside `digest_mail_layout`.** The conclusion is right — `email_secondary_color` does drive it — but the anchors point at a different template.

**Item 24** — names the file and "line 84" but never states the parent `t-name`, in an item whose own text warns a wrong name fails silently. Measured: line 84 is inside `point_of_sale.CustomerFacingDisplayOrder` (`:43`).

**Fix:** correct the parent ids, replace "single edit" claims with concrete per-template anchors, and supply every missing anchor expression.

---

### A7. D7 is undecided, and items 1, 2, 7, 44 plus the verification plan cannot be written without it

*Sources:* S7-B4 · S6-#4 · S9-B6 · S5-M10 · S7-M10 · S8-M4

D7 says the plan "needs an answer before the Detailed Implementation Plan can be executed" and then claims it "is written so that any of the three can be applied to the same file set." Both cannot hold:

- **Option C** folds `depends` into item 1 and **deletes items 8, 10, 12, 14, 16, 18, 20, 22**.
- **Option B** adds item 7 and a `post_init_hook` key.
- **Option A** removes item 7 and item 2's `hooks` import.

Three options, three file sets. Item 2's conditional import is conditional **in prose only** — an unconditional `from . import hooks` is an `ImportError` under A and C.

**A fourth mechanism exists** (S5-M10): `migrations/<version>/post-*.py` runs on every `-u castadoo_branding` — the command the sync path already mandates. Bumping the manifest version at each sync makes convergence a by-product, using the same trick D2 uses for LGPL dating.

**Also: D7 has no row in the register's decision sheet**, which ends at D6 (`change_register.md:416`), while Gate 1 checks the diff against that register.

**Decision required.** Adding D7 to the register is part of the fix.

---

### A8. Every security control lives in a document the plan does not produce

*Sources:* S7-M23 · S7-M24 · S7-M25 · S7-M26 · S7-M27 · S8-M1 · S8-M2

- **Phone-home** is parked on Open Question 2 with no default. Item 41 makes it a source edit; OQ2 says it is a conf line; item 42 says `odoo.conf` is not in the repo. **Three incompatible dispositions.**
- **`list_db` / `admin_passwd`** are deferred to "the runbook" — cited six times (405, 547, 782, 785, 1320, 1340), created by no item.
- **`DEFAULT_POSTGRESQL_PASSWORD 'openpgpwd'`** (measured exact at `setup.nsi:87`, the only instance in the tree) ships in a product installer. "Would break existing installs" does not hold: this fork's install base is new installs by definition.
- **Bus factor is one**, and the answer is documentation. No owner is named anywhere; no gate verifies itself.
- **"No credential is touched"** (786–790) is contradicted by the next sentence.

**Fix:** a one-page deployment checklist as a third deliverable; D3 turned into a decision with a default; the password forced on first run or recorded as accepted risk; a named backup owner.

---

### A9. The LGPL claim is asserted, not cited — and it conflates licence with trademark

*Sources:* S7-M25 · S7-M20(Style-C8) · S6-#29

"LGPL-3 permits this. It does not permit the fork to *claim* to be Odoo" mixes two legal frames, contradicting 151–152 and 720–723. LGPL grants no trademark rights, and the deliverable puts CASTADOO — a mark containing Odoo's — on publisher fields and login pages with no confusion analysis.

G7 calls the dating obligation "structural, not documentary", but step 6 dates only merge commits: **an overlay commit between syncs has no dating mechanism**, and the ~25 new files' licence headers are never stated.

Separately *(measured)*: `release.py:33` is `author = 'OpenERP S.A.'` — **not `Odoo S.A.`**. Item 35 correctly freezes it, but the design's rationale describes a value the tree does not contain, and an implementer reading "Odoo S.A." may "correct" the field and break the Windows datadir path (`config.py:50`, measured exact).

**Fix:** a legal risk row with an owner; state the new files' headers; cite the clause or downgrade "the licence requires" to a policy choice; say `OpenERP S.A.` in item 35.

---

## 🟠 MAJOR — 14 consolidated items

### B1. One declarative manifest replaces the register, the budget, the allowlist and the file table

*Sources:* S8-Q1/Q2 · S7-M2 · S7-M6 · S6-B1 · S9-M10

~80 rows in `castadoo/change_manifest.toml` with four record types (`[[change]]`, `[[setting]]`, `[[assertion]]`, `[[allowlist]]`). The register becomes a rendering; Gate 1 diffs against `[[change]]`; Gate 2 against `[[allowlist]]`; the budget is a `WHERE`; the footnote table is a `GROUP BY`.

**~100 lines of checker — the cheapest component in a plan priced at ≈17 h**, and it reopens no decision. It makes A3, A5, and most count findings (B2) unexpressible rather than fixed.

**This is the single highest-leverage repair in the whole review.**

---

### B2. Replace the five-tier ordinal with four boolean columns

*Sources:* S8-Q2 · S6-#15 · S7-…

`Tier` is one ordinal scale pretending to answer four orthogonal questions: recurring conflict surface, reversible-by-uninstall, counted-by-budget, upstream-owned. It cannot, and the proofs are in the document — item 26 filed under Tier 1 while being six upstream blob overwrites; item 42 filed under "the only files with recurring conflict surface" while being "**Not** modified in the repo."

That is why 20 files produce "4 irreversible" (815), "16 binaries" (864), "11 committed binaries" (800) and "17 images" (register 279). **Not four arithmetic slips — one relation answering four questions.**

With four booleans, "20 files not 4" is a `WHERE` clause.

---

### B3. Gate 2's allowlist is unbounded and its patterns do not exist

*Sources:* S7-M7 · S6-B1 · S5-M1 · S9-M10

1,343 residual hits across 591 files, plus 5,496 mandated headers and 18,920 `.po` files. "grep for the enumerated patterns" — **no pattern list exists in the document or the register.** No path scoping, no `.po` exclusion, no ceiling, no owner. The design predicts its own failure: "otherwise it fills with noise and gets disabled" (509–510). And its central methodological finding — "a case-sensitive grep cannot tell a brand string from an identifier" — is the argument against its own gate.

The correct mechanism (rendered-output assertions) is already written down — as *Future Work*.

**Measured support for the scale problem:** `git grep -l "Powered by Odoo"` returns **52 files**, against a table scoped to 13; `git grep -l "Sent by"` returns **180**. Neither is reconciled.

---

### B4. The binary/replacement model is wrong in three ways at once

*Sources:* S5-M3 · S7-M12 · S9-M6 · S6-#16

- **"Conflict surface: none — git sees a new blob, not a hunk"** is false. Both sides modifying a binary path yields `CONFLICT (content)` with no hunk resolution. "Take ours" silently discards upstream fixes.
- **Three of the 16 are text.** `odoo_logo.svg`, `odoo_logo_dark.svg`, `odoo-icon.svg` are XML — git diffs them line-by-line and they *will* conflict. The "outlined wordmark" instruction guarantees a whole-file single-token diff.
- **The rollback story collapses two kinds of change.** Uninstalling restores the ~25 additive addon files; it restores **nothing** for 16 overwritten blobs. The non-reversible set is 20, not 4.

**Fix:** `.gitattributes merge=ours` scoped to the 13 true binaries; classify the 3 SVGs as text; split the rollback claim three ways.

---

### B5. "Cheap to sync" measures the smaller of two costs

*Sources:* S8-M1 · S7-M26

The thesis counts **merge** cost and omits recurring **human** cost: re-applying 87 lines after take-upstream, manual POS receipt print, manual email-client check, manual PWA install on two devices, asset recompile, and under D7-B a `-u` per sync. Plausibly **1–2 hours per point release against a merge cost near zero.**

Also: "Rollout and rollback" contains no rollout. An existing stock database moving to branded has no path — module install, `-u`, asset rebuild, five config values, service-worker invalidation.

---

### B6. Two decisions are priced to the hour; the two that change the shape are unpriced

*Sources:* S8-M2 · S7-M18 · S7-M21

D1-C vs D1-A is priced at 37/94/≈17 h against 43/101/≈19 h — a two-hour delta that excluded customer first-contact mail. Meanwhile **D7 and Surface 5 are unpriced**, and those two determine whether a third of the document exists.

Worse: those two hours sit inside a ≈17 h figure the register documents as excluding the four largest components. **The only quantified decision in the design is quantified inside a number the design admits is wrong by an unknown factor.**

---

### B7. Three unranked superlatives, a false framing claim, and an uncontrolled heading vocabulary

*Sources:* S9-M14 · S7-M32 · S7-…

> "the pseudocode and shapes are what the implementer needs to make no further decisions"

**There is no pseudocode anywhere in 874–1449**, and at least eleven items hand a decision back. A work order that opens by asserting it contains no open decisions trains the reader to stop looking for them.

Eight status qualifiers in headings with no controlled vocabulary; "optional" floats between required and absent across three items.

**Fix:** two fields — **Action** (Create/Modify/None) and **Gate** (none/D7/OQ2).

---

### B8. Three sections answer "may a clone duration be quoted?" three ways

*Sources:* S7-M17 · S6-#26

G6: "clone in minutes rather than hours". OQ4: two bandwidth measurements disagree by ~34×. NFR: "so no duration is quoted."

---

### B9. The measurement chain cannot be reconstructed

*Sources:* S7-M6 · S6-#10 · S7-M4

"26,560 **files** contain Odoo; 5,496 of the matching **lines**; 18,920 translation files. Of the remaining 1,343 hits…" — the 8,985 step is missing. 26,560 − 5,496 − 18,920 = **2,144**, not 1,343. Non-Goals then treats 18,920 as a *file* count while Alternative M says "3,410 `.po` files" for the same set.

---

### B10. Non-viable alternatives, and one rejected on a false ground

*Sources:* S7-M18 · S7-M19 · S7-M21 · S7-M22

- **Alternative J** rests on an unmeasured precedence claim: `!default` does **not** block a plain assignment in a later-loaded file. A new asset-bundle file is mechanism 2, not 4. Its second half ("not one of the six surfaces") is circular — G4 lists the backend shell as in-scope.
- **Alternative G** is a strawman; it discredits its own 290 figure two sentences later, and the real competitor (in-place edit of ~30 rendered files) is never compared.
- **Alternative N** is rejected as "staff-facing", contradicted by 154–156 naming portal-invitation and account-created as customer first-contact mail.
- **Alternative M** is "rejected provisionally" — deferred, not rejected.

---

### B11. D1-C compares the wrong mechanism

*Sources:* S5-M9 · S9-M12 · S7-…

Alternative K evaluates a `post_init` hook that **mutates `body_html` in place** — the rollback-hazard variant — and rejects the middle path on that basis. Odoo's extension point is the model layer: subclass `mail.template`, override `_render_template()`, post-process the rendered body. No data record, no `noupdate` row, no migration, gone on uninstall.

*(Measured: `auth_signup/data/mail_template_data.xml:3` is `<data noupdate="1">` — the premise is real; the rejected implementation is not the only one.)*

---

### B12. Item 38 is not implementable; items 39 and 40 are wrong on their own arithmetic

*Sources:* S9-M1 · S9-M2 · S6-#6 · S7-…

**Item 38:** "87 replacements", six named, **81 unnamed**. Measured: 729 lines, **89 lines contain `Odoo`**, **114 occurrences**. 87 is reproducible as neither. Used as three units (occurrences / replacements / superset-with-French-block). The French block is 31 `LANG_FRENCH` lines needing *translation*. Lines 134–139 are pixmap **paths**, not strings — a blanket replace breaks the installer.

**Item 39:** "8 occurrences, two must not change" — then enumerates **nine**; measured **9**. Real split: **1** user-visible (`:323` `Odoo Bot <info@odoo.com>`), the rest internal identifiers.

**Item 40:** "Keep the LGPL-3 text verbatim. Add the CASTASOFT copyright line." Verbatim and additive are mutually exclusive. Path is `setup/win32/static/doc/License.rtf` (design omits `static/doc/`); **2** `Odoo` occurrences, not 1.

---

### B13. Gate 2's own logic is contradicted by item 43's content

*Sources:* S9-M10(codebase M6) · S7-M7

`#875A7B` appears in `README.md`. Item 43 claims items 27 and 9 fix it — neither can; item 27 replaces a *blob*, item 9 is a new QWeb view. Gate 2 will hit the hex colour, and **none of the four allowlist reasons is truthful for it.**

Also: `README.md` is upstream-owned and Modified, so it is a 38th upstream path the register does not list. `CONTRIBUTING.md` **already exists** (measured) — item 44 says "Create".

---

### B14. The verification plan names no harness, and one command is vacuous

*Sources:* S9-M11 · S9-M7 · S7-B3

- `odoo-bin --test-tags /castadoo_branding` — **no item creates a test file.** The tag selects nothing and exits 0. It is also not manifest validation.
- `--addons-path` omitted from the 1378 command — the thing item 42 exists to supply.
- `--version` does not list modules.
- "must show all 9 addons" conflicts with item 22 optional and item 7 conditional.
- **No assertion for items 6, 35–42.** The user-menu patch, release description, db-manager strings and installer are unverified.
- **Not hermetic** — company name, email colour and `web_app_name` are deployment data the plan will not ship.

**Odoo already provides what the plan reinvents:** `HttpCase`; an existing `addons/web/tests/test_webmanifest.py` exercising exactly the `name`/`background_color`/`theme_color`/`icons` fields asserted at 1387; `browser_js` for computed style; `MailCase`/`assertEmailSent`/`_render_template` for rendered email.

---

## 🟢 NIT — 11 consolidated items

| # | Item | Sources | Scope |
|---|---|---|---|
| C1 | **Count contradictions, 13 quantities** — files (54/49/47/37), binaries (16/11), `package.py` (8/9), additive (23/22/27), records per item (4: 2/3; 11: 1/4; 17: 1/2), digest range (270–447/451), optional (2/3), in-place sites (4/6). All dissolve under B1+B2 | ALL | passim |
| C2 | **`web.web_app_name` fallback assertion is wrong** — `<title>` is data-driven; move to `title == company.name` | S9-M5 | 911, 1386 |
| C3 | **Item 32's consumer is unestablished** — nothing in `website_links` references `default_favicon.png`; `git grep -i favicon` returns only `.po` hits | S9-M8 | 1197–1200 |
| C4 | **Item 4: two records, three sites** — `:317`/`:319`/`:330`/`:332` all measured exact; the count is wrong | S9-M4 | 926–937 |
| C5 | **`Registry.remove` exists** — `registry.js:122`. Write `remove("odoo_account")`; item id is `account`, `odoo_account` is the key | S9-M7 | 950–966 |
| C6 | **Item 26 is in the wrong tier** — Tier 1 heading, Tier 3 content | S7-…, S8-Q2, S9-M15 | 1149–1165 |
| C7 | **Ten terms undefined** — QWeb, xpath inheritance, Owl `t-inherit`, `auto_install`, `noupdate`, `ir.config_parameter`, `addons_path`, blobless clone, promisor remote, `--no-ff`. A glossary is not cosmetic: the mechanism table's ranking cannot be evaluated without it | S6-#22, #23, #24 | passim |
| C8 | **D3/D4 never cited** (phone-home, retheme); **D2 used at 113 before being stated**; **no S-numbering table exists anywhere** for 11 S-IDs; **OQ7 does not exist** although `#7` is cited | S6-#25, S7-…, S5-… | 113, 157, 180, 205, 425, 551 |
| C9 | **Wrong cross-reference at 882** — "(see item 35)" for `addons_path`; item 35 is `release.py`, `addons_path` is item **42** | ALL | 882 |
| C10 | **Structural clean-ups** — `### Target Files to Create/Modify` H3 missing (874–889); Additional Resources/Future Improvements are H3 with no H2 parent (829, 848); two extra `----` breaks; two `text` fences should be `python`/`bash`; CUJ 2 bullet wrap at 235/237 | S7-structural | various |
| C11 | **Voice and edits** — 16 rhetorical "not X; it is Y" in 873 lines; 6 "silent/silently" (2 carry mechanism); "simply" (638), "genuinely" (410, 594) cut; present tense describes a repository that does not exist (22, 26, 297); three unranked superlatives (932, 1006, 1229); "It is not ceremonial" (529); "The consequence, stated rather than glossed" (154) | S7-style, S9-M14 | passim |

---

## Traceability matrix

Every consolidated item traces to its raw findings. `S5`–`S9` = stage report; number = finding ID in that report.

| Consolidated | Severity | Raw findings |
|---|---|---|
| A1 fork justified | 🔴 | S8-B1, S7-B3, S5-M5, S7-M20, S8-Q3 |
| A2 manifests load nothing | 🔴 | S9-B1, S9-B3, S6-B5, S7-#5 |
| A3 Gate 1 cannot pass | 🔴 | S7-B1, S6-B2, S9-B4, S8-M3, S5-M1, S9-M1 |
| A4 config tier | 🔴 | S7-B2, S6-#17, S5-M7, S9-M3 |
| A5 count is wrong metric | 🔴 | S8-M3, S9-B4, S7-B1 |
| A6 four impossible shapes | 🔴 | S9-B5, S9-B2, orchestrator A1/A3/A6/A7/A8 |
| A7 D7 undecided | 🔴 | S7-B4, S6-#4, S9-B6, S5-M10, S7-M10, S8-M4 |
| A8 security unbuilt | 🔴 | S7-M23, S7-M24, S7-M26, S7-M27, S8-M1, S9-M13 |
| A9 LGPL/trademark | 🔴 | S7-M25, S6-#29, S9-M2(author) |
| B1 change manifest | 🟠 | S8-Q1, S8-Q2, S7-M2, S7-M6, S6-B1, S9-M10 |
| B2 four booleans | 🟠 | S8-Q2, S6-#15, S9-M15 |
| B3 Gate 2 unbounded | 🟠 | S7-M7, S6-B1, S5-M1, S9-M10 |
| B4 binary model | 🟠 | S5-M3, S7-M12, S9-M6, S6-#16 |
| B5 cheap-to-sync cost | 🟠 | S8-M1, S7-M26 |
| B6 pricing inversion | 🟠 | S8-M2, S7-M18, S7-M21 |
| B7 framing/voice | 🟠 | S9-M14, S7-M32, S9-(style)1–4 |
| B8 clone duration | 🟠 | S7-M17, S6-#26 |
| B9 measurement chain | 🟠 | S7-M6, S6-#10 |
| B10 alternatives | 🟠 | S7-M18, S7-M19, S7-M21, S7-M22 |
| B11 D1-C mechanism | 🟠 | S5-M9, S9-M12 |
| B12 items 38/39/40 | 🟠 | S9-M1, S9-M2, S6-#6, orchestrator A11 |
| B13 README/allowlist | 🟠 | S9-M10(c), S9-M2(M5) |
| B14 verification | 🟠 | S9-M11, S9-M7, S7-B3 |
| C1 counts | 🟢 | S5, S6, S7, S9 passim |
| C2 title assertion | 🟢 | S9-M5, orchestrator A2 |
| C3 item 32 consumer | 🟢 | S9-M8, orchestrator X3 |
| C4 item 4 records | 🟢 | S9-M4 |
| C5 Registry.remove | 🟢 | S9-M7, orchestrator A9 |
| C6 item 26 tier | 🟢 | S7, S8-Q2, S9-M15 |
| C7 glossary | 🟢 | S6-#22, #23, #24 |
| C8 IDs not defined | 🟢 | S6-#25, S7, S5 |
| C9 cross-ref 882 | 🟢 | S5-M2, S7-…, S9 |
| C10 structure | 🟢 | S7-structural T-01, H-02, T-02, CF-01/02, L-01 |
| C11 voice | 🟢 | S7-style, S9-M14 |

---

## Measured ground truth

Stages 5–8 all ran blind. Stage 9's orchestrator populated a sparse checkout of 44 paths at `9c58cae5` and ran the checks reviewer isolation blocks. Results in `verified_ground_truth.md` and `anchor_verification.md`.

**17 citations confirmed exact**, including the highest-stakes ones:

| Claim | Status |
|---|---|
| `webmanifest.py:48` `web.web_app_name` fallback `'Odoo'` | Exact |
| `webmanifest.py:54/55` both `'#714B67'` | Exact |
| `config.py:50` datadir from `product_name` + `author` | Exact |
| `models.py:5103` `noupdate` skip on update | Exact |
| `ir_module.py:420` `must_install` | Exact |
| `release.py` 15/19/20/32/33/37 | Exact |
| `setup.nsi:87` `DEFAULT_POSTGRESQL_PASSWORD 'openpgpwd'` | Exact, sole instance in tree |
| `database_manager.qweb.html` 4/33/102/144 | All four exact |
| `digest_data.xml:398` Sent by, `:436` Powered by | Both exact |
| `hr_expense/mail_templates.xml:49` `#9E588B` | Exact |
| `order_receipt.xml:140`, `customer_display:84` | Both exact |
| `report_templates.xml:16/50` `title or 'Odoo Report'` | Both exact |
| 35 `logo.png` refs, 2 `logo2.png` refs | Exact |
| `ruff.toml` at repo root | Exists |

**7 contradicted** — the basis of A6, B4, B12, B13.

---

## Repair plan

Ordered by dependency. Steps 1–2 are decisions only you can make; 3–5 are mechanical once 1–2 are settled.

**1. Decide Surface 5.** *(A1)* Does the fork exist? If Surface 5 is out: delete G1–G3, D2, the sync procedure, Alternatives A–F, and re-scope to an addon repository plus a patch file. **This determines whether a third of the document survives.**

**2. Decide D7** and add it to the register. *(A7)* Option A (install list), B (`post_init_hook`), C (`depends`), or the fourth mechanism (`migrations/`). Then unblock items 1, 2, 7, 44.

**3. Introduce the change manifest.** *(B1, B2)* ~80 rows, four record types, ~100 lines of checker. Re-derive the register, the budget, the allowlist and the file table. This removes A3, A5, B2, B3's allowlist half and all of C1 — **not by fixing them but by making them unexpressible.**

**4. Fix the wiring.** *(A2)* `data` and `assets` keys; `__init__.py` files; item 2's real content. Without this, nothing else in the plan has effect.

**5. Correct the measured defects.** *(A6, B4, B12, B13)* `web.layout`; per-template anchors for items 4/11/17/19/24; SVG-vs-binary classification; items 38/39/40 counts and literals.

**6. Name the two missing artefacts.** *(A4, A8, B14)* The deployment checklist and the rendered-output assertion suite — promoted from Future Work to a third gate. This makes the config tier and the silent-failure paths enforceable rather than described.

**7. Clean-up.** *(C1–C11)* Everything left is an edit inside the new shape, not work in its own right.

---

## Decisions required from you

Three questions block the repair. The rest is mechanical.

1. **Is Surface 5 (the Windows installer) in scope?** The Non-Goals say no build pipeline; CUJ 5 requires building one. If out, the fork loses its only justification and the plan becomes a three-page addon repository. *(A1)*

2. **Which D7 option?** A (explicit install list), B (`post_init_hook`), C (all overlays as `depends`), or the `migrations/` fourth mechanism. Three of these produce different file sets. *(A7)*

3. **Should the repair be applied now, or would you rather review the findings first?** The Stage 9 terminal gate. If you pick "Resolve findings with agent", `egm-resolve` applies the approved edits to `docs/designs/castadoo-rebrand-fork.md`.

---

## What is genuinely good

Recorded so the repair does not damage it:

- **Measurement-correction table (73–88)** and the four-purples consequence — the strongest evidence work in the document.
- **Non-Goals (135–168)** — each states its consequence rather than its absence, which is what makes the leakage auditable.
- **Alternatives that carry the measurement which killed them** (565–643, 673–686).
- **D2's merge rationale** and its LGPL-by-product argument.
- **The datadir invariant** and the one-line `release.py` conclusion.
- **Data/configuration table (416–451)** — correct altitude, names where the convenient story is false.
- **The `.po` deferral** and its `msgstr` mitigation.
- **Silent-failure diagnosis (90–103)** — correct, and the reason the gates exist at all.
- **Structural integrity** — heading hierarchy, template order, all five tables well-formed, all six fences balanced, items 1–47 all defined exactly once, G1–G9, CUJ 1–6, OQ 1–6, Alternatives A–O all resolving.
- **Document skeleton and ordering.** Do not restructure.

---

**Report written:** `consolidated_review_report.md`
**Stage reports:** `zoom_out_report.md`, `comprehension_report.md`, `critic_report.md`, `intermediate_zoom_out_report.md`, `implementation_readiness_report.md`
**Measured ground truth:** `verified_ground_truth.md`, `anchor_verification.md`
