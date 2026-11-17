# Stage 5 — Initial Zoom Out Review

**Target:** `docs/designs/castadoo-rebrand-fork.md` (1,449 lines)
**Standard:** `resources/document_standards/zoom-out-standard.md`
**Reviewers:** `egm-zoom-out`, `egm-inventive-catalyst`
**Mode:** REVIEW, full file
**Date:** 2026-11-17

---

## Verification limits

The Odoo 17.0 source tree is not browsable to either reviewer (read-only personas, no shell, no grep). Every `file:line` citation against tip `9c58cae5` — `webmanifest.py:48`, `config.py:50/78`, `ir_module.py:420-422`, `setup.nsi` counts, `models.py:5103` — is **unverified** in this stage. Findings below lean on a citation only where the argument structurally depends on the number being right.

Stage 9 is where path and line verification belongs (`egm-codebase-details` + `egm-implementation-readiness`).

---

## Synthesis note

Two reviewers ran independently. They converged on three points from different directions:

- **The binary conflict claim is wrong in the same way, twice.** `egm-inventive-catalyst` found that git does not merge binaries, so "conflict surface: none" understates the cost of 16 replacements. `egm-zoom-out` found the matching error in the rollback story: replaced binaries cannot be restored by uninstalling, yet the design lists only 4 irreversible sites. Same 16 files, two different sections both wrong in the same direction.
- **The CI gates are the wrong mechanism for the job they are given.** `egm-zoom-out` measured it as unbounded allowlist work. `egm-inventive-catalyst` identified that the document's own central methodological finding ("a grep cannot tell a brand string from an identifier") argues against its own Gate 2, and that the correct mechanism is already written in the document — as *Future Work*.
- **The two-tier addon split carries more machinery than it earns.** `egm-zoom-out` measured the dependency-drag justification as an estimate in a document that rejects estimates, and the example as stale (`sale`/`account`/`crm` are not in the register). `egm-inventive-catalyst` accepted the split as genuinely required by Odoo's dependency-chain install, and attacked only the activation mechanism under it. **These two disagree**, and the disagreement is recorded rather than resolved below.

---

## BLOCKER

### B1. The two-tier, nine-addon architecture is the largest piece of machinery in the design, and its justification is an unmeasured number plus a stale example

*Scope:* Addon architecture (344–414), D7 table (402–414), item 7 (968–978), items 8–25 (987–1147), register Email row (line 323).
*Reviewer:* `egm-zoom-out`.

The split exists to avoid one thing: `depends` dragging business modules in. That drag is asserted as "roughly 15–25 business modules" (355, 667) — an estimate, in a document whose method chapter (82–88) argues budgets must be derived from measurement.

The example is stale. It cites `sale`, `account`, `crm` (353–355, 663–668), and the register touches **none of them**. The real dependency set is `mail`, `auth_signup`, `portal`, `im_livechat`, `hr_expense`, `digest`, `website_slides`, `point_of_sale`.

What the split actually buys: of 23 additive overrides, 2 are PDF titles, 7 are web-shell records, 1 is the user-menu patch — all of those need only `web`. Everything the eight overlays carry is **eight single-footer edits**, in modules many deployments never install. And per D7, `auto_install` does not fire on existing databases anyway, so activation needs a hook or an install list regardless. Once activation is manual, the eight-way split buys only module-set granularity — granularity the design cannot size, because deployment shape is Open Question 3 and remains unanswered.

**Proposed simplification:** one base addon (`web` only) plus **at most one** "extra surfaces" addon. Removes item 7, the D7 menu, items 10–25, and 17 of 54 files, with the same customer-visible result.

**Contested by `egm-inventive-catalyst`**, which lists the two-tier split under "no false compromise detected": "Odoo installs dependency chains; the split is genuinely required. Only the *activation* mechanism under it was compromised." The disagreement is on whether eight overlays are required or one is. **This needs an author decision, not a reviewer consensus.**

---

### B2. The default branch is set to the unbranded mirror, which reproduces the harm it claims to fix

*Scope:* Repository topology (321–324), Goal G2 (110–111), sync step 3 (520, 529–531), item 46 final bullet (1363).
*Reviewer:* `egm-zoom-out`.

The stated harm: "a fork whose default is `20.0` hands an unqualified clone unbranded Odoo 20.0, which is the worst possible first impression." Setting the default to `17.0` produces exactly that at the right series — anyone cloning without `-b` gets pristine, fully-Odoo 17.0.

