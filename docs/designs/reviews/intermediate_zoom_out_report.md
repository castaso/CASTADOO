# Stage 8 — Intermediate Zoom Out Review

**Target:** `docs/designs/castadoo-rebrand-fork.md` (1,449 lines, full file)
**Standard:** `resources/document_standards/zoom-out-standard.md`
**Reviewer:** `egm-zoom-out` (second pass)
**Context supplied:** `concepts_brief.md`, `change_register.md`, `zoom_out_report.md` (Stage 5), `comprehension_report.md` (Stage 6), `critic_report.md` (Stage 7)
**Date:** 2026-11-17

---

## Verification limits

Unchanged from Stages 5–7: the Odoo tree is not browsable, no shell, no grep. Every `file:line` against `9c58cae5` is unverified. The reviewer noted that target line numbers are unchanged from Stage 5's citations, so **all Stage 5 findings stand as recorded — no finding has been repaired in the intervening stages**, including the `!default` claim, which still reads identically at 157–161 and 691–695.

---

## Verdict

**Repairable with targeted edits — not a rewrite.** Three quarters of the findings across all five stages collapse into one contained restructure; the remainder are edits inside the new shape.

The reviewer also recorded a structural note in the document's favour: *"the skeleton — problem → measurement → mechanisms → alternatives → gates → DIP — is better than most designs of this size, and the ordering is load-bearing. Do not restructure the document."*

---

## Q1 — Is there one root cause behind B1/B2/B3/B4 and M7?

**Yes, but not the candidate as I stated it.** The proposed hypothesis was "the document specifies intent in prose and never in an executable artefact." The reviewer refined it to something narrower and more actionable:

> **Every load-bearing quantity in this document is a hand-computed number typed into prose, and nothing recomputes it.**

That single property explains why the same defect recurs in the four named places and in roughly twenty more.

### Test results

| Finding | Absent artefact, or hand-typed number? | Fits? |
|---|---|---|
| B1 metric (`≤37/≤94`, `--stat`) | The metric is a sentence; the command in it counts a different thing. Nothing runs it. | Yes, both |
| B2 config values | Five values as a prose table with "Set by: deployment." An `ir.config_parameter` record with `noupdate="1"` is a 12-line XML file. | Yes |
| B4 / D7 file set | Three options in prose; the file set derived by hand in a footnote table that already disagrees with itself (37 vs 54 vs 49) | Yes |
| Stage 7 M7 allowlist | "The enumerated patterns" is a phrase. No pattern file, no allowlist file, no ceiling. | Yes |
| Stage 6 B1 (content lives outside) | The artefact *exists* — `change_register.md` — but was never reconciled. | Partly |
| Stage 6 B3 (six vs eight surfaces) | Six and eight are both typed; the set was never enumerated as a data structure with IDs. | Yes |
| Stage 6 B5 (`assets` key, `models` import) | The manifest is a prose bullet list of keys; lossy exactly where a written manifest is not. | Yes |
| **B3 (CUJs vs Non-Goals)** | Two prose statements contradict. No artefact resolves it and none should — governance choice. | **No** |
| **M23/M24/M25/M27** (runbook, password, licence, bus factor) | Risk acceptance and legal judgement. No artefact repairs these. | **No** |

So the root cause covers **all four Blockers**, the file-set model, both gates, and the configuration tier — the majority of the review by weight. It does not cover governance (B3) or legal/operational risk (M23–M25, M27). **That residue is genuinely editorial.**

### Is it architectural or editorial?

Both readings are defensible and the distinction decides the verdict, so it is stated precisely: it is **architectural in one respect** — the repair changes what the plan *produces*, from "a design plus a register" to "a design plus one machine-readable change manifest from which the register, the budget, the gate allowlist and the file table are all derived." It is **editorial in extent** — the page count of that repair is small.

The reason it matters is empirical: this document has been through four revisions and every revision produced a fresh crop of count contradictions — eight in Stage 6, ten in Stage 7. **A hand-typed count drifts by construction.** Fixing the individual numbers buys one clean revision, not a stable document.

### The single change that repairs all of them

One file — `castadoo/change_manifest.toml` — with four record types:

- **`[[change]]`** — `path`, `kind` (create / modify-binary / modify-text / non-file), `mechanism`, `upstream_owned`, `reversible_by_uninstall`, `status` (required / optional / conditional), `surface`, `reason`
- **`[[setting]]`** — `model`, `key`, `value`, `noupdate`
- **`[[assertion]]`** — `surface`, `request_or_renderer`, `expect`, `environment` (source-tree / deployed)
- **`[[allowlist]]`** — `pattern`, `path_scope`, `reason`

