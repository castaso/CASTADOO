# Stage 7 — Critic Review

**Target:** `docs/designs/castadoo-rebrand-fork.md` — **FeatureRange, lines 1–873**
**Standard:** `resources/document_standards/feature-spec-standard.md`; template order from `skills/egm-draft/references/design_doc.md`
**Reviewers:** `egm-design` (hostile architecture), `egm-structural` (layout/template), `egm-style` (editorial)
**Context supplied:** `concepts_brief.md`, `change_register.md`
**Date:** 2026-11-17

---

## Verification limits

The Odoo 17.0 tree is not browsable to any reviewer in this stage (read-only personas; no shell, no grep). Every `file:line` citation against tip `9c58cae5` is **unverified**: `webmanifest.py:48`, `config.py:50/78`, `ir_module.py:420-422`, `models.py:5103`, `setup.nsi:87`. Verdicts below rest on internal consistency, the register, and domain reasoning about the cited mechanisms. Path and line verification belongs to Stage 9.

Two reviewers said this explicitly; the style reviewer's "KEEP" verdicts therefore mean *cited and internally consistent*, not *independently confirmed*.

**One reconstructed item.** The design reviewer's M11 arrived truncated on both attempts — only its closing clause ("…saving is exactly what guarantees the stale client") and its fix survived transport. It is reported below as **M19** with its scope and rationale reconstructed from those fragments and from the asset/PWA material at 458–485. It should be re-confirmed in Stage 8 or Stage 9 rather than trusted as quoted.

---

## Reviewer convergence

Nine findings were reached independently by more than one reviewer. These are the load-bearing ones and they should not be re-litigated in Stage 8:

| # | Convergence | Reviewers |
|---|---|---|
| 1 | The budget and Gate 1 measure different quantities; the gate cannot pass | design B1, style C1 |
| 2 | The configuration tier is invisible to both gates and deploys unbranded | design B2, style D3 |
| 3 | Binary replacement is not conflict-free, and the rollback count collapses new files and overwritten blobs | design M8, style C3, (Stage 5) |
| 4 | Gate 2's allowlist is unbounded and its pattern set is never written down | design M12, style C12, (Stage 6) |
| 5 | D7 is undecided while the plan is presented as executable | design B4, style V2/B4, structural X-02 |
| 6 | The surface taxonomy does not close — six-vs-eight, S-IDs never defined, "ten" sites table holding thirteen | design M17, structural TBL-01/X-03, style S3 |
| 7 | `!default` does not block a later-loaded assignment; Alternative J's rejection reason is wrong | design M3, style C5 |
| 8 | LGPL and trademark are conflated; the licence claim is asserted, not cited | design M10, style C8 |
| 9 | Count discipline fails in the places the document's credibility depends on | all three |

**The pattern behind 1, 4 and 9:** the document's thesis is that a budget must be derived from measurement and enforced by a gate. Three of its four budget mechanisms — the metric, the lint and the counts — are specified at a level of precision that cannot be executed. The measurement work was done; the *enforcement artefacts* were not.

---

## 🔴 BLOCKER

### B1. The 37-file / 94-line budget cannot be independently verified, and Gate 1 fails on the plan's own output

*Scope:* 34, G5 (119–122), 800, 811, 864, Gate 1 (495–499), item 46 (1351–1364); cross-checked against `change_register.md` 279, 318–343.
*Reviewers:* `egm-design` (B1), `egm-style` (C1).

Nine addons are specified (359–374). Each needs at minimum `__manifest__.py` and `__init__.py` plus its view XML. The register's "23 additive items" counts **view records**, not files, and its deduplicated file table (358–343) contains no manifest or `__init__.py` entry at all. Nine modules is therefore ≈18–27 files that `git diff --stat` will see and the register does not enumerate.

`egm-style` gives the arithmetic in the other direction: G5 defines the metric as `git diff --stat upstream/17.0...HEAD` with "lines ≤ 94", but `--stat` counts insertions **plus** deletions **plus every line of every new file**. The 94 is 87+2+4+1 edited lines only. The register itself quotes "86%" (351) while line 59's "87 such lines" of 94 implies 92.5% — a third denominator.

Either the metric excludes additive files — in which case `git diff --stat` is the wrong command and no substitute is supplied — or the 94 is wrong. An implementer wiring item 46 literally ships a gate that fails on the first commit.

**Fix:** define the unit once, state the arithmetic, exclude new files from the metric by construction (e.g. `git diff --stat --diff-filter=M`), and reconcile 94 against 87+2+4+1 in the document.

---

### B2. The cheapest tier lives in the database, not the tree, so a correct build deploys as unbranded Odoo with no error

*Scope:* 332–334 (rank 1), 416–428, 447–451, 486–513, 867–870; CUJ 1 (211–222).
*Reviewers:* `egm-design` (B2), `egm-style` (D3).

Company name, logo, `email_secondary_color`, `web.web_app_name` and `website.favicon` are all "Set by: deployment". Gate 2 greps the post-sync **tree** (501); Gate 1 diffs **paths**. Neither can see a database. The design concedes this only in Future Improvements (867–870).

The consequence is stated but not mechanised: a branded tree on a fresh database yields a blank logo, `name` = "YourCompany", unset `web.web_app_name` (whose stock fallback is `Odoo`) and unset `email_secondary_color`. CUJ 1's `GET /web/login` assertion still passes on the inherited footer alone — because 447–451 excludes the only mechanism that would have set it.