The default should be `castadoo/17.0`. `17.0` is a maintenance branch nobody has a reason to clone.

This also weakens the mirror branch's case. Its only consumer is one assertion — `git rev-parse 17.0 == upstream/17.0` — while Gate 1 already diffs against `upstream/17.0` directly (496), never against the local branch. A single-branch model merging `upstream/17.0` into `castadoo/17.0` satisfies G2's intent via `git merge-base --is-ancestor`, and deletes a branch, a goal, a sync step, a default-branch trap, and a `--ff-only` failure mode from the runbook.

---

## MAJOR

### M1. Gate 2 as specified is unbounded work hidden in a one-line CI item

*Scope:* Two gates (486–513), Goal G8 (129–131), item 46 (1351–1364).
*Reviewers:* both.

`egm-zoom-out` on cost: "grep the post-sync tree… fail on any unlisted hit" means allowlisting the 1,343 non-translation hits across 591 files the design itself catalogues — plus every hit upstream adds later. The register supplies allowlist entries only for the six D1-C files. That work lands outside the "≈17 h" estimate entirely.

`egm-inventive-catalyst` on correctness: the document's own central finding — "a case-sensitive grep cannot tell a brand string from an identifier" (82–88) — is the argument against its own Gate 2. Measured failure in both directions is already in the document: false negatives (the `Sent by` footer a `Powered by` grep missed; the four split-line sites; every runtime-assembled string, which the document concedes) and false positives (1,343 internal identifiers, with the document predicting its own allowlist "fills with noise and gets disabled").

The correct mechanism is already written down in the document — as **Future Work** (`Extend Gate 2 from grep patterns to rendered output assertions`). The design ships the weak mechanism as enforcement and defers the correct one.

**Proposed:** invert the assertion target from source text to rendered output, reusing the assertions the Verification Plan already specifies (`GET /web/login`, `/web/manifest.webmanifest`, rendered email, PDF extracted text, offline computed style). Keep grep as a fast low-precision pre-check.

**Secondary liability, stated plainly:** a rendered gate needs a live Odoo instance in CI — Postgres, test DB, `-i` of nine addons, a headless browser for Owl/POS. An order of magnitude more infrastructure than grep, minutes not seconds. The honest shape is two tiers, not a swap.

---

### M2. The scope has three competing sources of truth, keyed on data that expires on the first sync

*Scope:* item 45 (1344–1349), register per-line tables, Detailed Implementation Plan (874–1443).
*Reviewer:* `egm-zoom-out`.

The register keys every entry on an upstream **line number** ("Line numbers are from the 17.0 tip", 877). The overrides themselves key on template XML ID plus an xpath anchor — the durable handle. After one point release the register's line numbers are wrong while the overrides still work, so Gate 1's "every changed path present in change_register" passes against a document that no longer describes the code.

Divergence is already visible, in a document that has not yet been synced once:

| Location | Claims | Actual |
|---|---|---|
| 881 | "one `addons_path` entry in `odoo.conf` (see item 35)" | item 35 is `release.py`; `addons_path` is item 42 |
| 811 | "22 of the items are new files or replaced binaries" | 23 everywhere else |
| 1332 | "`#875A7B` references in README are replaced by items 27 and 9" | item 9 is the mail footer |
| register 49 | "8 register items" over S1.01–S1.09 | nine |
| G4 (115–118) | "six named surfaces" | then lists eight |

**Proposed:** register keys on path + template XML ID + selector, never upstream line numbers. Design holds mechanism taxonomy and decisions. Nothing enumerates lines twice.

---

### M3. The rollback story is wrong for the binaries, and it is the argument used to justify the mechanism split

*Scope:* Rollout and rollback (809–825) vs. disposition table (332–337).
*Reviewers:* both.

Line 811 claims 22 items "are new files or replaced binaries" and that uninstalling the addon restores stock behaviour "without touching upstream files." Replaced binaries **are** upstream files; uninstalling an addon cannot restore a blob overwritten at `addons/web/static/img/favicon.ico`.

Lines 815–817 then list "the 4 in-place edit sites" as irreversible — omitting the 16 binaries. The non-reversible set is **20 files, not 4**.

`egm-inventive-catalyst` supplies the mechanism error underneath: "Conflict surface: none — git sees a new blob, not a hunk" (334) is false. Git does not merge binaries. Both sides modifying the same binary path is a conflict, resolved by picking a side.