Then: the register becomes a rendering of it; Gate 1 diffs changed paths against `[[change]]`; Gate 2 diffs grep hits against `[[allowlist]]`; the budget becomes a count over a `WHERE` clause; the footnote table at 1419–1432 becomes a `GROUP BY kind`; the DIP is generated or at minimum linted against it. **One source, five views.**

About 80 records and ~100 lines of checker — the cheapest component in a plan priced at ≈17 h, and it reopens none of D2, the branch model, the mechanism taxonomy or any decision. It changes where intent is stored, not what the intent is.

This restructure also **subsumes** Stage 7's separate fixes to B1 ("define the unit") and M7 ("scope the lint") — those become properties of the manifest rather than two more paragraphs to keep in sync.

---

## Q2 — The twenty files counted three ways: the model is wrong, not the bookkeeping

The design runs three axes over one set of files: a five-step **Tier** in the DIP, a four-rank **Mechanism** in the Technical Plan, and a **Create/Modify** binary in the preamble. None of them is the axis the document needs.

The properties the design must track per file are orthogonal — four of them:

1. Does it carry recurring conflict surface? *(merge cost)*
2. Is it reversible by uninstalling? *(rollback story)*
3. Does it count against the budget? *(Gate 1)*
4. Is it upstream-owned? *(LGPL provenance)*

`Tier` is a single ordinal scale pretending to answer all four, and it cannot. The proofs are in the document:

- **Item 26** (1149–1163) sits under "Tier 1 — base addon" while being six overwrites of upstream blobs: Tier 3 by the document's own definition, upstream-owned by any definition, irreversible by uninstall, and counted by `git diff` while the register's file table does not list it.
- **Item 42** (1313–1322) sits under a heading that says "the only files with a recurring conflict surface" and its own text says it is "**Not** modified in the repo."
- **Item 3** is not upstream-owned, is reversible, does not count in the register's "37 upstream paths" — and is counted by `--stat`.

Tier can express none of those three. That is why the same 20 files produce "4 irreversible" (815), "16 binaries" (864), "17 images" (register 279) and "11 committed binaries" (800). **That is not four arithmetic slips; it is one relation being asked to answer four questions and answering a different one each time.**

**Replace the tier axis with the four boolean columns.** Then "20 files, not 4" is a `WHERE` clause, not a correction, and the finding class cannot recur — a stronger outcome than fixing the count.

### This also corrects Stage 7's diagnosis of B1

B1 is **not** "define the unit once" — the unit is already wrong, and the register says so itself:

> "`setup.nsi` 87 lines is 86% of the in-place edit volume by count, but it is a leaf file that upstream touches once or twice a year. `webmanifest.py` is 2 lines and upstream touches it most years — that is a higher conflict *rate* per line. … Ranking by count would put the effort in the wrong place." (register 351–357)

**The document discovers that count is the wrong metric — and then ships count as Goal G5, as Gate 1, as the effort estimate, and as the difficulty narrative at 58–61. The register's best paragraph contradicts the design's headline goal, and the goal won.**

This is new to Stage 8; no earlier stage caught it. It means G5's repair is **not a definition but a change of quantity**: budget `lines × upstream-touch-frequency-per-release`, or budget only the paths upstream actually touches in the last N point releases, and report `setup.nsi`'s 87 lines as *volume with low rate* rather than as 86% of the risk.

---

## Q3 — How much survives if the branding lives in a separate repo? Is the fork justified?

### What survives: almost all of the architecture

Items 1–25 are 26 files and every one is additive; they can live in a standalone addon repo on `addons_path` with no fork. The mechanism taxonomy, the per-module overlay shape, D1-C, D7, the asset-from-mark rule, the filename-preservation trick and the gate concept all survive unchanged.

What does not survive is the **repository topology**: two branches, the mirror, G1–G3, D2, the sync procedure and Alternatives A–D — roughly 300 lines and the most confident prose in the document.

The 16 binary overwrites *look* like they must stay in the fork because the paths are inside `addons/web`. They do not. **One inherited view that rewrites the three icon references, plus the icons served from `castadoo_branding/static/img/` at their preserved filenames, converts 16 upstream-path overwrites into 0 at the cost of ~3 lines of inheritance.** The design rejects that trade at 478–480 because it prefers zero reference edits to three; under a separate-repo model the preference inverts, and nobody has priced it either way. This belongs *with* Stage 7's M20(a), not separate from it.

### What actually remains in the fork after both moves

| File | Lines |
|---|---|
| `release.py` | 1 |
| `database_manager.qweb.html` | 4 strings |
| `webmanifest.py` | 2 |
| `config.py` | conditional |
| `setup/package.py` | 8 |
| `License.rtf` | 1 |
| `setup.nsi` | 87 |

Surface 5 is 87 of those 94 in-place lines.

### Verdict on the fork

**It is justified — by exactly one thing, and the document never says so.** The fork exists because `setup.nsi` cannot be reached from `addons_path`. Every other in-tree file is one, two or four lines.

