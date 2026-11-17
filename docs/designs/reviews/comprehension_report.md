# Stage 6 — Comprehension Test

**Target:** `docs/designs/castadoo-rebrand-fork.md` (1,449 lines)
**FeatureRange:** 1–873 · **DetailedRange:** 874–1,449
**Reviewer:** `egm-comprehension` (naive reader, zero institutional knowledge)
**Context supplied:** none. No `concepts_brief.md`, no `change_register.md`, no history. The document stood alone.
**Standard:** none applied, per skill. `re-implementation-standard.md` explicitly not applied.
**Date:** 2026-11-17

---

## What this proposes

This document specifies a **source tree, not a product build**: a GitHub fork `castaso/CASTADOO` of `odoo/odoo` 17.0 in which branch `17.0` stays byte-identical to upstream (proved by `git rev-parse`) and a single long-lived branch `castadoo/17.0` carries every CASTADOO change, merging upstream point releases with `--no-ff`. Branding reaches customer-visible output through four ranked mechanisms — configuration/data, QWeb view inheritance in new files, binary replacement at existing paths, and in-place edits of upstream files — with in-place edits treated as the scarce, budgeted resource (37 files / 94 lines) inside a 47-item plan enumerated against upstream SHA `9c58cae5`. The rebrand ships as nine addons (one `castadoo_branding` base depending only on `web`, plus eight per-module overlays activated by `auto_install`), two CI gates (a diff-budget/register check and a brand lint), and a written sync procedure. Several decisions (D1-C, D2, D5, D6, D7) and six open questions are carried rather than closed, and the document is explicit that LGPL-3 forbids removing attribution while permitting the product rename.

## How the existing system works, per this document

Odoo 17.0 renders brand text from three kinds of source: ordinary data (`res.company.name`, `.logo`, `.email_secondary_color`, plus the `ir.config_parameter` key `web.web_app_name`), QWeb templates that a new addon can override with an inherited view anchored on an existing XML ID, and literal strings compiled into upstream files such as `setup/win32/setup.nsi`, `webmanifest.py`, `database_manager.qweb.html` and `release.py`. `release.product_name` is not a display string — it computes the default datadir — and `release.author` also appears in the Windows datadir path, so both are frozen. An addon's `depends` list is installed transitively, and an `auto_install` list only fires when a named module is *newly entering installation*, not when it is already installed. Icons and logos are static files served from fixed paths, and the PWA name comes from a system parameter whose stock fallback is `Odoo`.

**Paraphrase failure, reported as a Blocker rather than skipped (finding 3):** the surface taxonomy (`Goal G4`, the `S1`–`S6` / `S4.01`–`S4.20` identifiers) could not be reconstructed. The document never states what the six surfaces are or builds the S-numbering anywhere.

---

## Findings

### 🔴 BLOCKER

**1. The design's checkable content lives in two files the document does not contain.**
*Scope:* Overview (34–37), Additional Resources (829–836), gates (495–505, 1358–1362), item 45 (1344).

`change_register.md` ("every one of those files is enumerated with a line number"; "37 files, 94 edit lines, 23 additive items") and `concepts_brief.md` ("Every measurement in this design traces back to it") are cited as the source of truth for every number.

Gate 2's "enumerated patterns" are never listed anywhere — not the grep patterns, not the allowlist entries, not the allowlist format. A reader given this document alone cannot evaluate the primary safety mechanism, cannot reproduce any of 37/94/23, and cannot tell what the gates assert.

This is not a cross-reference nit. The document's central falsifiable claims are entirely external to it, in a document whose thesis is that claims must be falsifiable.

---

**2. The budget and the gate measure different quantities, so Gate 1 fails by construction.**
*Scope:* G5 (119–122), gates (495–499), item 46 (1355–1357), footnote (1413–1443).

G5 and item 46 assert `git diff --stat upstream/17.0...HEAD` yields ≤ 37 files. The footnote says the register's 37 "counts upstream paths that differ after the overlay" and that the plan's own count is 54 files (49 must exist), "including the addon tree".