**Proposed:** a `.gitattributes` merge driver (`merge=ours`, path-scoped to the 16 binary paths) makes the table true. Without it the ranking understates binary cost and the register's "0 conflict" claim is inaccurate.

---

### M4. Ten-plus items sit outside the six named surfaces the scope is defined by

*Scope:* G4 (115–118), item 6 (950–966), item 30 (1187–1190), item 32 (1197–1200), item 36 (1231–1241), item 41 (1304–1311).
*Reviewer:* `egm-zoom-out`.

- **Item 6, user-menu JS** — removes "My Odoo.com account" and repoints documentation. A functional change (removing a menu entry), not a branding string. No named surface covers the user menu. It is also the only item adding executable logic.
- **Item 30, website-configurator logos** and **item 32, `website_links` favicon** — website configurator and link previews are not among the six.
- **Item 36, database manager** — reachable only when no database is selected, and the NFR recommends `list_db = False` for exactly these deployments (781–785). Under the recommended posture this is four in-place edits with recurring conflict surface on a file nobody will see.
- **Item 41, phone-home** — a privacy default, not branding.

**Proposed:** either G4 grows to name these surfaces (and the register grows a surface 7), or they are deferred. As written, the diff budget has no principled boundary and the "fixed scope" claim in the Overview (34) is not the scope being implemented.

---

### M5. CUJ 5 and the verification plan require building the Windows installer, which the Non-Goals forbid

*Scope:* CUJ 5 (268–279), Non-Goals (165–166), E2E plan (1404–1406).
*Reviewer:* `egm-zoom-out`.

"Build the installer, install on a clean Windows VM, check the uninstall registry key" is a build-and-test workflow. Non-Goals: "No installer build pipeline, no auto-update, no release artefacts. This plan produces a source tree."

This is not cosmetic. The registry-key migration (item 38, 1262–1269) is one-shot and non-reversible, and it can only be validated by actually building. Either the non-goal is honest and CUJ 5 reduces to a static review of `setup.nsi`, or the deliverable includes a build. The decision moves the effort estimate materially.

---

### M6. The Detailed Implementation Plan duplicates the register, and the duplication is already failing

*Scope:* 874–1443 vs. `change_register.md` in full.
*Reviewer:* `egm-zoom-out`.

575 lines restate the register per file, per line, per string. The two have already diverged (M2). Keeping both means every scope edit is a two-file edit with no mechanism to detect disagreement — silent, in a design whose thesis is that silent drift is the enemy.

---

### M7. Configuration — the cheapest mechanism — is the only one outside version control, and it fails silently

*Scope:* Data and configuration model (416–451), CUJ 4 (254–266), disposition rank 1 (334).
*Reviewer:* `egm-zoom-out`.

Rank 1 is "zero code, zero conflict" and covers PWA name, email colours, favicon. All five values are deployment obligations. Forget `web.web_app_name` and every CUJ 4 assertion fails while the tree is perfectly clean. Neither gate checks post-render config.

Two of the five are shippable as module data: `web.web_app_name` as an `ir.config_parameter` record with `noupdate`, favicon as a `website.favicon` default. Company name and logo genuinely belong to deployment — that part is correct.

---

### M8. The backend-stays-purple rejection rests on a wrong reading of `!default`

*Scope:* Non-Goals (142–148), Alternative J (679–693), Future Improvements ¶3, register D4.
*Reviewer:* `egm-inventive-catalyst`.

The stated reason: "`!default` resolves before any later file in the bundle, so the change requires editing a compiled-variable file that changes between releases."

`!default` at line 73 means *that line* yields to an earlier definition. It does not block a **plain assignment in a later-loaded file**. Odoo orders its variable layer into asset bundles precisely so a dependent module's SCSS is concatenated after `primary_variables.scss` and before the derived-variable file. A new file in the branding module, declared in the manifest's asset-bundle key, is a **new file with no conflict surface** — mechanism 2, not 4.

The enumeration "either an upstream change… or a permanent edit" omits this third option.

**Secondary liabilities:** bundle key names and intra-bundle order are series-specific (low-churn dependency, not zero — a rename surfaces at asset-compile time, quieter than a conflict). Existing databases need an asset recompile or they render the old palette. And the document's own four-purple finding means a retheme is not one variable: `#71639e`, `#875A7B`, `#9E588B` and `hw_posbox_homepage/override.css` all survive and become support questions.