If Surface 5 is deferred — which Stage 7's M20(c) and Stage 5's M5 both argue for, and which the Non-Goals at 165–166 already forbid *building* — then the in-tree diff is ~7 lines and the correct artefact is a patch file plus a separate addon repo. **A fork with a 7-line overlay and a `--no-ff` merge ritual is answering a question nobody is asking.**

This is the architectural dead-end Zoom Out exists to find, and it is new to this pass. The document assumes the fork (its title *is* "Rebranded Fork"), then optimises zealously inside the assumption. It never states the conditional:

> **If Surface 5 is in scope, the fork is required. If it is out, G1–G3, D2, the sync procedure and Alternatives A–F should be deleted and the plan should be a three-page addon repo.**

Decide this before anything else, because it determines whether a third of the document survives.

---

## 🔴 BLOCKER

### B1. The fork's justification is a surface the Non-Goals exclude

*Scope:* Non-Goals 165–166; Technical Plan 344–414; sync procedure 486–531; Alternatives 563–614.

As Q3. **This is the highest-leverage edit available, because it can delete a third of the document rather than repair it.** Every commitment that makes this document long — the two-branch model, the pristine-mirror goal, D2's merge ritual, the acquisition alternatives, the sync runbook — is load-bearing only for `setup.nsi`, and the Non-Goals state that no installer will be built.

**The one sentence the document needs and does not contain:** "The fork exists because `setup.nsi` cannot be reached from `addons_path`; if Surface 5 leaves scope, this becomes an addon repository plus a patch file."

Note the internal tension this exposes: CUJ 5 (277–279) requires *building* the installer, and Stage 7's B3 found that the Non-Goals forbid it. Stage 8 makes the consequence concrete — the disagreement is not about a test, it is about whether the fork has a reason to exist.

---

## 🟠 MAJOR

### M1. "Cheap to sync" measures the smaller of the two costs

*Scope:* G5 (119–122), sync procedure (515–531), 58–61.

The thesis counts **merge** cost. It omits the recurring **human** cost: re-applying 87 lines after take-upstream (522, 1255), the manual POS receipt print (1402–1403), the manual email-client check (1407), the manual PWA install on two devices (1400–1401), the asset recompile, and — under D7-B — a `-u castadoo_branding` per sync.

That is plausibly **1–2 hours of human time per point release against a merge cost near zero.** "Cheap to sync" is therefore *unproven* rather than established, and the honest goal is amortised cost per sync including the manual set.

**Fix:** restate G5 in amortised terms, and count the manual verification steps as cost rather than as verification.

---

### M2. The decision sheet's precision is inverted

*Scope:* register D1 (390–393), D7 (402–406), Open Questions 3–5, Non-Goals 165–166.

D1-C vs D1-A is priced to the hour — 37 files/94 lines/≈17 h against 43/101/≈19 h — a two-hour delta that excluded customer first-contact mail (Stage 7 M21). The two decisions that change the *shape* of the answer, **D7 and Surface 5, are unpriced.**

Worse: those two hours sit inside a ≈17 h figure the register documents as excluding the four largest components (register 348–349). **The only quantified decision in the design is quantified inside a number the design admits is wrong by an unknown factor.**

**Fix:** price D7 (one hook, one convention, or eight installs) and Surface 5 (87 lines, a build-and-test capability, and the entire fork) — or stop quoting ≈17 h as a basis for anything.

---

### M3. The budget metric contradicts the register's own finding that count is the wrong metric

*Scope:* G5 (119–122), 58–61, register 351–357.

See Q2. The register argues that `setup.nsi`'s 87 lines are 86% of the volume but a low conflict *rate*, and that "ranking by count would put the effort in the wrong place." G5 then adopts count as the goal, Gate 1 as the enforcement and ≈17 h as the estimate.

**Fix:** budget `lines × upstream-touch-frequency-per-release`, or budget only paths upstream touched in the last N point releases. Report `setup.nsi` as volume-with-low-rate.

---

### M4. Stage 5's B1 escalates: the nine-addon split is not merely over-machinery, it is the expensive shape under D7

*Scope:* 344–414, D7 402–414, items 8–25.