A `git diff --stat` between fork and upstream counts *every* differing path — including items 1–25. That is the plan's own 54, not 37.

Applying the document's own definition ("upstream paths that differ") to its own enumeration: 16 overwritten binaries (26–33) + 6 in-place edits (35–40) + 1 conditional (41) = **23**, not 37. Fourteen paths are never identified.

An implementer following item 46 literally ships a CI gate that can never pass.

---

**3. "Six named surfaces" is followed by eight entries, and the surface taxonomy is never built.**
*Scope:* G4 (115–118), disposition table (332–337), data model (425–440), item 13 (1037–1040).

G4 says "Branding on six named surfaces" then lists **eight** comma-separated entries: backend shell and browser tab, login, PDF metadata, email, installer, PWA manifest, offline page, favicon and app icons. They are never collapsed to six or numbered.

`S4.01`–`S4.20` are cited 13 times with no definition of `S1`–`S6`. "Surface 4" is inferable only from item 13's aside — which breaks the model: "this is a sidebar in the portal *web* UI, not an email — the register lists it under Surface 4 because the string is identical." Surfaces keyed on string identity rather than screen make any screen-based count wrong.

The table at 430–440 is headed "the ten in-scope email/notification sites" and lists **13** distinct IDs (01–10, 18, 19, 20).

---

**4. D7 says the plan cannot be executed without an answer, then says the plan works under any answer.**
*Scope:* D7 (400–414), items 1/2/7 (891–978), Open Questions (205–207).

"Needs an answer before the Detailed Implementation Plan can be executed" and "is written so that any of the three can be applied to the same file set" cannot both hold.

- Option C (base declares all overlays as `depends`) deletes the reason for items 8–24 entirely and violates item 1's stated hard requirement that `depends` "must contain `web` and nothing else".
- Option A removes item 7 (`hooks.py`) and item 2's `hooks` import.
- Option B adds a `post_init_hook` key to item 1.

The file set differs under every option. The plan is not executable until an undocumented author decision is made.

---

**5. Nothing wires the new JS and Owl files into an asset bundle, and item 2 instructs an import that will fail.**
*Scope:* items 1–2 (891–905), item 6 (950–966), items 22–25 (1116–1148).

Item 1's manifest is specified as `name`, `depends`, `auto_install`, `license`, `author`, `application` — **no `assets` key**. So `castadoo_user_menu.js` (6), `receipt.xml` (23), `customer_display.xml` (24) and `odoo_logo.{js,xml}` (25) are never served.

Item 2 says `__init__.py` "Imports `models` (for `res_company` defaults if used)" — but no item anywhere creates a `models/` package. The literal instruction produces an `ImportError`.

These are the exact surfaces the document calls out as failing *silently*: "Owl inheritance fails silently if the parent name is wrong — it does not raise" (item 23). The plan hands the implementer dead files and calls it complete.

---

### 🟠 MAJOR

**6. "87" is used as three different units.**
*Scope:* "Why this is hard" (60), Alternative F (638), item 38 (1255).

The installer is "87 such lines" (merge-conflict lines), then "87 lines of `setup.nsi`", then "87 strings". The French translation block is "part of the 87" (1282–1283), so 87 includes translated duplicates of the same strings. It cannot be a line count, a string count, and a conflict-line count at once.

---

**7. The rollback story is false for two-thirds of the items it cites.**
*Scope:* NFR Rollout and rollback (811–814).

"Removing the branding addon restores stock behaviour for those [22/23 items] without touching upstream files." Replaced binaries (items 26–33, 16 files overwritten at upstream paths) are **not** restored by uninstalling an addon — they are upstream blobs in the tree. Only the ~25 additive addon files are. The count cited (22) also contradicts G5/Overview/Additional Resources (23).

---

**8. The NFR section's "no runtime overhead" omits the fourth mechanism.**
*Scope:* NFR "No runtime overhead" (805).

"Every in-scope mechanism is either configuration, a new file, or a replaced binary." That omits in-place edit — the 87-string `setup.nsi` edit and the document's own declared "scarce resource". A reader of the NFR alone concludes no upstream file is edited.