The decision *not* to retheme may still be correct — but on "outside the six named surfaces" grounds, which **contradicts G4 listing the backend shell as in-scope** (B1's sibling problem), not on "permanent conflict site" grounds.

---

### M9. D1-C's three-way framing omits a render-time decorator

*Scope:* Non-Goals (148–157), Alternative K (679–694), Alternative N (727–741), register §4b.
*Reviewer:* `egm-inventive-catalyst`.

The choice is framed as re-declare (`noupdate`), mutate `body_html` (rollback hazard), or accept the footer. Both touch state.

Neither is required to render the footer, because the footer is produced by a render step the fork can extend. A module can subclass `mail.template` and post-process the *rendered* body (call `super()`, transform the footer region), keyed to the seven XML IDs. New file, no upstream edit, no record re-declaration, no data mutation, undone by uninstalling. Upstream's body improvements still reach every install because the record is never shadowed.

**Secondary liabilities:** an HTML transform over email markup is brittle the same way xpath anchors are — an upstream footer redesign produces a no-op transform that *silently* keeps Odoo, the exact dangerous class the document identifies. It needs its own rendered-email assertion, not a grep. It runs on every render (cheap, real). And markup-transform code is harder to review than a diff line, which partially vindicates the document's "harder to audit" instinct.

---

### M10. D7 — a fourth mechanism exists; option B's weakness is dischargeable

*Scope:* Addon architecture §The trap, D7 (402–414), item 7 (968–978).
*Reviewer:* `egm-inventive-catalyst`.

"That's the only one" (option B) is false. B's residual failure — "a later database gains `mail` after `castadoo_branding` is installed, the hook does not re-run" — is on the highest-traffic surface, and is discharged by *a human convention*.

**Fourth mechanism:** a *self-service reconciliation pass*. A module migration script (`migrations/<version>/post-*.py`) runs on every `-u castadoo_branding`, which is exactly the command the fork's own sync/upgrade path already mandates. Bumping manifest `version` at each sync makes convergence a by-product — the same trick D2 uses to discharge the LGPL dating obligation. Optionally an `ir.cron` reconciliation for databases that gain modules outside the sync cycle.

**Secondary liabilities:** automated module installation is privileged and heavy — it rewrites `ir_module_module` state, can race a concurrent worker on the same registry, and turns "a module appeared" into an unasked-for deploy event. Needs idempotence, an explicit log line, a kill switch. O(databases) per sync on a multi-tenant host.

**Process gap:** the register's decision sheet contains **D1–D6 and no D7 row**, while the design calls D7 "an author decision". The register is the artefact Gate 1 reads; an author decision that lives only in the design is not in the versioned record.

---

### M11. The conflict-surface elimination stops one step short, and the stop is a false dichotomy

*Scope:* Disposition rule (326–343), Tier 4 (items 35–39), Alternatives F and G, NFR Rollout.
*Reviewer:* `egm-inventive-catalyst`.

"Attempting zero would mean either leaving the installer unbranded or building an installer-side override system that does not exist — an installer addon is a contradiction."

An *installer addon* is indeed a contradiction. An **installer-side include is not an addon**. NSIS is a compile-time macro processor with `!include` and `!define /redef`. The `!define`-carried fraction of the 87 strings (`PRODUCT_NAME`, `PUBLISHER`, `BrandingText`, contact and registry identities) can move to a fork-owned `.nsh`, collapsing to **one** conflict line; only inline caption literals remain in-place, and those rarely change upstream.

Separately, a **declarative transform table plus a verifier** (`apply-rebrand --check`) would re-derive the in-place edits after each merge and report non-zero when the tree diverges from `upstream + transforms`. This is *not* Alternative F: the merged tree stays checked out and runnable, no history model changes, no replay for provenance. It is a verifier and repair tool, one small script, and the same artefact strengthens Gate 1 (M1) — one mechanism paying twice.

**Secondary liabilities:** the transform table duplicates knowledge with the register unless the register is *generated* from it (mandatory, not optional). A git merge driver variant is worse — silent auto-resolution masks genuine upstream restructuring, failing as a wrong tree rather than a loud conflict; only acceptable with `--check` in front. Residue is real: caption literals, the French block, `database_manager.qweb.html` still land in-place. Controller substitution for `webmanifest.py` would trade a loud conflict for a quiet runtime failure on upstream signature change — **not** recommended, and the document is right to keep those lines in-place.

---

## NIT

- **No project root documentation exists.** `README.md` and `context.md` are absent; only `concepts_brief.md`, `design_draft.md`, `change_register.md` and this design. The standard's project-alignment check cannot be satisfied against root docs. Acceptable for a founding document, but worth one sentence.
- **No glossary.** QWeb, xpath inheritance, Owl `t-inherit`, `auto_install`, `noupdate`, `ir.config_parameter`, `addons_path` are all load-bearing and all undefined. A reader without Odoo exposure cannot evaluate the mechanism table.
- **"≈17 h" excludes asset design, the register, the CI gates and deployment** — the four most expensive components — yet that figure is quoted in the decision sheet as the basis for D1-C. State the excluded total or drop the headline number.
- **G5's "≥ 23 items additive" is a lower bound**, which rewards converting edits into inheritance rather than capping cost. State it as a fact, not a goal.
- **D1-C consequence lists name six of seven excluded records** (154–156, register 146–152). `validation_email` is missing from both prose lists while present in the table.
- **No scan of the module ecosystem.** The reuse analysis covers Odoo's own mechanisms well but never asks whether an existing community branding addon already covers the six surfaces.
- **"The implementer needs to make no further decisions"** (878–879) is contradicted by D7 being open and item 36's unresolved privacy-link target (1239–1241). Soften the claim.
- **Backend retheme deserves one experiment**, not a redesign: an additive asset-bundle override is cheaper than a permanent mismatch between a navy favicon and a purple UI. Connected to M8.

---

## D1-C / reuse note from `egm-zoom-out`

The design's reuse analysis covers Odoo's own mechanisms well — `web.web_app_name`, `website.favicon`, `email_secondary_color`, `company.logo` are all correctly identified as the cheap path. That reconnaissance is why the mechanism table can rank by cost at all. It should not be trimmed.

---

## Meets the standard

- **Context sufficiency (9–52).** Objective, constraint, deliverable shape, and an operational definition of "cheap to sync" all stated before any solution.
- **Root problem framing ("Why this is hard", "What the measurement changed").** The tension is stated as a real trade-off and the budget is derived from rendering surfaces rather than substring counts. Strongest part of the document.
- **Non-Goals (135–168).** Each exclusion states its consequence rather than its absence, which is what makes the leakage auditable.
- **Alternatives Considered (556–765).** Every rejected option carries the measurement that killed it.
- **Data and configuration model table (416–445).** Correct altitude: what is data, what is code, where the convenient story is false.
- **`release.py` frozen at one line.** Genuine invariant — `config.py:50` → `appdirs.user_data_dir()` makes the rename a data-visibility change, not a branding one. No pattern dissolves it.
- **Sync model (D2, `--no-ff`).** The trade (non-linear graph vs. SHA stability and LGPL provenance) is real and correctly decided.
- **Asset approach** (outline wordmark, derive square icons from mark, keep filenames). Reasoning sound; rasteriser/outlining separation correct.
- **`.po` and help-text leakage accepted.** `msgid`-rename cost and per-string trademark judgement are real; the `msgstr`-only overlay is the right deferral.

---

## Areas with no false compromise

Recorded so they are not re-litigated in Stage 8:

- `release.py` field freezing — genuine invariant.
- Sync model choice (D2) — correctly decided; the transform-table proposal deliberately does not reopen it.
- Two-tier addon split *as a shape* — `egm-inventive-catalyst` accepts it as required by dependency-chain install; `egm-zoom-out` disputes its size. **Disagreement recorded, not resolved.**
- Asset approach.
- `.po` / help-text leakage.

---

## Cross-cutting observation

Findings M1, M2, M3, M11 are one pattern viewed from four angles: **declare the intent as data, assert on the effect, and let a small tool re-derive the artefacts.**

A single executable transform table plus a rendered-output assertion corpus would (a) remove most recurring conflict *labour* without changing the branch model, (b) replace "≤ 94 lines" and "grep found nothing" with "the tree equals upstream plus declared intent" and "the six surfaces render without Odoo", and (c) make the register the single source of truth rather than a second copy of the transform table.

The document's own structure points at this. It stops one step short because each area was evaluated locally against a binary choice, rather than against the shared mechanism.