Stage 5 recorded a disagreement between `egm-zoom-out` (collapse to one overlay) and `egm-inventive-catalyst` (the split is required by Odoo's dependency-chain install). **Stage 8 resolves it, partly in favour of collapsing**, on a ground neither reviewer used: D7 makes the split *expensive*. Eight overlays mean eight install decisions instead of one under Option A, or eight `depends` under Option C.

"One base plus one extra-surfaces addon" is not just smaller — it is **the version of the split that makes Option B cheap.** Stage 5's suggested resolution — "shape correct, size wrong" — is the agreed position.

---

## 🟢 NIT

### N1. Two toolchain choices are left open inside a plan that claims none are

*Scope:* 458–471, 1370–1371.

"opentype.js (Node 22) or fontTools"; "sharp (npm) or cairosvg (pip)". Same class as Stage 6 finding 18, at a location it missed.

**Fix:** one line each — pick one, name the reason.

### N2. The manifest lists a non-change and a non-file as items — correctly

*Scope:* items 34 and 42; documented at 1438–1439.

Deliberate and documented. Should survive the restructure as `status: no-op` rather than as an item. Recorded so it is not "fixed" by mistake.

---

## Confirmation of Stage 5 findings

One line each; all unchanged, no repairs occurred in the intervening stages.

| Stage 5 | Status |
|---|---|
| B1 nine-addon split | Survives, **strengthened** — see M4. Disagreement resolved. |
| B2 default branch | Unchanged at 321–324 |
| M1 Gate 2 unbounded | Unchanged; see Q1 |
| M2 three sources of truth | Unchanged, **confirmed** — register still keys on line numbers; 882 still says item 35 |
| M3 rollback story | Unchanged at 811–817 |
| M4 items outside six surfaces | Unchanged |
| M5 CUJ 5 vs Non-Goals | Unchanged, **escalated to the fork's justification** (B1) |
| M6 DIP duplicates register | Unchanged |
| M7 config outside VCS | Unchanged; Stage 7 B2 restates it as Blocker, correctly |
| M8 `!default` | Unchanged, still wrong at 157–161 and 691–695 |
| M9 D1-C render-time decorator | Unchanged, still absent at 148–157 |
| M10 D7 fourth mechanism | Unchanged — three options at 402–406, register still ends at D6 |
| M11 installer `!include` | Unchanged |
| All Stage 5 nits | Unchanged |

---

## Clean bill of health

Checked at this altitude and genuinely sound; Stage 9 should not re-open these:

- The measurement-correction table (73–88) and its four-purples consequence.
- The datadir invariant and the one-line `release.py` conclusion.
- Non-Goals each stating a consequence rather than an absence (135–168) — "which is what makes the leakage auditable."
- Alternatives that carry the measurement which killed them (565–643, 673–686).
- D2's merge rationale and its LGPL-by-product argument.
- The data/configuration table's altitude (421–427).
- The `.po` deferral and its `msgstr` mitigation.
- The square-from-mark / never-the-wordmark rule (475–477).
- The filename-preservation decision (478–480).
- The silent-failure diagnosis at 90–103 — "correct, and the reason the gates exist at all."
- **Document skeleton and section ordering.** Do not restructure.

---

## Repair sequence

Three edits, in dependency order. This is the recommended path for the resolve phase.

**1. Decide Surface 5 first.** Its answer determines whether a third of the document needs to exist. One paragraph stating the conditional from B1. If Surface 5 is out: delete G1–G3, D2, the sync procedure and Alternatives A–F, and re-scope to an addon repository plus a patch file. If in: keep, but justify the fork by `setup.nsi` explicitly and stop justifying it by "rebranding."

**2. Replace the tier table, the budget sentence and the register with one declarative change manifest**, and derive the other views from it. ~80 rows. This removes B1, B2, B4's file-set half, M1, M6, M7's allowlist half, M12 and most of Stage 6's count findings — **not by fixing them but by making them unexpressible.**

**3. Name the two missing artefacts as deliverables rather than prose obligations:** the deployment checklist (cited six times, created by nothing) and the rendered-output assertion suite (promoted from Future Work to a third gate). This makes B2's config tier and the silent-failure mechanisms *enforceable* rather than *described*.

Everything else — the count contradictions, M13–M18, the nits — is cleanup inside the new shape, not work in its own right.

---

## Handoff to Stage 9

Stage 8's verdict changes what Stage 9 should audit. If the repair sequence is adopted, Stage 9's detailed-plan findings in 874–1449 are largely superseded by the manifest restructure — line-level verification of a file set that is about to be replaced by ~80 declarative rows would be wasted effort.

Two options for the gate:

- **Audit as written** — Stage 9 verifies the current 874–1449 on its own terms, and its findings are folded into the consolidated report alongside this one. Costs one stage, produces a complete record of the pre-repair state.
- **Repair first, then audit** — apply the three edits, then run Stage 9 against the new shape. Cheaper overall, but breaks the skill's fixed five-stage sequence and leaves the pre-repair DIP unaudited.

The skill's sequence is fixed at Stage 5 → 6 → 7 → 8 → 9, so **the default is to proceed to Stage 9 as written.** The recommendation is recorded here so the terminal gate can offer the alternative.

**Totals: 1 Blocker · 4 Major · 2 Nit**, plus resolution of one Stage 5 reviewer disagreement and escalation of one Stage 5 Major to Blocker.