---

**9. The D1-C exclusion set is enumerated three times in three different sizes.**
*Scope:* Non-Goals (153–156), Alternative K (700–712), Alternative N (741–752), item 46 (1360–1362).

- Non-Goals: six records (portal-invitation, portal-welcome, account-created, badge, lunch-supplier, lead-forward).
- Alternative K: seven (adds "validation").
- Alternative N: "seven".
- Item 46: "the **six** excluded data files", naming `auth_signup`, `portal`, `gamification`, `lunch`, `website_crm_partner_assign`, `website_profile`.

No record→module mapping is given. A reader cannot tell whether "validation" belongs to `website_profile` or is missing from the allowlist, and cannot tell whether the allowlist is complete.

---

**10. The headline measurement arithmetic does not reconcile, and mixes files with lines.**
*Scope:* "What the measurement changed" (82–88), Non-Goals (146–148), Alternative M (728–739).

"26,560 **files** contain `Odoo`; 5,496 of the matching **lines** are the notice; 18,920 are translation files. Of the remaining 1,343 hits…"

- Treating 18,920 as lines: 26,560 − 5,496 − 18,920 = 2,144 ≠ 1,343.
- Treating 18,920 as files: 7,640 ≠ 1,343.

Then Non-Goals treats 18,920 as a **file** count ("the 18,920 `.po`/`.pot` files") while Alternative M says "the **3,410** `.po` files containing `Odoo` in a `msgid`". Two different file counts for the same set, both presented as measured.

---

**11. `#9E588B` is the fourth purple and the fifth purple in the same document.**
*Scope:* line 80, line 442, item 17 (1069).

"Four distinct purples … `#9E588B`" / "The **fifth** purple — `#9E588B`" / "a **fourth** purple, distinct from `#714B67`, `#71639e` and `#875A7B`". Only four colours are ever named, so "fifth" is unsupported.

---

**12. The binary count is 11 and 16 in different sections.**
*Scope:* NFR Asset regeneration (800), Future Improvements (864), footnote (1425).

"Regenerating the **11** committed binaries" vs "The **16** committed binaries" vs the footnote's own row ("Upstream binaries overwritten at existing paths | 26–33 | 8 | 16"), which reconciles to 16. 11 is not derivable from anything.

---

**13. Optionality is stated three incompatible ways.**
*Scope:* item 22 (1120–1121), item 25 (1145–1147), footnote (1434).

- Item 22: the POS overlay "is **optional** per the register's 35-required / 2-optional split; it is **the second** optional item".
- Item 25: its two files "are the **two** optional files in the register's count".
- Footnote: "3 are optional (items 25 and 47)".

Three optional things, a "2-optional" split, and a footnote that excludes item 22. The verification plan also requires "all 9 addons", which fails if the optional overlay is skipped.

---

**14. "Additive" is never defined as a countable unit, and G5's method cannot measure it.**
*Scope:* item 4 (926–937), item 34 (1209–1214), line 34, G5 (120).

Count is 23 in Overview/G5/Additional Resources, 22 at line 811. Nothing defines whether an "additive item" is an addon, a file, an inherited record, or an xpath — item 4 alone contains four inherited records in one file; item 26 alone contains six binaries.

G5 says it is "Measured as `git diff --stat upstream/17.0...HEAD`", a command that reports insert/delete line counts per file, not the additivity of items.

---

**15. "Tier" means two incompatible things, and two items are filed under the wrong one.**
*Scope:* 28–32, 332–337, 344–374, 889, 980, 1165, 1216, 1324.

The Technical Plan defines **two** addon tiers (base + per-module overlays, "nine addons in total"). The Detailed Plan uses **five** tiers that mix addons, binaries, source edits and docs.

- Item 26 sits under "Tier 1 — base addon `castadoo_branding`" while being an overwrite of six upstream binary files — the definition of Tier 3. The footnote groups 26–33 together, contradicting the heading.
- Item 42 sits under "Tier 4 — in-place edits of upstream files. The only files with a recurring conflict surface" while its own text says it is "**Not** modified in the repo".