**Fix:** seed the shippable subset (`web.web_app_name`, favicon, email colour) as `noupdate="1"` module data, and add a third assertion tier that checks rendered manifest name, company logo and login body after deployment. Company name and logo can stay deployment-owned; the other three cannot, or the gate is checking something the plan never produces.

---

### B3. Four of the six CUJs require capability the Non-Goals forbid, and no owner is named for any of them

*Scope:* Non-Goals 165–166 versus CUJ 3 (251), CUJ 4 (266), CUJ 5 (277–279), CUJ 6 (288).
*Reviewer:* `egm-design` (B3).

"No installer build pipeline… This plan produces a source tree" sits against CUJ 5's "build the installer, install on a clean Windows VM", CUJ 4's "manual install on one Android and one iOS device", CUJ 3's "manual send through a real SMTP sink", and CUJ 6's PDF extraction from a running deployment.

This is not cosmetic. Item 38's registry-key migration (1262–1269) is one-shot and non-reversible and can only be validated by actually building. Either the non-goal is honest and CUJ 5 reduces to a static review of `setup.nsi`, or the deliverable includes a build — and that decision moves the effort estimate.

**Fix:** split the CUJs into source-tree-verifiable and deployment-only, and give the deployment-only set an owner and an environment or move them to Non-Goals.

---

### B4. D7 is undecided while the plan claims to work under any answer; the three options do not produce the same file set

*Scope:* D7 (400–414), Open Questions (205–207), item 1 (891–905), item 2, item 7 (968–978), 551–552.
*Reviewers:* `egm-design` (B4), `egm-style` (V2, B4), `egm-structural` (X-02, X-04).

"The plan needs an answer before the Detailed Implementation Plan can be executed" (D7 head) and "is written so that any of the three can be applied to the same file set" (404) cannot both hold:

- **Option C** (base declares all overlays as `depends`) deletes the reason for items 8–24 entirely and violates item 1's stated hard requirement that `depends` "must contain `web` and nothing else".
- **Option A** removes item 7 (`hooks.py`) and item 2's `hooks` import, and silently leaves the footer as Odoo whenever an operator omits a module from the install list (stated at 404).
- **Option B** adds a `post_init_hook` plus a `-u` convention.

The file set differs under every option, so the plan is not executable until an author decision exists. The section is also written as verdict then disclaimer — "Option B is the only one that is both reliable…" (408–409) followed by "This is an author decision, not a drafting decision" (412) — which reads as a settled recommendation that withdraws itself.

Separately: **D7 has no row in the register's decision sheet**, which genuinely ends at D6 (`change_register.md:416`), while Gate 1 checks the diff against that register. A reader following D7 there finds a document that does not contain it.

**Fix:** decide D7 before the Detailed Implementation Plan, state the default the plan assumes at the section head rather than after the verdict, and add D7 to the register.

---

## 🟠 MAJOR

### Scope and budget

**M1. The surface taxonomy has no closure anywhere in the document.**
*Scope:* G4 (115–118), 34, table 430–440, 442, 551; register 318–343.
*Reviewers:* `egm-design` (M17), `egm-structural` (TBL-01, X-03, X-07), `egm-style` (S3).

Three separate non-closures:
- G4 promises "six named surfaces" then lists **eight** comma-separated entries, never saying which fold into which. The register totals also count `release.py` (326) and the user-menu JS patch (327), which belong to none of the eight — so "37 files" and "six surfaces" describe two scopes with a two-file gap.
- Eleven distinct S-IDs are used (S4.01–S4.10, S4.18, S4.19, S4.20) and **no S-numbering table exists anywhere in the file to line 1449**. First use at 425 carries no pointer to the register. A reader cannot resolve S4.05, S4.08, S4.18 or S4.19 at all.
- The table at 430–440 is headed "the ten in-scope email/notification sites" and enumerates **thirteen** (4 data-driven + 5 literals + 4 more on row 440). Line 80 repeats "Four of ten"; 442 concludes "four of ten are free and five need the literal replaced" — which sums to nine, against a table of thirteen.

**Fix:** enumerate S1–S6 once with their member files, add a seventh "outside the six" row for `release.py` and the user-menu patch, retitle the email table to thirteen, and add the S-ID table or a pointer at 425.

---

**M2. The nine modules have no stated directory, no `addons_path` statement and no discovery mechanism.**
*Scope:* 344–374, 359–372.
*Reviewer:* `egm-design` (M16).

Across 873 lines of architecture the addons have no home. The base-tier description also mixes in-tree edits with addon content — "web views, PDF titles, PWA colours, release description, user-menu patch" (361) — although `release.py` and `webmanifest.py` are unreachable from any addon. That is the same seam that makes the addon count and the file budget irreconcilable in B1.

**Fix:** state the directory layout and separate in-addon from in-tree in the architecture section, not in the runbook.

---

**M3. The headline effort figure excludes every component that makes the budget checkable, and the target platform is never established.**
*Scope:* register 348–349, Non-Goals 165–166, Open Question 3.
*Reviewer:* `egm-design` (M18).

"≈17 h" excludes asset design, the register itself, both CI gates and all deployment work. Meanwhile 87 of 94 edit lines buy an installer the Non-Goals will not build, on a platform the Open Questions never establish — Open Question 3 asks tenancy, not operating system.