A reader counting tiers gets 2 or 5; a reader sorting item 26 gets Tier 1 or Tier 3.

---

**16. Binary conflict behaviour is stated backwards.**
*Scope:* Tier 3 preamble (1167–1169).

"git records a changed binary, not a hunk, so an upstream edit to the same file is a whole-file replacement rather than a merge conflict" and "carry **no** conflict surface".

Git *does* conflict when both sides modify the same binary — it reports `CONFLICT (content)` with no hunk resolution, which is strictly worse than a text merge because there is nothing to merge. This matters: upstream Odoo does periodically touch its own logo assets, and 16 paths are exposed.

---

**17. No deliverable sets four of the five settings that produce the branded surfaces.**
*Scope:* Data and configuration model (421–451), item 42 (1313–1322), G4 (115), CUJ 4 (256).

`res.company.name`, `.logo`, `.email_secondary_color`, `website.favicon` and `web.web_app_name` are all "Set by: deployment". **No item produces them.** Item 42 covers only the `addons_path` line.

The consequence is stated ("partly a deployment step") but the mechanism is not. `web.web_app_name` — whose stock fallback is `Odoo` — is a named surface and a CUJ-4 assertion, and its verification (`GET /web/manifest.webmanifest` returns `name`) can only pass after an undocumented manual step.

---

**18. "The implementer needs to make no further decisions" is contradicted six times in the same section.**
*Scope:* 876–879 vs items 4, 6, 25, 36, D7, and item 6's API guess.

The plan hands back undecided choices at:

- Item 4: "Two options, and the implementer must pick one deliberately."
- Item 6: "Either repoint … or remove the item", and `registry.category("user_menuitems").remove?` — written with a literal question mark, indicating the author does not know whether the API exists.
- Item 25: "can be skipped".
- Item 36: "the link target needs a decision at implementation time".
- D7: three options.
- Item 46's allowlist contents: unspecified.

---

**19. G2's enforcement is attached to the branch that cannot break it, and the acquisition phase has no deliverables.**
*Scope:* G2 (110–111), item 46 (1351–1364), topology (321–324), Verification Plan (1376–1411).

The workflow runs "on push and on PR into `castadoo/17.0`" and asserts `git rev-parse 17.0 == git rev-parse upstream/17.0` — but the branch that can break the mirror is `17.0`, and a bad push to `17.0` triggers nothing. The gate also presumes an `upstream` remote in the CI checkout, which is never specified.

Separately, the default-branch check is asserted to be "verified with `git ls-remote --symref origin HEAD`, not assumed", but it appears nowhere in the Verification Plan. No item covers fork creation, the rename-then-fork sequence of Alternative D, or remote configuration — the entire acquisition phase has no numbered deliverable.

---

**20. The budget is numerically impossible under its own measurement command.**
*Scope:* G5 (119–122), Overview (34–37), item 46 (1355–1357).

G5 defines the metric as `git diff --stat upstream/17.0...HEAD`, which counts **insertions in new files**. Items 1–25 are 25 new addon files — manifests plus view XML plus a hook — easily 400+ added lines by themselves. A budget of "≤ 94 editor lines" measured that way cannot hold.

Same for file count: 25 new + 16 overwritten binaries + 6 edits = **47 paths**, not 37.

Either the metric excludes additive files (in which case `git diff --stat` is the wrong command and no substitute is given) or the 94 figure is wrong. Item 46 as written fails on the first commit.

---

**21. "≥ 23" makes the constraint non-falsifiable, and "additive override" is undefined as a unit.**
*Scope:* G5 (120), line 34, line 835, line 656.

"of which **≥ 23** items are additive" versus "23 additive overrides" (34), "23 additive items" (835), "23 items never touch an upstream file" (656).

`≥` passes with 23 or 400. A lower bound rewards converting edits into inheritance rather than capping cost — the opposite of a budget.

---

**22. The document's second-most-used mechanism is never defined.**
*Scope:* 28–32, disposition table (332–337), items 3, 5, 9–21, 23–24.

**QWeb** appears at line 29 and ~30 more times, never explained as Odoo's templating engine. **View inheritance** is never explained (an override declares `inherit_id` plus an `<xpath>` locator into the parent DOM; the locator fails if upstream renames the anchor). **Owl** appears at 76, 952, 1118, 1125, never named as the frontend component framework. **`t-inherit`** (item 23) is never explained as Owl's inheritance mechanism with the different failure mode the document relies on.

The document's central risk argument — xpath fails loudly, Owl fails silently — cannot be evaluated by anyone who does not already know both mechanisms.

---

**23. The git vocabulary the repository model rests on is undefined.**
*Scope:* G1 (107–109), G6 (123–125), Alternative C (591–603), sync procedure (517–527), D2 (113).

**Blobless clone**, **promisor remote**, and "the blobs live only on the promisor remote … the saving is an illusion once the destination is not the promisor" (Alternative C) are the entire justification for G1's fork-first ordering. None of the three is defined.

**Fast-forward** / `--ff-only` / `--no-ff` are used as self-explanatory (302, 311, 519, 521). The reason `--no-ff` is *required* — it preserves a merge commit carrying the LGPL dating obligation and keeps overlay SHAs stable, which is the whole of D2 — is only inferable by cross-reading Alternative E.

---

**24. Smaller load-bearing terms are undefined.**
*Scope:* 421–427, Alternative N (744–749), item 38 (1271–1272), item 26 (1156), 482–484.

- **`ir.config_parameter`** presented as a normal field on a normal model; never stated to be a global key/value store keyed by string.
- **`noupdate="1"`** never defined beyond a parenthetical, and the consequential inference — that a re-declared `noupdate` record may therefore *not* overwrite the installed body — is never drawn *(see finding 30)*.
- **`nssm`** (item 38) and **NSIS** never expanded.
- **Maskable safe-area inset** (477, item 26) required by the icon pipeline without saying what the safe zone is or what fraction it covers.

---

**25. Five decision IDs carry the plan's most consequential choices and none is defined.**
*Scope:* 33 (`D1-C`), 113 (`D2`), 199 (`D5`), 194 (`D6`), 400 (`D7`), 835 (`decision sheet D1–D6`).

`D1-C` is used at line 33 before any D1 exists. The letter-suffix notation (implying options A/B/C under a decision D1) is never explained, though Alternative N lets a reader guess.

**`D3` and `D4` are never mentioned at all**, yet the register is said to contain a "decision sheet D1–D6" — two decisions with consequences are invisible to a reader.

---

**26. Three sections give three different answers on whether a clone duration may be quoted.**
*Scope:* G6 (123–125), Open Question 4 (190–193), NFR (799).

- G6: clone "stays under 500 MB (measured: 444 MB) with full history, so a maintainer can clone **in minutes rather than hours**."
- Open Question 4: the two bandwidth measurements disagree by ~34×, and "Every duration estimate for the initial clone depends on which is real."
- NFR: "so **no duration is quoted**."

G6 quotes one. A reader cannot tell whether 444 MB and "minutes" rest on 0.25 MB/s (≈30 min for 444 MB) or 8.6 MB/s.

---

**27. "The runbook" is treated as an existing deliverable six times; no item creates it.**
*Scope:* 405, 547, 782, 785, 1320, item 44 (1339–1342).

It is said to carry D7 option A's install list (404), the `list_db`/`admin_passwd` mitigation (785), the `addons_path` line (1320), the initial-clone duration (547), and the `-u castadoo_branding` convention under D7-B (405).

Item 44 (`CONTRIBUTING.md`) is maintainer documentation covering sync and D7, not deployment. The deliverable that would carry the deployment settings flagged in finding 17 is missing from the enumeration.

---

**28. Essentially every number is unverifiable from the document; there is no measurement appendix.**
*Scope:* 34–37, 75–88, 190–193, 584, 638, 647–657, 720, 728, 797–799, 1174, 1180, 1425.