**Fix:** quote the headline with its exclusions attached, and either establish Windows-native as the target or move Surface 5 out of the headline budget.

---

**M4. Prose enumerations disagree with the tables they summarise.**
*Scope:* 419 versus 421–427 (data model); 153–156 versus 700–705 and register S4.11–S4.17 (excluded records).
*Reviewers:* `egm-style` (S4, S1).

- 419 says "two company fields and one system parameter"; the table below lists **three** `res.company` fields, one `ir.config_parameter` and `website.favicon`.
- Non-Goals names **six** `mail.template` body records; Alternative K names seven; Alternative N says "seven"; item 46 says "the six excluded data files". `validation_email` is missing from both prose lists while present in the register table. No record→module mapping is given, so a reader cannot tell whether the allowlist is complete.

**Fix:** derive both sentences from the table, or delete the sentences and cite the table.

---

**M5. G4's success statement is unfalsifiable.**
*Scope:* 118, versus 221–222, 264–266, 288–289.
*Reviewer:* `egm-style` (S11).

"Branding means a user reading those surfaces sees CASTADOO" cannot be checked. The falsifiable versions already exist in the CUJs — the login assertion, the manifest name assertion, the PDF text extraction.

**Fix:** relocate G4 onto those assertions and drop the prose definition.

---

**M6. The measurement chain slips between files, lines and hits, and omits the step that would make 1,343 checkable.**
*Scope:* 83–88; also 146–148, 728–739.
*Reviewer:* `egm-style` (S8), supported by `egm-comprehension` (Stage 6, finding 10).

"26,560 **files** contain `Odoo`; 5,496 of the matching **lines** are the notice; 18,920 are translation files. Of the remaining 1,343 hits…" The 8,985 intermediate step is not shown, so 1,343 cannot be reconstructed: 26,560 − 5,496 − 18,920 = 2,144, not 1,343. Non-Goals then treats 18,920 as a **file** count while Alternative M gives "the 3,410 `.po` files" for the same set.

**Fix:** restore the chain with one unit per term, or drop the derived number and cite the register.

---

### Gates and enforcement

**M7. Gate 2 as specified is unbounded work hidden in a one-line CI item.**
*Scope:* 486–513, 100–103, G8 (129–131), item 46 (1351–1364).
*Reviewers:* `egm-design` (M12), `egm-style` (C12); also Stage 5 M1, Stage 6 finding 1.

The tree holds 18,920 `.po` files, 5,496 mandated headers and 1,343 residual hits. "Grep the post-sync tree for the enumerated patterns; fail on any unlisted hit" therefore needs thousands of allowlist entries to pass at all. The design predicts exactly this — "otherwise it fills with noise and gets disabled" (509–510) — and supplies no pattern list, no path scoping, no `.po` exclusion, no false-positive budget and no owner.

**Fix:** scope the lint to the register paths plus a coarse whole-tree pattern set, specify both sets in the document, and state the allowlist ceiling. The rendered-output assertion corpus already listed as Future Work (867–870) is the correct long-term target; the honest shape is two tiers, not a swap.

---

**M8. G2 is called "a CI gate, not a habit" but is step 3 of a manual procedure and appears in neither gate list.**
*Scope:* G2 (110–111) versus 486–513, 520.
*Reviewer:* `egm-design` (M13).

A maintainer who merges the overlay without fast-forwarding ships a stale published `17.0` with nothing failing. The three-dot diff still computes off a correct merge-base, so Gate 1 passes while the mirror claim is quietly false.

**Fix:** make it Gate 3 with a real invocation, or stop calling it a gate.

---

**M9. G8 claims CI catches unbranded strings; the document's own Future Work says it cannot, and silent under-coverage is the gap.**
*Scope:* G8 (129–131) versus 867–870; also 158–160, 92–98.
*Reviewer:* `egm-style` (S10), extended with `egm-design`'s angle-5 failure #3.

G8 says "an unbranded user-visible string … fails CI". But 868–869 concedes it "cannot see a string composed at runtime… `web.web_app_name` and the PDF title". The third silent path is the one that matters most for a design built on inheritance: an xpath that *still matches* after upstream rearranges its surroundings leaves the string in place with no error, and an Owl `t-inherit` with a wrong parent loads silently (158–160). Gate 1 counts files and lines; Gate 2 fires only on this document's enumerated patterns.

**Fix:** calibrate G8 to "literal strings in enumerated paths", and add an install-time smoke test plus rendered assertions as the control for under-coverage. "An xpath whose anchor upstream renamed fails loudly at install, which is fine" (92–93) is true only if something installs the addon — no gate does.

---

**M10. D7 has no counterpart in the register that Gate 1 reads.**
*Scope:* 400, 835, plus 206, 412, 551, 662, 670, 971, 977, 983, 1340–1341, 1380; `change_register.md:416`.
*Reviewer:* `egm-structural` (X-02).

Reported separately from B4 because it is an artefact defect, not a decision defect: the register's decision sheet genuinely ends at D6, and Gate 1 (1355–1357) checks the diff against that register. An author decision that lives only in the design is not in the versioned record.

**Fix:** add D7 to the register as part of resolving B4.

---

**M11. The highest-risk manual operation gets six words.**
*Scope:* 522 ("resolve conflicts once, here — `setup.nsi` is the expected site").
*Reviewer:* `egm-design` (M14).