No command, script or method is given for: 40,111 files; 26,560 / 5,496 / 18,920 / 1,343; 3,410 `.po` files; 290 user-visible files; ~1,150 strings; 444 MB; ~17.7 GB; 4.76 GB vs the 2 GB push limit; "34.5 days" for 75 commits; "four other stock manifests"; "roughly 15–25 business modules"; "35 references" to `logo.png` and "2 references" to `logo2.png`; "16 committed binaries" / "11 committed binaries"; "20 sites: 11 / 7 / 2".

The document's thesis is that the budget derives "from measurement rather than preference". A reader cannot reproduce or falsify any measurement, and several contradict each other (findings 10, 12, 14, 21).

---

**29. LGPL-3 obligations are asserted, not tied to any clause.**
*Scope:* G7 (126–128), sync step 6 (523–524), item 40 (1296–1302), 49–52.

G7 calls compliance "**structural, not documentary**" and requires "every modification dated in the merge commit that introduced it" — but a merge commit message *is* documentary evidence, and the mechanism given (step 6: one "CASTADOO modifications staged <date>" line per sync) dates the *sync*, not each modification, which is what G7 claims.

Whether LGPL-3 actually requires per-file change dates, and what "keeping the derivation visible" concretely demands, is never tied to a licence clause. A reader cannot distinguish legal requirement from policy choice, although the document leans on "the licence requires" to justify decisions (e.g. rejecting rebase at 624).

---

**30. The `noupdate` mechanism is asserted in one direction only, which undermines Alternative N's rejection.**
*Scope:* Alternative N (744–749).

N says the seven records are "skipped on every module update including upstream's own (`odoo/models.py:5103`), so the cost is a standing review obligation **rather than the data-loss trap an earlier draft claimed**."

If `noupdate` records are skipped on update, the corollary is that a *re-declaration* in a new module **also would not overwrite the already-installed body on an existing database** — i.e. N would not achieve its stated goal there either. The document neither states nor rules this out, and refers to "an earlier draft" the reader cannot see.

Combined with finding 25 (D1-C undefined), a reader is asked to accept a rejection on a mechanism asserted in only one direction.

---

**31. The digest "zero edits" claim rests on line numbers outside the stated template.**
*Scope:* item 19 (1084–1098).

The entry says `digest.digest_mail_main` "spans lines 270–447", then justifies the colour with "line 14 sets `color_company = …` and line 147 applies it to `.odoo_link_text`". Lines 14 and 147 cannot be inside a template spanning 270–447.

A reader cannot tell whether those two lines are file-level CSS reaching this template, or a differently-numbered template — which is the difference between "set the field, zero edits" and "replace the literal in markup". Same ambiguity at 1091 ("they share one parent template, so one `<xpath>` cannot cover both"): unclear whether the two anchors are in one template or two.

---

## Summary of contradiction types

The naive reader's failures cluster into four kinds, and the clustering matters more than the individual counts:

| Kind | Findings | What it indicates |
|---|---|---|
| **Self-contradicting numbers** | 7, 10, 11, 12, 13, 14, 21, 26 | Numbers were updated in some places and not others across drafting revisions. The Step-6 reconciliation caught three; at least eight more survive. |
| **Undefined load-bearing terms** | 22, 23, 24, 25 | The document assumes Odoo and git fluency it never establishes. A glossary is not cosmetic here — the mechanism table's ranking cannot be evaluated without it. |
| **Taxonomy that does not close** | 3, 9, 15, 6 | Six-vs-eight surfaces, two-vs-five tiers, 87-as-three-units, six-vs-seven-vs-six excluded records. Each is a count that was never recomputed after a revision. |
| **Mechanism under-specified where it matters most** | 1, 2, 4, 5, 17, 19, 27, 30 | The gates, the asset bundle, the configuration settings, the runbook, and the mirror-branch enforcement are all described as working without the specific artefact that makes them work being enumerated. |

Finding 5 (dead JS/Owl files, `ImportError` from item 2) and finding 17 (`web.web_app_name` delivered by nothing) are the two that would produce a silently unbranded deployment — the failure class the document's own thesis exists to prevent.