87 of 94 edit lines live in one file, and "resolve" is never defined: take-ours wholesale, hunk-by-hunk, or take-theirs-and-re-apply. Take-ours silently discards new upstream installer pages and French translation entries, producing a partially-updated installer with no error and no gate that could notice.

**Fix:** specify "take upstream, re-apply the register's 87 enumerated lines", enforced by Gate 1.

---

### Mechanism claims

**M12. Binary replacement is not conflict-free, and the rollback count collapses two different kinds of change.**
*Scope:* 336, 811–814, 815–817.
*Reviewers:* `egm-design` (M8), `egm-style` (C3); also Stage 5 M3.

"Conflict surface: none — git sees a new blob, not a hunk" is false in the direction that matters: when both sides modify the same binary path, git reports `CONFLICT (content)` and offers no hunk resolution. "Take ours" then silently discards an upstream fix while looking identical in review. Upstream does periodically touch its own logo assets, and 16 paths are exposed.

The rollback clause has the matching error: "Removing the branding addon restores stock behaviour … without touching upstream files" is true for the ~25 additive addon files and false for the 16 overwritten blobs. Listing "the 4 in-place edit sites" as the irreversible set undercounts by all 16 binaries.

**Fix:** add a path-scoped `.gitattributes` (`merge=ours` on the 16 binary paths) so the table becomes true, mark rank 3 as "conflicts on upstream touch; resolution discards upstream, review the diff", and split the rollback claim three ways: additive / replaced-binary / edited.

---

**M13. "Silently relocates every filestore" describes an event that does not happen.**
*Scope:* 75, 679–681.
*Reviewer:* `egm-style` (C2).

Nothing moves. The datadir becomes *unreachable* at the new path and Odoo creates an empty one without raising. The distinction matters because it changes the recovery: renaming back restores access, whereas a genuine relocation would not.

**Fix:** "makes the existing datadir and every filestore under it unreachable; Odoo creates an empty one without raising."

---

**M14. "~90% of the email surface becomes additive" is not the figure the document's own inventory supports.**
*Scope:* 76, versus the 20-site inventory.
*Reviewer:* `egm-style` (C4).

11 views + 7 data bodies + 2 Owl = 13/20 = 65%. The 90% figure requires traffic-weighting, which is nowhere asserted.

**Fix:** state the 65% count, or state the traffic weighting and its source.

---

**M15. "None of them is user-visible" is the only absolute claim in the document with no consumer citation.**
*Scope:* 141–142 (`version_info`, `series`, `odoo.conf`).
*Reviewer:* `egm-style` (C6).

Every comparable claim here cites a mechanism or a measurement; this one cites nothing. `version_info` and `series` surface in the database manager and in module upgrade reports.

**Fix:** name the non-rendered fields explicitly and record version display as accepted leakage, alongside the `.po` entry.

---

**M16. Service-worker caching guarantees a stale branded client after upgrade, and nothing checks it.**
*Scope:* asset/PWA section (458–485); CUJ 4 (254–266).
*Reviewer:* `egm-design` (M11 — **reconstructed**, see Verification limits).

The PWA saving is precisely what makes an installed app keep the old brand after the tree is updated: the shell is cached, so the offline page and icons survive a deploy. There is no cache-versioning decision in the asset section and no assertion in CUJ 4 that a post-upgrade client shows the new brand.

**Fix:** add a cache-versioning decision to the asset section and a stale-PWA verification step to CUJ 4. **Confirm the reviewer's exact wording in Stage 8 before acting on the detail.**

---

**M17. Three sections answer "may a clone duration be quoted?" three ways, and one of them quotes one.**
*Scope:* G6 (123–125), Open Question 4 (190–193), NFR (799).
*Reviewer:* `egm-style` (S9).

G6: "under 500 MB (measured: 444 MB) … so a maintainer can clone in minutes rather than hours". Open Question 4: the two bandwidth measurements disagree by ~34× and "Every duration estimate for the initial clone depends on which is real." NFR: "so no duration is quoted."

**Fix:** calibrate G6 to size only.

---

### Alternatives

**M18. Alternative J's rejection rests on an unmeasured precedence claim, and its second half is circular.**
*Scope:* 687–698; Non-Goal 157–161; D4.
*Reviewers:* `egm-design` (M3), `egm-style` (C5); also Stage 5 M8.

"`!default` resolves before any later file in the bundle, so the change requires editing a compiled-variable file" is an ordering claim the document's own methodology (82–88) says must be measured. `!default` at that line means *that line* yields to an earlier definition; it does not block a plain assignment in a later-loaded file, and Odoo's asset bundles concatenate a dependent module's SCSS after `primary_variables.scss`. A new file in a branding module's asset key is mechanism **2**, not 4.

The second half — "not part of the six named surfaces" — is circular: the six surfaces are the design's own premise, and G4 lists the backend shell as in-scope.

**Fix:** measure the ordering route, or restate J as a pure scope decision on the grounds that the backend palette is out of the six. The recommendation may survive; the stated reason does not.

---

**M19. Alternative G is a strawman, and the real competitor is never compared.**
*Scope:* 647–657; register 63–65, 351–357.
*Reviewers:* `egm-design` (M1), `egm-style` (S14).

G discredits its own "290 user-visible files" figure two sentences later. The genuine alternative — in-place edit of ~30 *rendered* files instead of inheritance — is never built. And "inheritance churn costs nothing" (register 355–357) is untested for the six inline-`style`/`<style>` anchors (S1.09, S4.03/04/07/09), only one of which gets a smoke-test note.

**Fix:** replace G with INH-anchor churn versus EDIT-line churn, measured over the last N point releases. Rename the heading so it stops asserting a count its own Cons deny.

---

**M20. Three genuinely viable options are absent from 15.**
*Scope:* 556–765.
*Reviewer:* `egm-design` (M2).

- **(a)** Branding addons in a **separate repository** on `addons_path` — 23 of 37 items never touch upstream and need not live in the fork at all.
- **(b)** **Don't fork** — stock Odoo plus addons plus a deployment-time patch for the four in-place files, which makes G2 trivially true.
- **(c)** **Defer Surface 5** — 87 of 94 lines buy an installer the Non-Goals will not build.

The standard requires rejected alternatives, not an incomplete set. (a) and (c) are the two that most change the shape of the answer.

**Fix:** add (a) and (c) at minimum, and record the trade-off that killed each.

---

**M21. Alternative N is rejected on a claim the rest of the document contradicts.**
*Scope:* 741–752 versus 249–250, 153–156, G4.
*Reviewer:* `egm-design` (M4).

N is rejected as "largely staff- or supplier-facing", but 154–156 names portal-invitation, portal-welcome and account-created as customer first-contact mail, and CUJ 3 concedes a customer may see an Odoo footer. That is a breach of a named surface, not margin leakage.

**Fix:** reject N on the register's actual ground — seven watched records for one footer line — and delete the staff-facing claim.

---

**M22. One alternative overclaims and one is deferred rather than rejected.**
*Scope:* Alternative A (565–578), Alternative M (728–739).
*Reviewer:* `egm-design` (M5).

A's "a shallow base destroys the merge base" is recoverable with `--unshallow`; the shallow-push rejection alone suffices. M is "rejected provisionally", so the `.po` boundary is undecided — and the standard requires rejected alternatives, not deferred ones.

**Fix:** correct A's overclaim and convert M into a decision or a Future Work entry.

---

### Security and legal

**M23. Every security control lives in a runbook this plan does not produce.**
*Scope:* 776–785; D3 (register 402–404).
*Reviewer:* `egm-design` (M6).

Both risks are correctly labelled inherited, but both mitigations are named and unbuilt: phone-home is parked on Open Question 2 with no default, and `list_db`/`admin_passwd` are deferred to a runbook that is not an item in the plan and that neither gate can see.

**Fix:** make a one-page deployment checklist a third deliverable alongside the gates, and turn D3 into a decision with a default.

---

**M24. The stock superuser password ships in a product installer.**
*Scope:* 786–790.
*Reviewers:* `egm-design` (M7), `egm-style` (C7).

"`DEFAULT_POSTGRESQL_PASSWORD 'openpgpwd'` would break existing installs" does not hold here: this fork's install base is new installs by definition (CUJ 5 validates a clean VM). The rebrand is what converts a stock developer installer into CASTASOFT's published product installer carrying a known superuser password. The same section also says "No credential, key or token is touched by any file in this plan" (786–790), which the next sentence contradicts.

**Fix:** force a password on first run, or record it as an accepted risk with the deployment platform stated. Calibrate the absolute to "no credential *value* is modified".

---

**M25. Licence and trademark are conflated, and the LGPL claim is asserted rather than cited.**
*Scope:* 49–52, G7 (126–128), 523–524, 846; contradicts 151–152 and 720–723.
*Reviewers:* `egm-design` (M10), `egm-style` (C8).

"LGPL-3 permits this. It does not permit the fork to *claim* to be Odoo" mixes two legal frames. LGPL grants no trademark rights, and the deliverable puts CASTADOO — a mark containing Odoo's — on publisher fields and login pages, with no confusion or policy analysis anywhere. Two later passages (151–152, 720–723) treat the same question as settled differently.

G7 also calls the dating obligation "structural, not documentary", while the mechanism dates only merge commits (step 6, 523–524): an overlay commit between syncs has no dating mechanism, and the ~25 new files' licence headers are never stated.

**Fix:** add a legal risk row with an owner, state the new files' headers, cite the clause relied on or downgrade "the licence requires" to a policy choice, and drop "structural" if dating stays merge-only.

---

### Operations

**M26. "Rollout and rollback" contains no rollout.**
*Scope:* 809–825.
*Reviewer:* `egm-design` (M9).

The section is titled rollout but describes only rollback. The only case that matters for an existing deployment — a stock database moving to branded (module install, `-u`, asset rebuild, five config values, service-worker invalidation, visual check) — has no path, and B2 makes the config half the most skippable part.

**Fix:** add the per-deployment upgrade path at the specificity of the sync procedure (515–527).

---

**M27. Bus factor is one, and the document's answer is documentation.**
*Scope:* G9 (132–133), 411–415.
*Reviewers:* `egm-design` (M15), `egm-style` (S12).

"Documented, so the fork does not depend on one person's memory" conflates documentation with redundancy. The document itself warns the `--first-parent` convention "will confuse the next maintainer" (414). D1–D7, the asset pipeline and the LGPL ritual all sit with one person, no owner is named anywhere, no gate verifies itself (B1, M7, M8, M10), and there is no second reviewer, dry run or rehearsal step.

**Fix:** add a sync rehearsal on a throwaway clone plus a named backup owner, or record bus factor as an accepted risk.

---

### Structure and template

**M28. The mandatory `### Target Files to Create/Modify` H3 is missing.**
*Scope:* 874–889 (the H2 boundary; the omission is inside FeatureRange's successor but is caused by the FeatureRange-to-DIP handoff at 873).
*Reviewer:* `egm-structural` (T-01).

Template line 145 requires it directly under `## Detailed Implementation Plan`. At 874 the H2 is followed by prose (876–879) and the "**Placement decision.**" block (881–887), then `### Tier 1` at 889. The required H3 never appears; five `### Tier` headings substitute for it.

**Fix:** insert the H3 at 889 and demote the Tier headings beneath it.

---

**M29. Additional Resources and Future Improvements are mis-nested under Non-Functional Requirements.**
*Scope:* 829 (`### Additional Resources`), 848 (`### Future Improvements`), following the H3s at 774, 795, 809.
*Reviewer:* `egm-structural` (H-02).

Neither has an H2 parent, so both read as the 4th and 5th subsections of NFR. Their **placement** in document order is correct per `design_doc.md` (they belong before the DIP); their **level** is not. The mis-nesting is inherited from the template, which itself uses H3 for these two.

**Fix:** promote both to `##` and record the deviation from `design_doc.md:121`/`:130` so it is not re-introduced on the next draft.

---

**M30. A cross-reference points at the wrong item.**
*Scope:* 882.
*Reviewer:* `egm-structural` (X-01).

"(see item 35)" is attached to "**one** `addons_path` entry in `odoo.conf`". Item 35 is `odoo/release.py` (1221); `addons_path` is **item 42** (1313). Item 35 never mentions `addons_path`, `odoo.conf` or deployment. Following the pointer edits the wrong file and leaves the addon tree invisible — the failure the document itself names at 1321–1322.

**Fix:** change to "(see item 42)".

---

### Redundancy and voice

**M31. Two passages restate material that already appears verbatim, in a document that is over budget on attention.**
*Scope:* 533–552 (`### Where the open questions bite`), 488–490.
*Reviewer:* `egm-style` (R1, R2), `egm-structural` (H-04).

533–552 restates all seven open questions, each of which already ends with an italic *Shapes:* line (178–203). 488–490 is the third statement of 95–98 and the second of the two-gate remedy at 100–103. Each adds one new fact per entry, which reads as signposting at first and as padding by the fourth restatement — the same complaint the style reviewer makes about "37 files / 94 lines / 23 additive" appearing six times (34–37, 120–122, 233, 497, 656–657, 834–835).

**Fix:** delete the section and replace with one sentence per question, or delete it entirely and rely on the *Shapes:* lines. Keep the gate diagram, drop its prose restatement.

---

**M32. The document describes a repository that does not exist, in the present indicative.**
*Scope:* 11–37, 296–324, 108–109, 322.
*Reviewer:* `egm-style` (V1).

"Branch `17.0` **is** byte-identical" (22); "Nothing is edited on `17.0`" (26, 297) — interleaved with `must` (321) and completed-action passives ("This **is verified** with `git ls-remote --symref origin HEAD`" (322); "Verified by the GitHub API" (108–109)). Nothing has been created yet: there is no `castadoo/17.0` branch, no fork, no CI file.

**Fix:** add one convention line under Status — *"present tense describes the intended end state; nothing here exists yet"* — and convert 108–109 and 322–324 to requirement or move them to the Verification Plan.

---

**M33. A defensive caveat asserts something the same section denies.**
*Scope:* 171–173.
*Reviewer:* `egm-style` (D5).

"Each changes what gets implemented" is contradicted by Open Question 1's "No file in the plan changes either way" and Open Question 4's "nothing in the source tree".

**Fix:** "Two change documentation only."

---

**M34. The effort figure is used as the basis for a scope decision while excluding the four most expensive components.**
*Scope:* register 348–349 (basis for D1-C).
*Reviewer:* `egm-design` (M18), `egm-style` (Nit 7 in Stage 5).

The "≈17 h" excludes asset design, the register, both CI gates and deployment — the four largest pieces — yet is quoted in the decision sheet as the basis for D1-C. See M3 for the same defect in scope terms.

**Fix:** state the excluded total, or drop the headline number from the decision sheet.

---

## 🟡 MINOR

| # | Finding | Scope | Reviewer |
|---|---|---|---|
| m1 | "22 of the items are new files or replaced binaries" vs 23 everywhere else (34, 119, 656, 834, 1440) | 811 | structural E-04, style S2 |
| m2 | "Regenerating the **11** committed binaries" vs 16 at 864/1425 and 17 in register 279; 11 is the register's `addons/web/static/img` subtotal | 800 | structural E-02, style S5 |
| m3 | "The **4** in-place edit sites" vs six in the plan (items 35–40 add `setup/package.py`, `License.rtf`); row 1427 says 6 | 815–817 | structural E-03 |
| m4 | "The **fifth** purple — `#9E588B`" contradicts "Four distinct purples" (80) and "a fourth purple" (1069); no fifth exists | 442–443 | structural E-01 |
| m5 | "A seventh question" and "**#7** overlay activation" exist, but `## Open Questions` announces six and has no #7 | 171, 205, 551 | structural X-04, style S6 |
| m6 | D3 and D4 are never cited although their subjects appear as prose (phone-home 180–185, retheme 157–161); D2 is used at 113 before being stated | 113, 157–161, 180–185 | structural X-05 |
| m7 | "**≥ 23** items are additive" — the count is exact and `≥` reverses the logic; additive items are a subset, not a floor | 120 | structural E-05 |
| m8 | Four names for one quantity: "edit lines", "editor lines", "changed-line count", "in-place edit volume" | 34, 120, 122, 497, 351 | style B8, structural E-06 |
| m9 | "uplift drift" is coined once (507–508), never defined, and load-bearing for Gate 2 | 507–508 | style B7 |
| m10 | CUJ 2's nested bullets wrap to column 6 against content column 8; renders only via CommonMark lazy continuation | 235, 237 | structural L-01 |

---

## 🟢 NIT

| # | Finding | Scope |
|---|---|---|
| n1 | Alternatives are H4 under four H3 group headings; template puts them at H3. All 15 present, Pros/Cons/Reason correct | 563, 616, 645, 714; 565–754 |
| n2 | H4 means "alternative" in the spec half and "numbered item" in the DIP; the DIP's own `#### Footnote on file count` breaks its own convention | 1413 |
| n3 | Two extra `----` breaks beyond the template's five, diluting "separator = major boundary" | 291, 554 |
| n4 | Neither D7 table (402) nor the site-colour table (432) carries a caption, yet the D7 table is cited five times | 402, 432 |
| n5 | Fence at 383–387 tagged `text`; content is Python. Should be `python` | 383–387 |
| n6 | Fence at 517–527 tagged `text`; content is shell. Should be `bash` | 517–527 |
| n7 | `text` fences render correctly on a normal monospace stack; box-drawing and `×`/`²` glyphs go double-width under a CJK or emoji fallback. Not fixable in-document | 299–309, 359–372, 458–471, 492–505 |
| n8 | "Each open question from the section above" — the section above is `### Sync procedure` (515); Open Questions is at 169 | 535 |
| n9 | `S4.20` is out of sequence in the register (after S4.10); correctly paired with S4.10, so nothing dangles, but it feeds the "ten sites" arithmetic error | 430, 435 |
| n10 | "The consequence, stated rather than glossed:" — DROP the clause, keep the content | 154 |
| n11 | "The colour row is the one place where the convenient story and the measured tree disagree, so it is stated precisely." — DROP first two clauses, keep the table | 429–430 |
| n12 | "Step 3 is not ceremonial." — DROP the clause, keep the reason | 529–531 |
| n13 | "A seventh question surfaced while writing the Technical Plan, and it is the one with the sharpest failure mode." — RELOCATE as #7, DROP the process detail and the superlative | 205–207 |
| n14 | "Gate 2 becomes load-bearing rather than precautionary" — the conditional weakens both halves | 545 |
| n15 | "Only the concerns that carry real risk … generic concerns are omitted deliberately" — then 781–785 includes one | 771–772 |
| n16 | "It is not a smaller version of the chosen approach; it is incompatible with it." — pure cadence, already in Cons | 577–578 |
| n17 | "`auto_install` as a list is stock practice, not a trick." — answers an accusation no reader made | 376 |
| n18 | Three variants of "we are rigorous": "rather than a preference" (561), "rather than a preference to hold" (762–765), "not ceremonial" | 561, 762–765 |
| n19 | "wrong in both directions" — neither direction is named | 86–87 |
| n20 | Two unquantified rankings of the same decision ("sharpest failure mode" 206, "highest-consequence of the seven" 552) against a datadir trap the document itself calls an incident | 206, 552 |
| n21 | Missing period at 78; straight vs curly quotes at 220; bold applied ~30× including whole clauses (75, 111, 121, 160–161, 341, 412), diluting it on the KEEP claims | 78, 220, passim |
| n22 | Only `.po` carries the "accepted leakage" label (147); D1-C's exclusions (153–156) do not | 118, 137–167 |
| n23 | Alternative G is headed "Edit all 290 user-visible files in place" while its own Cons deny 290 is a user-visible count | 647–657 |
| n24 | "only immutable annotated tags … can be published" — branches publish fine, they cannot be *supported* | 626–627 |
| n25 | CUJ 2 is the only CUJ whose **Then** is a bullet list; the other five use prose | 230–237 |
| n26 | `*Shapes:*` is the only italic run-in label; every other field label is bold. Deliberate and consistent across all six | 175–203 |
| n27 | Future Improvements bullets carry two bold labels where the template shows one | 850–870 |

**Style rulings that require no action (KEEP):** 389–394 ("the overlay never auto-installs", correctly scoped with quoted `must_install` code); 22–24 ("a check, not a claim"); 92–98 ("the dangerous case is not a broken override … is an override that still applies cleanly"); 50–52 ("the work is not 'remove Odoo'; it is 'make CASTADOO the product name'"); `release.product_name`'s three appearances (75, 143–145, 673–685), each doing distinct work.

**Banned-pattern measurement:** promotional adjectives and decorative adverbs are near-absent — no "seamlessly", "effortlessly", "literally", "drastically", "obviously". "simply" (638) and "genuinely" (410, 594) are the only decorative adverbs found and should be cut. "exactly" (75, 199) is load-bearing. "silent/silently" appears 6 times (75, 224, 404, 488, 680, 791); two carry mechanism (404, 488), the rest are intensifiers — calibrate each.

**Rhetorical "not X; it is Y" construction: 16 instances in 873 lines** (~1 per 55 lines), plus ~12 bare absolutes ("No runtime overhead", "Nothing adds a query" 804; "No Odoo string anywhere" 718). The construction is the document's analytical signature and earns its space in four places (50–52, 92–98, 336, 412-adjacent); at 16 it makes a draft with seven open questions read as a settled verdict (see B4, M32).

---

## Structural clean list

Verified correct and requiring no change:

- Heading level sequence: `#` → `##` → `###` → `####`, no H5, no skipped level.
- Template H2 order and titles: Overview, The Problem, Goals, Non-Goals, Open Questions, CUJs, Technical Plan, Alternatives Considered, Non-Functional Requirements, Detailed Implementation Plan.
- **Placement** of Additional Resources (829) and Future Improvements (848) before the DIP — correct per template. Only their level is wrong (M29).
- All five tables structurally well-formed: correct header row, matching separator, consistent column count, no unescaped pipes. Zero malformed tables.
- All six code fences balanced, twelve markers, all at column 0, none inside a list, none containing markdown that breaks rendering. Widest line ~75 columns.
- List separation and marker uniformity: no list continues after a paragraph without a blank line; `*`+3-space bullets throughout; ordered items uniformly `N.`+2 spaces; no mixed markers at one level.
- Cross-references resolving: **items 1–47 all defined exactly once, no gaps, no duplicates**; G1–G9 all defined; CUJ 1–6 all defined; Open Questions 1–6 all defined; Alternatives A–O all defined; item 45's reference at 836 resolves to 1344; register §4b, Surface 4 and decision sheet D1–D6 all exist in `change_register.md`. **Item 35 exists** at 1221 — it is the *pointer* at 882 that is wrong (M30), not the item.
- Dash discipline: en dash for all ranges (`15–25`, `94–95`, `270–447`, `D1–D6`), hyphens retained inside tokens (`LGPL-3`, `D1-C`, `odoo-server-17.0`); one em-dash style only, spaced ` — `.
- Backtick discipline: paths, identifiers, commands, config keys and `file:line` refs all backticked; the brand word `Odoo` correctly left unbackticked in prose; no unbalanced `**` or backtick spans.

---

## Meets the standard

The design reviewer's verdict on `feature-spec-standard.md`: the document clears all five required sections (Problem, Goals/Non-Goals, Architecture, Alternatives, Risks) and is better evidenced than most specs. It fails the **Alternatives Rule** in two places (M19, M20) and fails the **Risks & Limits** clause by listing four risks whose mitigations are named-but-unbuilt (M23, M24, M26, M27).

Sections named as meeting the bar:

- The datadir analysis (75, Alternative I) — a genuine invariant, correctly reasoned.
- G2's operational definition of "pristine" (`rev-parse` equality) — falsifiable and cheap.
- Repository-acquisition and sync-model alternatives B, C, D, E, F (563–643) — each carries the measurement that killed it.
- The measurement-correction table (70–88).
- The four-purples / per-site colour finding (429–445) — the strongest evidence work in the document.
- The security section's inherited-versus-introduced distinction (776–785), for the distinction itself, not for the mitigations.
- Non-Goals (135–168) — each states its consequence rather than its absence, which is what makes the leakage auditable.
- Data and configuration model table (416–445) — correct altitude, and it names where the convenient story is false.

---

## Severity disagreements recorded

| Item | Design says | Structural says | Style says | Resolved as |
|---|---|---|---|---|
| 22 vs 23 additive items (811) | — | NIT (E-04) | MAJOR (S2) | **Minor** — a count typo with no argument depending on it |
| 11 vs 16 binaries (800) | — | MINOR (E-02) | MAJOR (S5) | **Minor** — understates asset workload, no argument depends on it |
| OQ 7 numbering (171/205/551) | — | MINOR (X-04) | MAJOR (S6) | **Minor** — trivial fix, but it is the fourth version of the same count |
| Alternative N rejection (M21) | MAJOR | — | — | **Major**, kept: it contradicts a named surface |
| Gate 2 scope (M7) | MAJOR (unbounded labour) | — | MAJOR (undefined unit) | **Major**, merged — same defect, two costs |
| Design M11 (stale PWA) | MAJOR | — | — | **Major**, held pending re-confirmation (truncated twice) |

**Note on tables.** `egm-structural` reports "all five tables structurally well-formed" — that is a statement about markdown integrity. `egm-design` B1 reports that the **register's** file table omits manifests and `__init__.py` — a statement about the register, not about any table in the design document. Both are correct and they are about different artefacts.

---

## Handoff to Stage 8

Stage 8 (Intermediate Zoom Out) should test whether the four Blockers are one root cause. The candidate: **the document specifies intent in prose and never in an executable artefact** — B1's metric, B2's config values, B4's file set and M7's allowlist all fail the same way. If Stage 8 confirms that reading, the repair is a single change to the plan's shape rather than eleven independent edits.

Stage 9 must verify, because Stage 7 could not: every `file:line` citation against `9c58cae5`; the nine-module file count against the register; whether `setup.nsi` really holds 87 of the 94 lines; and whether the six inline-`style`/`<style>` anchors survive upstream churn as the register claims (M19).

**Totals: 4 Blocker · 34 Major · 10 Minor · 27 Nit.**
