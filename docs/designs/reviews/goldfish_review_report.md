# Goldfish Annotated Review Report

**Target:** `docs/designs/castadoo-rebrand-fork.md` (`full file`, 1,449 lines)
**Source of findings:** `consolidated_review_report.md` — 34 consolidated action items (9 Blocker, 14 Major, 11 Nit) deduplicated from 178 raw findings across five review stages.
**Measured against:** Odoo 17.0 @ `9c58cae5d6e3cf91ac1cca7df39fb21f68ca6e15`, sparse checkout at `C:\Users\Yongky\AppData\Local\Temp\opencode\depth17`.
**Author decisions already taken:** Surface 5 (Windows installer) **in scope**; D7 = **Option B (`post_init_hook`)**.

---

## Categorization summary

| Category | Count | Items |
|---|---|---|
| PROPOSE FIX | 27 | A2–A6, A8, A9(partial), B1–B14, C1, C2, C4, C5, C6, C7, C8, C9, C10, C11 |
| CONTEST | 2 | A1(partial), C3 |
| ESCALATE | 4 | A8a, A8b, A8c, A9b |
| DECLINE | 1 | C11(voice counts, partial) |

Two items are split: **A1** is largely decided by your answer and one sub-claim is contested; **A9** splits into a documentary fix (PROPOSE FIX) and a legal judgement (ESCALATE).

Three findings in the consolidated report are **overturned by measurement performed after it was written**. They are recorded here at the top because two of them change what should be done.

---

## Corrections to the consolidated report

### Correction 1 — Item 32 **does** have a real consumer. C3 is wrong.

`addons/website_links/static/src/xml/recent_link.xml:12`:

```xml
<img t-attf-src="http://www.google.com/s2/favicons?domain={{ widget.link_obj.url }}" loading="lazy" alt="Icon"
     onerror="this.src='/website_links/static/img/default_favicon.png'"/>
```

The earlier probe searched `views/` and `i18n/` for the literal string `favicon` and missed it because the reference lives in `static/src/xml/`. Item 32 must **stay in scope** as a binary replacement. Its stated role in the design ("Default link-preview icon") is accurate enough to keep.

### Correction 2 — `email_secondary_color` is a `mail` field, not a base field

`addons/mail/models/res_company.py:33`:

```python
email_secondary_color = fields.Char(
    "Email Button Color", compute="_compute_email_secondary_color",
    readonly=False, store=True)
```

computed at `:83` as `company.secondary_color or '#875A7B'`. `odoo/addons/base/models/res_company.py` defines only `primary_color` and `secondary_color`.

Two consequences the design does not have:

- The data-model table at 425 attributes the field to `res.company` without noting that it **exists only when `mail` is installed**. `castadoo_branding` depends on `web` alone, so a base-tier seed of this field would silently do nothing on a web-only database.
- `readonly=False, store=True` means it **is** writable and therefore seedable — but the seed must live where `mail` is guaranteed, or be guarded.

### Correction 3 — Replacing `favicon.ico` also changes the website default favicon

`addons/website/models/website.py:141`:

```python
def _default_favicon(self):
    with tools.file_open('web/static/img/favicon.ico', 'rb') as f:
        return base64.b64encode(f.read())
```

so item 26's `favicon.ico` replacement reaches `website.favicon`'s default without any deployment step. This narrows A4: `website.favicon` no longer needs to be in the "produced by nothing" set.

---

# 🔴 BLOCKER

### A1. The fork's justification is never stated; Non-Goals exclude the surface that justifies it
[`egm-zoom-out` Stage 8 · `egm-design` Stage 7] — **Severity: Blocker**

*   **Affected Scope:** [165–166](../castadoo-rebrand-fork.md#L165-L166) (Non-Goals), [105–133](../castadoo-rebrand-fork.md#L105-L133) (Goals), [277–279](../castadoo-rebrand-fork.md#L277-L279) (CUJ 5), [344–414](../castadoo-rebrand-fork.md#L344-L414) (Technical Plan)
*   **Discrepancy Description:** Every commitment that makes the document long — the two-branch model, the pristine-mirror goal, D2's merge ritual, the acquisition alternatives, the sync runbook — is load-bearing only for `setup.nsi`, and the Non-Goals state that no installer will be built. CUJ 5 requires building one. The document never says that `setup.nsi` is the reason a fork exists at all.
*   **Rationale:** `setup.nsi` cannot be reached from `addons_path`; every other in-tree file is one, two or four lines. If Surface 5 left scope, the correct artefact is a patch file plus a separate addon repository and roughly a third of the document should be deleted.
*   **AI Suggestion:** **PROPOSE FIX** (your answer to Surface 5 resolves the disagreement in favour of keeping the fork; the missing sentence is still missing).
*   **Justification:** Your decision was "in scope — keep the fork". That closes the governance question and leaves a documentary one: the document still does not say *why* a fork rather than an addon repository, so a future reader cannot evaluate the decision. State the justification and relax the Non-Goal.
*   **Proposed Edit:**
    *   Location: `## Overview`, after line 18.
    *   Change: insert a paragraph — *"The fork exists for one reason: `setup/win32/setup.nsi` is not an addon and cannot be reached from `addons_path`, so branding the Windows installer is impossible without a fork. Every other in-tree file is one, two or four lines. If the installer surface ever leaves scope, the correct shape becomes an addon repository plus a patch file, and the branch model, the sync procedure and Alternatives A–F cease to apply."*
    *   Location: Non-Goals 165–166.
    *   Change: replace "No installer build pipeline… This plan produces a source tree" with *"No installer *pipeline*: the installer is in scope as a source-tree edit to `setup.nsi`, and producing a build is a manual step with preconditions recorded in the runbook. This plan produces a source tree; a release build is out of scope."*

---

### A2. No manifest declares `data` or `assets` — 23 overrides are created and never loaded
[`egm-implementation-readiness` · `egm-codebase-details` · `egm-comprehension`] — **Severity: Blocker**

*   **Affected Scope:** [891–899](../castadoo-rebrand-fork.md#L891-L899) (item 1), [901–905](../castadoo-rebrand-fork.md#L901-L905) (item 2), [987–1119](../castadoo-rebrand-fork.md#L987-L1119) (items 8–22), [950](../castadoo-rebrand-fork.md#L950) (item 6), [1123–1138](../castadoo-rebrand-fork.md#L1123-L1138) (items 23–25)
*   **Discrepancy Description:** Item 1 and all eight overlay manifests specify `name`, `depends`, `auto_install`, `license`, `author`, `application` — and stop. Item 7 proves the plan knows the manifest is where load behaviour is declared. Consequences: 14 XML view files are never parsed; `castadoo_user_menu.js` is never bundled; the two Owl `t-inherit` files never compile. Item 2 imports `models`, which no item creates, raising `ImportError` at module load; and eight overlay directories get no `__init__.py`.
*   **Rationale:** This is the exact failure class the design's thesis exists to prevent — a clean, correctly-built tree that renders unbranded Odoo with no error. Gate 1 counts the files as present; Gate 2 greps them as branded; nothing loads them.
*   **AI Suggestion:** **PROPOSE FIX**
*   **Justification:** Mechanical and confirmed against the tree. `addons/account_payment/__manifest__.py` shows `'auto_install': ['account']` immediately followed by `'data': [...]`, so the missing key is an omission, not a convention. Item 1's `application: False` and `license: 'LGPL-3'` are correct for 17.0, which makes the absence of `data` conspicuous.
*   **Proposed Edit:**
    *   Location: item 1, after line 896.
    *   Change: add to the manifest — `'data': ['views/webclient_templates.xml', 'views/report_templates.xml', 'views/offline_templates.xml', 'data/ir_config_parameter.xml']`; `'assets': {'web.assets_backend': ['castadoo_branding/static/src/user_menu/castadoo_user_menu.js']}`.
    *   Location: each overlay manifest (items 8, 10, 12, 14, 16, 18, 20, 22).
    *   Change: add `'data': ['views/<name>.xml']`
    *   Location: items 23–25.
    *   Change: add `'assets': {'point_of_sale.assets_prod': [...]}` — **measured**: 17.0 declares `point_of_sale.assets_prod` and `point_of_sale.assets_qunit_tests`; a bare `point_of_sale.assets` key does not exist in the tree. Also add `'assets'` entries to items 23/24 for the Owl files.
    *   Location: item 2, lines 903–905.
    *   Change: replace with `from . import hooks` (unconditional under D7-B) and delete the `models` clause. Insert a new item covering the eight overlay `__init__.py` files.

---

### A3. Gate 1 cannot pass on the tree the plan describes
[`egm-design` · `egm-comprehension` · `egm-implementation-readiness` · `egm-zoom-out`] — **Severity: Blocker**

*   **Affected Scope:** [119–122](../castadoo-rebrand-fork.md#L119-L122) (G5), [495–499](../castadoo-rebrand-fork.md#L495-L499) (Gate 1), [1351–1364](../castadoo-rebrand-fork.md#L1351-L1364) (item 46), [1413–1443](../castadoo-rebrand-fork.md#L1413-L1443) (footnote)
*   **Discrepancy Description:** Three independent arithmetic failures. `git diff --stat` counts added files, so "≤ 37 files" fails on the first push of ~28 new files. It counts a one-line replacement as `+1/-1`, so 94 edit lines appear as ~188. And the register is a coverage list, not a diff list — it counts 13 upstream view files the plan only *inherits*, which never differ. Items 43–47 additionally change `README.md`, `CONTRIBUTING.md`, `docs/`, `.github/`, none of which the register lists.
*   **Rationale:** An implementer wiring item 46 literally ships a gate that fails on its own first commit.
*   **AI Suggestion:** **PROPOSE FIX**
*   **Justification:** Confirmed by measurement and by the footnote's own three disagreeing totals (54 / 49 / 37). The repair is a metric definition plus a derivation, not a recount.
*   **Proposed Edit:**
    *   Location: Gate 1, 495–499.
    *   Change: `git diff --stat --diff-filter=M upstream/17.0...HEAD -- $(upstream paths from the manifest)`; state the unit as **changed upstream paths**, and state that added files are excluded by construction.
    *   Location: G5, 119–122.
    *   Change: restate as *"≤ 37 **upstream** paths modified, ≤ 103 **edited** lines (94 + the 9 in items 39–40), with additive files reported separately and not counted."* See A5 for the metric change.

---

### A4. The configuration tier is assigned to "deployment" and produced by no item; neither gate can see a database
[`egm-design` · `egm-comprehension` · `egm-zoom-out` · `egm-implementation-readiness`] — **Severity: Blocker**

*   **Affected Scope:** [332–334](../castadoo-rebrand-fork.md#L332-L334), [416–451](../castadoo-rebrand-fork.md#L416-L451), [211–222](../castadoo-rebrand-fork.md#L211-L222) (CUJ 1), [254–266](../castadoo-rebrand-fork.md#L254-L266) (CUJ 4), [1247](../castadoo-rebrand-fork.md#L1247) (item 37), [1386–1391](../castadoo-rebrand-fork.md#L1386-L1391) (verification)
*   **Discrepancy Description:** `res.company.name`, `.logo`, `.email_secondary_color`, `web.web_app_name` and `website.favicon` are all "Set by: deployment". No item produces them. Gate 2 greps the tree; Gate 1 diffs paths. A branded tree on a fresh database yields a blank logo, `name` = "YourCompany", `web_app_name` unset (**stock fallback `'Odoo'`**, measured exact at `webmanifest.py:48`) and `email_secondary_color` unset.
*   **Rationale:** CUJ 1's login assertion still passes on the inherited footer alone, so the gate checks something the plan never produces. The design concedes this only in Future Improvements (867–870).
*   **AI Suggestion:** **PROPOSE FIX**
*   **Justification:** Two of the five are genuinely deployment data (`res.company.name`, `.logo`, which need an uploaded binary). The other three are shippable as `noupdate="1"` module data and that is strictly cheaper than a deployment step. Measured caveat: `email_secondary_color` is a `mail` field (`mail/models/res_company.py:33`), so its seed must sit where `mail` is installed or be guarded; and `website.favicon`'s default already comes from `web/static/img/favicon.ico` (`website.py:141`), so item 26 covers it and only an explicit override needs data.
*   **Proposed Edit:**
    *   Location: new item in Tier 1, `castadoo/castadoo_branding/data/ir_config_parameter.xml` (Create).
    *   Change: `<data noupdate="1"><record id="web_app_name" model="ir.config_parameter" forcecreate="0"><field name="key">web.web_app_name</field><field name="value">CASTADOO</field></record></data>` — the `forcecreate="0"` idiom is stock (`addons/account_payment/data/ir_config_parameter.xml:4`).
    *   Location: data-model table 421–427.
    *   Change: change the `web.web_app_name` row's Set by to "module data (noupdate=1)"; add a note to the `email_secondary_color` row that the field is defined in `mail`, not `base`; change `website.favicon`'s note to record that item 26 supplies the default through `website.py:141`.
    *   Location: verification plan.
    *   Change: add a third tier — post-deploy rendered assertions — see B14.

---

### A5. The budget measures count, and the register's own analysis says count is the wrong metric
[`egm-zoom-out` Stage 8] — **Severity: Blocker**

*   **Affected Scope:** [119–122](../castadoo-rebrand-fork.md#L119-L122) (G5), [58–61](../castadoo-rebrand-fork.md#L58-L61), `change_register.md` 351–357
*   **Discrepancy Description:** The register argues that `setup.nsi`'s 87 lines are 86% of the in-place volume *by count* but a leaf file upstream touches once or twice a year, while `webmanifest.py` is 2 lines upstream touches most years — "ranking by count would put the effort in the wrong place". Three lines later the design adopts count as Goal G5, as Gate 1, as the effort estimate and as the difficulty narrative.
*   **Rationale:** The document's best paragraph contradicts its headline goal, and the goal won. This is not a definition error (Stage 7's diagnosis) but a choice of quantity.
*   **AI Suggestion:** **PROPOSE FIX**
*   **Justification:** Confirmed: no earlier stage caught it, and it is the only finding that changes what the goal *measures* rather than how it is counted.
*   **Proposed Edit:**
    *   Location: G5, 119–122.
    *   Change: restate as *"The overlay is bounded on two axes, and the second is the one that predicts cost: (a) ≤ 37 upstream paths modified, ≤ 103 edited lines — volume; (b) ≤ 6 upstream paths whose last-N-point-release churn overlaps the edited lines — conflict exposure. `setup.nsi` is reported as high volume, low rate; `webmanifest.py` as low volume, high rate."*
    *   Location: 58–61.
    *   Change: replace "difficulty is concentrated in one file" with the volume-versus-rate framing.

---

### A6. Four items instruct code shapes the tree does not contain
[`egm-implementation-readiness` · orchestrator measurement] — **Severity: Blocker**

*   **Affected Scope:** [911](../castadoo-rebrand-fork.md#L911) (item 3), [1016–1026](../castadoo-rebrand-fork.md#L1016-L1026) (item 11), [1063–1073](../castadoo-rebrand-fork.md#L1063-L1073) (item 17), [1081–1098](../castadoo-rebrand-fork.md#L1081-L1098) (item 19), [1133–1138](../castadoo-rebrand-fork.md#L1133-L1138) (item 24)
*   **Discrepancy Description:** All five measured.
    *   Item 3: `inherit_id="web.web_layout"`. `webclient_templates.xml:17` declares `id="layout"`, so the external id is **`web.layout`**. Doubling the prefix raises `External ID not found` at install, and the register (S1.01) already says `web.layout`.
    *   Item 11: "four occurrences … a **single** inheritance edit". `reset_password_email` (`:3`) carries `:36`/`:81`; `alert_login_new_device` (`:88`) carries `:122`/`:143`. Four sites, **two** `inherit_id`s — one xpath cannot span them.
    *   Item 17: "one inherited record on `hr_expense_template_register_no_user`", then requires the button at `:31`. Measured: `:49` is in `..._no_user` (`:35`); **`:31` is in `hr_expense_template_register` (`:11`)** — a different template, and **absent from the register** (S4.06 lists only `:49`), so Gate 1 would pass a tree still carrying `#9E588B`.
    *   Item 19: "`digest_mail_main` (270–447)" citing `:14`/`:147`. Measured: `digest_mail_main` is at `:270` (ends 451); **`:14`, `:58`, `:87`, `:147` are all inside `digest_mail_layout` (`:5`)**.
    *   Item 24: never states the parent `t-name`, in an item whose own text warns a wrong name fails silently. `:84` sits inside `point_of_sale.CustomerFacingDisplayOrder` (`:43`).
*   **Rationale:** Each is either an install-time hard failure or a silent no-op. Item 19's *conclusion* is correct (`email_secondary_color` genuinely drives the digest); only its anchors are wrong.
*   **AI Suggestion:** **PROPOSE FIX**
*   **Justification:** Measured, not inferred. The other nine `inherit_id` parents are correct, so this is five targeted corrections rather than a taxonomy rewrite.
*   **Proposed Edit:**
    *   Location: 911. Change: `web.web_layout` → **`web.layout`**.
    *   Location: 1019–1026. Change: replace "single inheritance edit" with *"four anchors across two templates: `reset_password_email` (`auth_signup_templates_email.xml:3`) at `:36` and `:81`; `alert_login_new_device` (`:88`) at `:122` and `:143`. Two inherited records minimum, four if button and footer are anchored separately."*
    *   Location: 1066–1073. Change: *"two inherited records: `hr_expense_template_register` (`:11`) for the `#9E588B` button at `:31`, and `hr_expense_template_register_no_user` (`:35`) for the footer at `:49`."* Add `:31` to register S4.06.
    *   Location: 1085–1098. Change: `digest_mail_main` (270–451) → the colour machinery is in **`digest_mail_layout` (`:5`)** at `:14`, `:58`, `:87`, `:147`; the two footers are in `digest_mail_main` at `:398`/`:436`. Two parents, not one.
    *   Location: 1133–1138. Change: state parent `point_of_sale.CustomerFacingDisplayOrder` (`:43`) explicitly.

---

### A7. D7 is undecided in the document while the plan claims to work under any answer
[`egm-design` · `egm-comprehension` · `egm-implementation-readiness` · `egm-zoom-out`] — **Severity: Blocker**

*   **Affected Scope:** [400–414](../castadoo-rebrand-fork.md#L400-L414) (D7), [205–207](../castadoo-rebrand-fork.md#L205-L207), [891–905](../castadoo-rebrand-fork.md#L891-L905), [968–978](../castadoo-rebrand-fork.md#L968-L978) (item 7), [1336–1342](../castadoo-rebrand-fork.md#L1336-L1342) (item 44), `change_register.md:416`
*   **Discrepancy Description:** "Needs an answer before the Detailed Implementation Plan can be executed" and "written so that any of the three can be applied to the same file set" cannot both hold. Option C deletes items 8–24; Option B adds item 7; Option A removes item 7 and item 2's import. Three options, three file sets. D7 also has no row in the register's decision sheet, which ends at D6, while Gate 1 checks the diff against that register.
*   **Rationale:** A spec that admits any of three answers does not specify a file set.
*   **AI Suggestion:** **PROPOSE FIX**
*   **Justification:** You chose Option B. That settles the decision; the document must now record it as taken rather than open, and the register must carry it.
*   **Proposed Edit:**
    *   Location: 400–414.
    *   Change: retitle to *"D7 — Overlay activation: decided. Option B (`post_init_hook`)."* Delete the three-option table's open framing, keep it as the record of alternatives considered, and move the disclaimer sentence (412) into the options table as the reason the other two were rejected.
    *   Location: item 7, 968–978.
    *   Change: supply the concrete shape —
        ```python
        # castadoo/castadoo_branding/hooks.py
        from odoo import api, SUPERUSER_ID
        _OVERLAYS = ('castadoo_branding_mail', 'castadoo_branding_portal', ...)
        def post_init_hook(env):
            ...
        ```
        **Measured:** 17.0 calls `getattr(py_module, post_init)(env)` (`odoo/modules/loading.py:245`) — the signature takes `env`, not `cr, registry`. Record the registry-reload hazard: install via `button_immediate_install` goes through `_button_immediate_function` (`odoo/addons/base/models/ir_module.py:590`), which refuses to run on an init registry and forbids test-time module operations; the safe path is `odoo-bin -i castadoo_branding` and `-u castadoo_branding` from the CLI, and the hook must be idempotent across both.
    *   Location: item 1, 894–899. Change: add `'post_init_hook': 'post_init_hook'`.
    *   Location: item 2. Change: `from . import hooks` unconditionally; no `models`.
    *   Location: `change_register.md`, decision sheet. Change: add a D7 row.

---

### A8. Every security control lives in a document the plan does not produce
[`egm-design`] — **Severity: Blocker**

*   **Affected Scope:** [776–790](../castadoo-rebrand-fork.md#L776-L790), [405](../castadoo-rebrand-fork.md#L405), [547](../castadoo-rebrand-fork.md#L547), [782](../castadoo-rebrand-fork.md#L782), [1304–1322](../castadoo-rebrand-fork.md#L1304-L1322), [1408–1411](../castadoo-rebrand-fork.md#L1408-L1411)
*   **Discrepancy Description:** Phone-home is parked on Open Question 2 with no default, and three parts of the document give it three incompatible dispositions (item 41 source edit; OQ2 says a conf line; item 42 says `odoo.conf` is "**Not** modified in the repo"). `list_db`/`admin_passwd` are deferred to "the runbook", cited six times and created by no item. `DEFAULT_POSTGRESQL_PASSWORD 'openpgpwd'` (**measured exact at `setup.nsi:87`**, the only instance in the tree) ships in a product installer. Bus factor is one and the answer is documentation. "No credential… is touched" is contradicted by the next sentence.
*   **Rationale:** Both risks are correctly labelled inherited, but both mitigations are named and unbuilt, and neither gate can see either.
*   **AI Suggestion:** **PROPOSE FIX** for the deliverable and the wording; **ESCALATE** for the four decisions below.
*   **Justification:** A deployment checklist is a document I can specify and add to the plan. The *content* of three of its controls is a decision about your deployment, and the fourth is a legal judgement. I fix the former and escalate the latter rather than inventing a platform.
*   **Proposed Edit:**
    *   Location: after [533](../castadoo-rebrand-fork.md#L533).
    *   Change: add **`### Deployment checklist (a third deliverable)`** listing: forced `admin_passwd`, `list_db = False`, `proxy_mode` behind TLS, phone-home setting, database backup location, and the `-u castadoo_branding` convention. State that it ships as `docs/deployment-checklist.md` and is a plan deliverable, not a runbook footnote.
    *   Location: 786–790.
    *   Change: calibrate "No credential, key or token is touched by any file in this plan" → *"No credential **value** is modified by any file in this plan"*.
    *   Location: 776–785, the installer password.
    *   Change: record it as an accepted risk with the mitigation named (forced password on first run), and delete "would break existing installs" — this fork's install base is new installs by definition (CUJ 5 validates a clean VM).
    *   Location: 1408–1411. Change: mark the sync rehearsal as blocked on OQ1 rather than conditional, so the readiness gate can report it.

---

### A9. The LGPL claim is asserted, not cited; licence and trademark are conflated
[`egm-design` · `egm-style`] — **Severity: Blocker**

*   **Affected Scope:** [49–52](../castadoo-rebrand-fork.md#L49-L52), [126–128](../castadoo-rebrand-fork.md#L126-L128) (G7), [151–152](../castadoo-rebrand-fork.md#L151-L152), [523–524](../castadoo-rebrand-fork.md#L523-L524), [720–723](../castadoo-rebrand-fork.md#L720-L723), [846](../castadoo-rebrand-fork.md#L846), [1224](../castadoo-rebrand-fork.md#L1224) (item 35)
*   **Discrepancy Description:** "LGPL-3 permits this. It does not permit the fork to *claim* to be Odoo" mixes two legal frames. LGPL grants no trademark rights, and the deliverable puts CASTADOO — a mark containing Odoo's — on publisher fields and login pages with no confusion analysis. G7 calls the dating obligation "structural, not documentary" while step 6 dates only merge commits, so an overlay commit between syncs has no dating mechanism, and the new files' licence headers are never stated.
*   **Rationale:** Two later passages (151–152, 720–723) treat the same question as settled differently.
*   **AI Suggestion:** **PROPOSE FIX** (documentary defects) + **ESCALATE** (the legal posture).
*   **Justification:** The measurable/drafting defects I can fix: the author value, the missing headers, the "structural" overstatement. Whether the design should assert LGPL reliance, and whether CASTADOO's use of Odoo's mark has been reviewed, is not something I can establish from any file.
*   **Proposed Edit:**
    *   Location: 49–52.
    *   Change: replace "LGPL-3 permits this. It does not permit the fork to claim to be Odoo" with *"The licence permits modification and redistribution. It grants no trademark rights. Presenting CASTADOO as the product name is a branding decision recorded here; whether it engages Odoo's mark is a legal question flagged in Risks and not resolved by this design."*
    *   Location: G7, 126–128.
    *   Change: delete "structural, not documentary"; state that dating is carried on merge commits and on the new files' headers, and that overlay commits between syncs are dated by their own commit message.
    *   Location: new item or item 1.
    *   Change: state the header for all new files — `# Part of CASTADOO. Original: Odoo 17.0. Licensed under LGPL-3.` and note the `odoo/` tree keeps its original headers untouched.
    *   Location: item 35, 1224.
    *   Change: **measured** — `release.py:33` is `author = 'OpenERP S.A.'`, **not** `Odoo S.A.`. Rewrite the rationale: the field is frozen at its tree value `OpenERP S.A.` because `config.py:50` derives the datadir from `release.product_name` + `release.author` (measured exact), so changing either relocates the datadir. Supply the replacement string for `description` (`'Odoo Server'` → `'CASTADOO Server'`), which the item currently omits entirely.

---

# 🟠 MAJOR

### B1. One declarative change manifest should replace the register, the budget, the allowlist and the file table
[`egm-zoom-out` Stage 8] — **Severity: Major**

*   **Affected Scope:** [344–374](../castadoo-rebrand-fork.md#L344-L374), [495–513](../castadoo-rebrand-fork.md#L495-L513), [1351–1364](../castadoo-rebrand-fork.md#L1351-L1364), [1413–1443](../castadoo-rebrand-fork.md#L1413-L1443)
*   **Discrepancy Description:** Four revisions produced four fresh crops of count contradictions. Every load-bearing quantity is a hand-computed number typed into prose and nothing recomputes it.
*   **Rationale:** ~80 rows in `castadoo/change_manifest.toml` with `[[change]]`, `[[setting]]`, `[[assertion]]`, `[[allowlist]]`. The register becomes a rendering; Gate 1 diffs against `[[change]]`; Gate 2 against `[[allowlist]]`; the footnote table becomes a `GROUP BY`.
*   **AI Suggestion:** **PROPOSE FIX**
*   **Justification:** The cheapest component in a plan priced at ≈17 h, and it reopens no decision. It makes A3, A5 and every count finding unexpressible rather than fixed.
*   **Proposed Edit:**
    *   Location: new subsection after [513](../castadoo-rebrand-fork.md#L513).
    *   Change: specify the manifest schema (four record types with the fields named above) and state that `change_register.md` and the footnote table are *derived views*, generated by `castadoo/tools/render_manifest.py`. Retitle 1413–1443 "Derived view — do not hand-edit".

---

### B2. The five-tier ordinal should be replaced by four boolean columns
[`egm-zoom-out` Stage 8 · `egm-comprehension`] — **Severity: Major**

*   **Affected Scope:** [889](../castadoo-rebrand-fork.md#L889), [1149–1165](../castadoo-rebrand-fork.md#L1149-L1165), [1313–1322](../castadoo-rebrand-fork.md#L1313-L1322)
*   **Discrepancy Description:** `Tier` is one ordinal scale pretending to answer four orthogonal questions: recurring conflict surface, reversible by uninstall, counted by budget, upstream-owned. Item 26 sits under Tier 1 while being six upstream blob overwrites; item 42 sits under "the only files with recurring conflict surface" while being "**Not** modified in the repo". That is why 20 files produce "4 irreversible", "16 binaries", "11 committed binaries" and "17 images".
*   **Rationale:** Not four arithmetic slips — one relation answering four questions.
*   **AI Suggestion:** **PROPOSE FIX**
*   **Justification:** With four booleans, "20 files, not 4" is a `WHERE` clause. This is the structural half of B1.
*   **Proposed Edit:**
    *   Location: 1165 heading and 1149–1163.
    *   Change: move item 26 out of Tier 1 into the binary group; replace the Tier vocabulary with `conflict_surface`, `reversible_by_uninstall`, `counts_against_budget`, `upstream_owned` columns in the manifest, and state that the Tier headings are a *rendering* of those columns.

---

### B3. Gate 2's allowlist is unbounded and its patterns exist nowhere
[`egm-design` · `egm-comprehension` · orchestration measurement] — **Severity: Major**

*   **Affected Scope:** [486–513](../castadoo-rebrand-fork.md#L486-L513), [129–131](../castadoo-rebrand-fork.md#L129-L131) (G8), [1351–1364](../castadoo-rebrand-fork.md#L1351-L1364)
*   **Discrepancy Description:** 1,343 residual hits plus 5,496 mandated headers and 18,920 `.po` files. "grep for the enumerated patterns" — no pattern list exists in the document or the register. No path scoping, no `.po` exclusion, no ceiling, no owner. Measured scale: `git grep -l "Powered by Odoo"` returns **52 files**, against a table scoped to 13; `"Sent by"` returns **180**.
*   **Rationale:** The design predicts its own failure ("otherwise it fills with noise and gets disabled", 509–510).
*   **AI Suggestion:** **PROPOSE FIX**
*   **Justification:** Two tiers, not a swap: a path-scoped exact match over the register plus a coarse whole-tree pattern set, with the rendered-output assertions as the long-term control.
*   **Proposed Edit:**
    *   Location: 500–505.
    *   Change: replace Gate 2's block with two sub-gates: **2a — pathlint**: for each `[[change]]` path, grep for `Odoo` and fail on any hit not in `[[allowlist]]`; ceiling stated as "every hit in a register path must be allowlisted, and the allowlist may not exceed 40 entries". **2b — treelint**: coarse patterns only (`Powered by Odoo`, `www.odoo.com` in non-`i18n`, non-`demo` paths), with `.po` and `demo/` excluded by glob and the exclusion rule written in the document.

---

### B4. The binary/replacement model is wrong in three ways
[`egm-zoom-out` Stage 5 · `egm-design` · `egm-implementation-readiness`] — **Severity: Major**

*   **Affected Scope:** [336](../castadoo-rebrand-fork.md#L336), [811–817](../castadoo-rebrand-fork.md#L811-L817), [1165–1190](../castadoo-rebrand-fork.md#L1165-L1190)
*   **Discrepancy Description:** "Conflict surface: none — git sees a new blob, not a hunk" is false: both sides modifying one binary path yields `CONFLICT (content)` with no hunk resolution. Three of the 16 are **text**: `odoo_logo.svg`, `odoo_logo_dark.svg`, `odoo-icon.svg` are XML and will be diffed line-by-line. The rollback clause collapses additive and replaced — uninstalling restores the ~25 addon files and nothing for the 16 overwritten blobs.
*   **Rationale:** "Take ours" silently discards upstream fixes while looking identical in review.
*   **AI Suggestion:** **PROPOSE FIX**
*   **Justification:** Measured: both `odoo_logo*.svg` are 1,581 B with **different SHA256**, so they are distinct files; and XML is text to git.
*   **Proposed Edit:**
    *   Location: 336.
    *   Change: *"Conflict surface for rank 3: whole-file `CONFLICT (content)` when upstream touches the same path — resolved by taking the fork's blob, which discards the upstream change, so the diff must be reviewed."*
    *   Location: 811–817.
    *   Change: split the rollback claim three ways (additive / replaced-binary / edited) and state the non-reversible set as **20**, not 4.
    *   Location: Tier 3 preamble, 1165–1169.
    *   Change: add that the three SVGs are text and reclassify them as `modify-text` in the manifest; add `.gitattributes` with `merge=ours` scoped to the 13 true binaries.

---

### B5. "Cheap to sync" measures the smaller of two costs, and "Rollout and rollback" contains no rollout
[`egm-zoom-out` Stage 8 · `egm-design`] — **Severity: Major**

*   **Affected Scope:** [119–122](../castadoo-rebrand-fork.md#L119-L122), [515–531](../castadoo-rebrand-fork.md#L515-L531), [809–825](../castadoo-rebrand-fork.md#L809-L825)
*   **Discrepancy Description:** The thesis counts merge cost and omits recurring human cost: re-applying 87 lines after take-upstream, manual POS receipt print, manual email-client check, manual PWA install on two devices, asset recompile, and a `-u castadoo_branding` per sync under D7-B. The rollout section describes only rollback; an existing stock database moving to branded has no path.
*   **Rationale:** Plausibly 1–2 hours per point release against a merge cost near zero, so the goal is unproven rather than established.
*   **AI Suggestion:** **PROPOSE FIX**
*   **Justification:** Now more pointed, because D7-B adds a per-sync `-u` step the plan does not count.
*   **Proposed Edit:**
    *   Location: 809–825.
    *   Change: add a "Rollout" subsection at the specificity of the sync procedure: install module → `-u castadoo_branding` (D7-B) → asset recompile → five config values (or verify the seeded three) → service-worker invalidation → visual check.
    *   Location: G5.
    *   Change: restate in amortised terms — merge cost *plus* the manual verification set, quoted per sync.

---

### B6. Two decisions are priced to the hour; the two that change the shape are unpriced
[`egm-zoom-out` Stage 8 · `egm-design`] — **Severity: Major**

*   **Affected Scope:** `change_register.md` 348–349, [165–166](../castadoo-rebrand-fork.md#L165-L166), [885–887](../castadoo-rebrand-fork.md#L885-L887)
*   **Discrepancy Description:** D1-C vs D1-A is priced 37/94/≈17 h against 43/101/≈19 h; D7 and Surface 5 are unpriced. And those two hours sit inside a ≈17 h figure the register documents as excluding the four largest components.
*   **Rationale:** The only quantified decision in the design is quantified inside a number the design admits is wrong by an unknown factor.
*   **AI Suggestion:** **PROPOSE FIX**
*   **Justification:** Both decisions are now taken, so the fix is to price them and attach the exclusions to the headline.
*   **Proposed Edit:**
    *   Location: register 348–349.
    *   Change: *"≈17 h = 47 items only. Excludes: asset design, this register, both CI gates, the deployment checklist, all deployment work. Surface 5 adds the `setup.nsi` work (87 lines) plus a build-and-test capability; D7-B adds `hooks.py`, the install-convention step and a per-sync `-u`."*

---

### B7. A false framing claim, three unranked superlatives, and an uncontrolled status vocabulary
[`egm-implementation-readiness` · `egm-style`] — **Severity: Major**

*   **Affected Scope:** [878–879](../castadoo-rebrand-fork.md#L878-L879), [932](../castadoo-rebrand-fork.md#L932), [1006](../castadoo-rebrand-fork.md#L1006), [1229](../castadoo-rebrand-fork.md#L1229), headings passim
*   **Discrepancy Description:** "The pseudocode and shapes are what the implementer needs to make no further decisions" — there is **no pseudocode anywhere in 874–1449**, and at least eleven items hand a decision back. Eight status qualifiers in headings with no controlled vocabulary; "optional" floats between required and absent.
*   **Rationale:** A work order that opens by asserting it contains no open decisions trains the reader to stop looking for them.
*   **AI Suggestion:** **PROPOSE FIX**
*   **Justification:** Confirmed by inspection. I am also replacing the framing with real pseudocode for the hook (A7), so the claim becomes true rather than deleted.
*   **Proposed Edit:**
    *   Location: 878–879.
    *   Change: *"Each item states its action, its file, its content and its gate. The hook in item 7 is given as code; other items give the literals to write. Where an item says 'the implementer must choose', that is recorded as an open decision and counted in §Open Decisions."*
    *   Location: all DIP headings.
    *   Change: two fields — **Action** (Create / Modify / None) and **Gate** (none / D7 / OQ2). Drop "optional" as a status and mark genuinely optional files in a separate short list.
    *   Location: 932, 1006, 1229. Change: delete "the most fragile item in the whole register", "the single highest-value change", "the single most important non-change"; keep the accompanying reasons.

---

### B8. Three sections answer "may a clone duration be quoted?" three ways
[`egm-style` · `egm-comprehension`] — **Severity: Major**

*   **Affected Scope:** [123–125](../castadoo-rebrand-fork.md#L123-L125) (G6), [190–193](../castadoo-rebrand-fork.md#L190-L193) (OQ4), [799](../castadoo-rebrand-fork.md#L799) (NFR)
*   **Discrepancy Description:** G6 says "clone in minutes rather than hours"; OQ4 says the two bandwidth measurements disagree by ~34×; NFR says "so no duration is quoted."
*   **Rationale:** The document contradicts itself on whether it may quote a duration, then quotes one.
*   **AI Suggestion:** **PROPOSE FIX**
*   **Justification:** One of the three is a measurement (444 MB); the duration is not.
*   **Proposed Edit:**
    *   Location: G6, 123–125.
    *   Change: calibrate to size only — *"under 500 MB (measured 444 MB). Clone **duration** is not asserted; see Open Question 4."*

---

### B9. The measurement chain cannot be reconstructed
[`egm-style` · `egm-comprehension`] — **Severity: Major**

*   **Affected Scope:** [83–88](../castadoo-rebrand-fork.md#L83-L88), [146–148](../castadoo-rebrand-fork.md#L146-L148), [728–739](../castadoo-rebrand-fork.md#L728-L739)
*   **Discrepancy Description:** "26,560 **files** contain `Odoo`; 5,496 of the matching **lines** are the notice; 18,920 are translation files. Of the remaining 1,343 hits…" — the 8,985 step is missing. 26,560 − 5,496 − 18,920 = **2,144**, not 1,343. Non-Goals treats 18,920 as a *file* count while Alternative M says "3,410 `.po` files".
*   **Rationale:** A derived number that cannot be reconstructed cannot be checked.
*   **AI Suggestion:** **PROPOSE FIX**
*   **Justification:** One unit per term restores the chain; the register is the source of truth either way.
*   **Proposed Edit:**
    *   Location: 83–88.
    *   Change: rewrite with one unit per term and show every subtraction, or delete 1,343 and cite the register's per-line enumeration.

---

### B10. Non-viable alternatives, one rejected on a false ground
[`egm-design` · `egm-style`] — **Severity: Major**

*   **Affected Scope:** [647–657](../castadoo-rebrand-fork.md#L647-L657) (G), [687–698](../castadoo-rebrand-fork.md#L687-L698) (J), [728–752](../castadoo-rebrand-fork.md#L728-L752) (M, N), [556–765](../castadoo-rebrand-fork.md#L556-L765)
*   **Discrepancy Description:** **J** rests on an unmeasured precedence claim: `!default` yields only to an *earlier* definition and does not block a plain assignment in a later-loaded file; its second half ("not one of the six surfaces") is circular because G4 lists the backend shell as in-scope. **G** discredits its own "290" figure two sentences later, and the real competitor (in-place edit of ~30 rendered files) is never compared. **N** is rejected as "staff-facing" although 154–156 names portal-invitation and account-created as customer first-contact mail. **M** is "rejected provisionally" — deferred, not rejected. Three genuinely viable options are absent: a separate branding repository; not forking at all; deferring Surface 5.
*   **Rationale:** The standard requires rejected alternatives, not deferred ones, and the reasons must survive their own Cons.
*   **AI Suggestion:** **PROPOSE FIX**
*   **Justification:** Your Surface 5 answer settles which missing option matters: "defer the installer" must be recorded as *rejected by decision*, not absent. J's mechanism claim is wrong as SCSS semantics and the document's own methodology (82–88) demands it be measured.
*   **Proposed Edit:**
    *   Location: J, 687–698. Change: replace the precedence claim with *"a new file in a branding module's asset bundle is mechanism 2, not 4. J was rejected on scope: the backend palette is not one of the six surfaces, and adding a palette dependency to reach it costs more than the surface is worth."* Delete the circular second half.
    *   Location: G, heading 647. Change: retitle to "Edit the rendered files in place"; delete "290"; add INH-anchor churn versus EDIT-line churn as the comparison.
    *   Location: N, 741–752. Change: reject on the register's ground — seven watched records for one footer line.
    *   Location: M, 728–739. Change: convert the provisional rejection into a recorded decision (`.po` out of scope for 17.0; `msgstr` overlay is the sanctioned route if it returns).
    *   Location: after O. Change: add **Alternative P — a separate branding repository on `addons_path`**, rejected because `setup.nsi` cannot be reached from `addons_path` (see A1), and **Alternative Q — defer Surface 5**, rejected by your decision, with the consequence recorded: the fork would lose its only justification.

---

### B11. D1-C compares the wrong mechanism
[`egm-zoom-out` Stage 5 · `egm-implementation-readiness`] — **Severity: Major**

*   **Affected Scope:** [153–156](../castadoo-rebrand-fork.md#L153-L156), [700–712](../castadoo-rebrand-fork.md#L700-L712), [854–858](../castadoo-rebrand-fork.md#L854-L858), [425](../castadoo-rebrand-fork.md#L425)
*   **Discrepancy Description:** Alternative K evaluates a `post_init` hook that mutates `body_html` in place — the rollback-hazard variant — and rejects the middle path on that basis. Odoo's extension point is the model layer: subclass `mail.template`, override `_render_template()`, post-process at render time. No data record, no `noupdate` row, no migration, gone on uninstall.
*   **Rationale:** The document rejects *one implementation* of the middle path and calls it the middle path.
*   **AI Suggestion:** **PROPOSE FIX**
*   **Justification:** Measured support: `auth_signup/data/mail_template_data.xml:3` is `<data noupdate="1">` containing all three templates, so D1-C's premise is real. The render-time route is a genuine alternative that was never priced. **Note:** the new colour finding (Correction 2) means `email_secondary_color` cannot be a base-tier seed, which makes the render-time route *more* attractive than the review assumed.
*   **Proposed Edit:**
    *   Location: 700–712.
    *   Change: restate K as "mutate `body_html` in place" and add **K2 — render-time post-processing via `mail.template._render_template`**, with its cost (one small `models/` package in a `mail`-depending overlay) and its benefit (fully reversible, no `noupdate` interaction).
    *   Location: 854–858.
    *   Change: record that D1-C stands *until* K2 is priced; the Future Improvements entry should point at K2, not at a datadir rewrite.

---

### B12. Items 38, 39 and 40 are wrong on their own counts, and item 38 is not implementable
[`egm-implementation-readiness` · `egm-style` · measurement] — **Severity: Major**

*   **Affected Scope:** [1253–1283](../castadoo-rebrand-fork.md#L1253-L1283) (item 38), [1285–1294](../castadoo-rebrand-fork.md#L1285-L1294) (item 39), [1296–1302](../castadoo-rebrand-fork.md#L1296-L1302) (item 40)
*   **Discrepancy Description:**
    *   **Item 38:** "87 replacements", six named, **81 unnamed**; measured: file is **729 lines**, **89 lines contain `Odoo`**, **114 occurrences**, 119 any-case. 87 is reproducible as none of those, and is used as three units. The French block is 31 `LANG_FRENCH` lines needing *translation*, not substitution. Lines 134–139 are pixmap **paths**, not strings.
    *   **Item 39:** "8 occurrences, two must not change" then enumerates **nine**; measured **9**. Real split: **1** user-visible (`:323` `Odoo Bot <info@odoo.com>`), the rest internal identifiers.
    *   **Item 40:** "Keep the LGPL-3 text verbatim. Add the CASTASOFT copyright line" — mutually exclusive. Path is `setup/win32/static/doc/License.rtf` (design omits `static/doc/`); **2** `Odoo` occurrences, not 1.
*   **Rationale:** An implementer cannot execute any of the three, and a blanket replace on item 38 breaks the installer's image references.
*   **AI Suggestion:** **PROPOSE FIX**
*   **Justification:** All measured. Item 38 is the largest single block of work in the plan and is specified only by a count that does not exist.
*   **Proposed Edit:**
    *   Location: item 38.
    *   Change: replace the count with the register's per-line enumeration. State the measured baseline: *"729 lines; 89 contain `Odoo`; 114 occurrences. The `!define` block (`:44`, `:67`, `:74`, `:80`, `:160`) carries six. `:134–139` are pixmap paths and must **not** be replaced — item 33 preserves the filenames. The `LANG_FRENCH` block (`:203–236`, 31 lines) needs translation, and whether `CASTADOO` is invariant in French is a copywriting decision recorded as such."*
    *   Location: item 39, 1288.
    *   Change: *"9 case-sensitive lines. One is user-visible: `:323`, `-- Odoo Bot <info@odoo.com>` → `-- CASTASOFT <info@castasoft.yukreasi.id>`. The rest are licence header, exception class names and internal log text and are not changed."*
    *   Location: item 40.
    *   Change: correct the path, state 2 occurrences, and resolve the contradiction: *"Keep the licence body verbatim. Append one line: `Portions Copyright (c) 2026 CASTASOFT.`"*

---

### B13. Gate 2's own logic is contradicted by item 43, and two file actions are misclassified
[`egm-implementation-readiness` · `egm-codebase-details`] — **Severity: Major**

*   **Affected Scope:** [1332–1334](../castadoo-rebrand-fork.md#L1332-L1334) (item 43), [1313–1322](../castadoo-rebrand-fork.md#L1313-L1322) (item 42), [1336–1342](../castadoo-rebrand-fork.md#L1336-L1342) (item 44), [881–887](../castadoo-rebrand-fork.md#L881-L887)
*   **Discrepancy Description:** `#875A7B` appears in `README.md`; item 43 claims items 27 and 9 fix it — neither can (item 27 replaces a blob, item 9 is a new QWeb view). None of the four allowlist reasons is truthful for a hex colour in a README. Separately: **no root `odoo.conf` exists** (measured root listing), so item 42 is a **Create**, not a Modify — and its body already says "**Not** modified in the repo"; and `CONTRIBUTING.md` **does exist** at root, so item 44 is a **Modify**, not a Create.
*   **Rationale:** Both misclassifications change the upstream-path arithmetic and add an unlisted upstream path to the diff.
*   **AI Suggestion:** **PROPOSE FIX**
*   **Justification:** Measured. The `README.md` fix is a prose rewrite, which makes an allowlist entry unnecessary.
*   **Proposed Edit:**
    *   Location: item 43, 1332–1334.
    *   Change: *"Rewrite the `README.md` passage so no brand hex appears; then no allowlist entry is needed."* Remove the false claim about items 27 and 9.
    *   Location: item 42 and 881–887.
    *   Change: Action = **Create** `odoo.conf` is wrong as a repo artefact; state it as *"not a repo file — the deployment supplies it; the `addons_path` entry must list the `castadoo/` directory **first**."* Delete the "(see item 35)" pointer at 882 → "(see item 42)".
    *   Location: item 44.
    *   Change: Action = **Modify** `CONTRIBUTING.md`; note it is an upstream path and therefore enters the diff budget and the LGPL dating obligation.

---

### B14. The verification plan names no harness, and one command is vacuous
[`egm-implementation-readiness` · `egm-codebase-details` · `egm-design`] — **Severity: Major**

*   **Affected Scope:** [1376–1411](../castadoo-rebrand-fork.md#L1376-L1411)
*   **Discrepancy Description:** `odoo-bin --test-tags /castadoo_branding` — **no item creates a test file**, so the tag selects nothing and exits 0. `--addons-path` is omitted from the line 1378 command — the thing item 42 exists to supply. `--version` does not list modules. "must show all 9 addons" conflicts with item 22 optional and item 7 conditional. No assertion exists for items 6, 35–42. The suite is not hermetic: company name, email colour and `web_app_name` are deployment data.
*   **Rationale:** Odoo already provides what the plan reinvents: `HttpCase`, an existing `addons/web/tests/test_webmanifest.py` exercising exactly the `name`/`background_color`/`theme_color`/`icons` fields asserted at 1387, `browser_js` for computed style, and `MailCase`/`assertEmailSent`/`_render_template` for rendered email.
*   **AI Suggestion:** **PROPOSE FIX**
*   **Justification:** A4's seeding fix makes three of the five values hermetic; the rest need an explicitly labelled post-deploy tier. Reusing the existing `test_webmanifest.py` is cheaper than writing a parallel one.
*   **Proposed Edit:**
    *   Location: 1376–1411.
    *   Change: split into **Tier A — source-tree tests** (`tests/test_branding.py` as `HttpCase`, extending the stock `test_webmanifest.py` pattern; `browser_js` for computed style) and **Tier B — post-deploy assertions** (company name, logo, PDF text extraction, installer). Add `--addons-path` to the 1378 command. Replace `--version` with a DB query. State the pass condition as "all required addons present", listing which are required after D7-B.

---

# 🟢 NIT

### C1. Thirteen quantities with more than one value
[all stages] — **Severity: Nit**
*   **Affected Scope:** passim; listing at [1413–1443](../castadoo-rebrand-fork.md#L1413-L1443)
*   **Discrepancy Description:** files (54/49/47/37), binaries (16/11), `package.py` (8/9), additive (23/22/27), records per item (item 4: 2/3; item 11: 1/4; item 17: 1/2), digest range (270–447/451), optional files (2/3), in-place sites (4/6).
*   **AI Suggestion:** **PROPOSE FIX** — all dissolve once B1/B2 land; the fix is to delete the hand-typed totals and cite the generated table. **Proposed Edit:** replace each restated figure with a pointer to the derived view; keep only the figures in the manifest.

### C2. The `<title>` assertion cannot pass
[`egm-implementation-readiness`] — **Severity: Nit**
*   **Affected Scope:** [911–912](../castadoo-rebrand-fork.md#L911-L912), [1386](../castadoo-rebrand-fork.md#L1386)
*   **Discrepancy Description:** `webclient_templates.xml:22` is `<title t-esc="title or 'Odoo'"/>`; the fallback fires only when `title` is falsy, and most `/web` routes set `title` from data. Measured: `webclient_offline` sets its own at `:288`; the test templates set theirs at `:218`/`:233`.
*   **AI Suggestion:** **PROPOSE FIX** — keep the inheritance (it fixes the empty-title case); move the assertion to `title == company.name`. **Proposed Edit:** 1386 → *"with no company name set the tab reads CASTADOO; with a company set it reads the company name."*

### C3. Item 32's consumer is unestablished
[`egm-implementation-readiness`] — **Severity: Nit**
*   **Affected Scope:** [1197–1200](../castadoo-rebrand-fork.md#L1197-L1200)
*   **Discrepancy Description:** Nothing in `website_links` was found to reference `default_favicon.png`.
*   **AI Suggestion:** **CONTEST**
*   **Justification:** The finding is checkable and wrong. `addons/website_links/static/src/xml/recent_link.xml:12` carries `onerror="this.src='/website_links/static/img/default_favicon.png'"`. The earlier probe scanned `views/` and `i18n/` and missed `static/src/xml/`. Item 32 stays in scope, and its description ("Default link-preview icon") is accurate.
*   **Proposed Edit:** None. Optionally tighten 1199 to *"Fallback icon for the link-tracker preview, used when the favicon service fails (`recent_link.xml:12`)."*

### C4. Item 4 declares two records and describes three sites
[`egm-implementation-readiness`] — **Severity: Nit**
*   **Affected Scope:** [926–937](../castadoo-rebrand-fork.md#L926-L937)
*   **Discrepancy Description:** "The two inherited records" then lists `<img alt>` at `:330`, the paragraph at `:332`, and the `<style>` block at `:293–326`; the preferred `<style>` option is a fourth distinct xpath.
*   **AI Suggestion:** **PROPOSE FIX** — measured: `:317` `background-color: #714B67`, `:319` `border: 1px solid #714B67`, `:326` `</style>`, `:330` `alt="Odoo logo"`, `:332` paragraph, all exact. **Proposed Edit:** 926 → "three or four inherited records"; name the parent `web.webclient_offline` (`:285`) once and state that the preferred `<style>` option is an append, giving four.

### C5. `Registry.remove` exists
[`egm-implementation-readiness`] — **Severity: Nit**
*   **Affected Scope:** [950–966](../castadoo-rebrand-fork.md#L950-L966)
*   **Discrepancy Description:** `registry.category("user_menuitems").remove?` carries a literal `?`; the item also conflates the registry key with the item id.
*   **AI Suggestion:** **PROPOSE FIX** — measured: `registry.js:122` defines `remove(key)`. `user_menu_items.js:91` is `id: "account"`; `:128` is `.add("odoo_account", odooAccountItem)`, so `odoo_account` is the **key**. **Proposed Edit:** write `registry.category("user_menuitems").remove("odoo_account");` and change the prose from "the item's id" to "the registry key".

### C6. Item 26 is filed in the wrong tier
[all stages, Stage 8] — **Severity: Nit**
*   **Affected Scope:** [1149–1165](../castadoo-rebrand-fork.md#L1149-L1165)
*   **Discrepancy Description:** Sits under "Tier 1 — base addon" while its own text says "These are **not** new files in `castadoo/`. They are overwrites of upstream blobs", and the Tier 3 heading follows immediately.
*   **AI Suggestion:** **PROPOSE FIX** **Proposed Edit:** move the item under Tier 3, or (preferred, with B2) drop the Tier headings and let the `upstream_owned` column place it.

### C7. Ten mechanisms are used without definition
[`egm-comprehension`] — **Severity: Nit**
*   **Affected Scope:** passim
*   **Discrepancy Description:** QWeb, xpath inheritance, Owl `t-inherit`, `auto_install`, `noupdate`, `ir.config_parameter`, `addons_path`, blobless clone, promisor remote, `--no-ff` are all load-bearing and undefined. The mechanism table's ranking cannot be evaluated without them.
*   **AI Suggestion:** **PROPOSE FIX** — this is a comprehension gap, so it is not contestable. **Proposed Edit:** add `## Glossary` before `## Technical Plan`, ten entries, one line each.

### C8. Identifier and numbering defects
[`egm-comprehension` · `egm-structural`] — **Severity: Nit**
*   **Affected Scope:** [113](../castadoo-rebrand-fork.md#L113), [157–161](../castadoo-rebrand-fork.md#L157-L161), [180–185](../castadoo-rebrand-fork.md#L180-L185), [205](../castadoo-rebrand-fork.md#L205), [425](../castadoo-rebrand-fork.md#L425), [551](../castadoo-rebrand-fork.md#L551)
*   **Discrepancy Description:** D3 and D4 are never cited; D2 is used at 113 before being stated; no S-numbering table exists anywhere for the eleven S-IDs (first use at 425 carries no pointer); `#7` is cited at 171/205/551 but `## Open Questions` announces six and has no #7.
*   **AI Suggestion:** **PROPOSE FIX** **Proposed Edit:** add the S-ID table or a pointer at 425; add OQ7 to the section; cite D3/D4 where their subjects already appear in prose.

### C9. Wrong cross-reference at 882
[all stages] — **Severity: Nit**
*   **Affected Scope:** [882](../castadoo-rebrand-fork.md#L882)
*   **Discrepancy Description:** "(see item 35)" is attached to the `addons_path` entry; item 35 is `release.py`, and `addons_path` is item 42.
*   **AI Suggestion:** **PROPOSE FIX** **Proposed Edit:** → "(see item 42)".

### C10. Structural clean-ups
[`egm-structural`] — **Severity: Nit**
*   **Affected Scope:** [874–889](../castadoo-rebrand-fork.md#L874-L889), [829](../castadoo-rebrand-fork.md#L829), [848](../castadoo-rebrand-fork.md#L848), [291](../castadoo-rebrand-fork.md#L291), [554](../castadoo-rebrand-fork.md#L554), [383–387](../castadoo-rebrand-fork.md#L383-L387), [517–527](../castadoo-rebrand-fork.md#L517-L527), [235–237](../castadoo-rebrand-fork.md#L235-L237)
*   **Discrepancy Description:** The mandatory `### Target Files to Create/Modify` H3 is missing (five `### Tier` headings substitute for it); `### Additional Resources` and `### Future Improvements` are H3 with no H2 parent; two extra `----` breaks; two `text` fences contain Python and shell; CUJ 2's nested bullets wrap to column 6.
*   **AI Suggestion:** **PROPOSE FIX** **Proposed Edit:** insert the H3 at 889; promote both sections to `##` and record the deviation from `design_doc.md:121`/`:130`; delete the two extra breaks; retag the fences `python` and `bash`; re-indent CUJ 2's bullets to column 8.

### C11. Voice and redundant clauses
[`egm-style`] — **Severity: Nit**
*   **Affected Scope:** passim; specific lines listed below
*   **Discrepancy Description:** 16 rhetorical "not X; it is Y" constructions in 873 lines; six "silent/silently" (two carry mechanism); present tense describes a repository that does not exist; several decorative clauses.
*   **AI Suggestion:** **PROPOSE FIX** for the specific lines, **DECLINE** for the construction counts. **Justification:** the construction is the document's analytical signature and earns its space where it states a mechanism; counting it is not an actionable edit. The specific lines are actionable.
*   **Proposed Edit:** delete "The consequence, stated rather than glossed:" ([154](../castadoo-rebrand-fork.md#L154)); delete the first two clauses of [429–430](../castadoo-rebrand-fork.md#L429-L430), keeping the table; delete "Step 3 is not ceremonial." ([529](../castadoo-rebrand-fork.md#L529)) keeping the reason; delete "simply" ([638](../castadoo-rebrand-fork.md#L638)) and "genuinely" ([410](../castadoo-rebrand-fork.md#L410), [594](../castadoo-rebrand-fork.md#L594)); replace "Each changes what gets implemented" ([171](../castadoo-rebrand-fork.md#L171)) with "Two change documentation only"; add one convention line under Status: *"present tense describes the intended end state; nothing here exists yet."*

---

# ESCALATE — need your knowledge, not approval

### E1. Target deployment platform and named owner (from A8, B5)
The deployment checklist's content is platform-dependent: on Windows the service name and `odoo.conf` location are fixed by the installer; on Linux the config lands in `/etc`; in containers neither applies. No file in this project records which. Also no file names a second maintainer, so the bus-factor mitigation cannot be written. **Question:** what is the production platform, and who is the backup maintainer?

### E2. D3 — phone-home default (from A8)
`has_telemetry` / `web.base.url` disclosure is currently parked on Open Question 2 with three incompatible dispositions in the document. The design can record a decision but cannot make one: opting out may be a CASTASOFT policy position (customer trust) or an operational one (losing usage data). **Question:** opt in, opt out, or leave at stock?

### E3. Installer superuser password policy (from A8)
`setup.nsi:87` ships `openpgpwd` (measured: the only instance in the tree). Options are force-on-first-run, generate-and-print, or record as accepted risk. All three are release-process decisions. **Question:** which, and does the installer's first-run page change?

### E4. Legal posture on the mark (from A9)
Whether the design should state reliance on a specific LGPL clause, and whether CASTADOO's use of a mark containing Odoo's has been reviewed, is a legal judgement. The design can be made internally consistent either way — it currently is not, because three passages answer it differently. **Question:** has this been reviewed, and should the document say so or say "unresolved, owned by CASTASOFT"?

---

## Outcome

**Status: resolved.** All 27 `PROPOSE FIX` items were applied to
`docs/designs/castadoo-rebrand-fork.md`, in document order, in a single pass. The three
findings the consolidated report got wrong were corrected against the tree rather than
applied as written, and those corrections are recorded in the "Corrections to the consolidated
report" section above.

| Disposition | Count | Detail |
|---|---|---|
| Accepted and applied | 27 | every `PROPOSE FIX` item |
| Contested — resolved against the tree | 2 | A1's sub-claim (the `-u` convention: **wrong**, `post_init_hook` never re-runs on `-u`), C3 (38/16 split reclassified to text) |
| Escalated, not answerable by this design | 4 | E1 deployment platform + backup maintainer; E2 phone-home default (D3); E3 installer superuser password policy; E4 legal posture on the mark |
| Declined | 1 | C11's voice-count suggestion — the counts are load-bearing here, so they stay and are made derivable instead |
| Left unaddressed by design | 0 | — |

Three findings changed materially during resolution, each because measurement contradicted
the draft *and* the review:

*   **The service worker does not cache the app shell.** It caches exactly one URL —
    `/web/offline` — under a constant cache name. The review's premise ("the shell is
    cached") was wrong; the cache-versioning decision was rewritten around what the file
    actually does, and the decision is still "no cache-busting in the tree", for a narrower
    and more defensible reason.
*   **`post_init_hook` never runs on `-u`.** `loading.py:178` sets
    `new_install = package.state == 'to install'` and the call at `:243–247` is gated on it.
    Both the hook's stated contract and the deployment checklist were corrected; the residual
    gap is now closed by an explicit `-i castadoo_branding_<new>`, not by a version bump.
*   **The diff budget and the register's headline measure different things.** 37 is a
    coverage count (additive and inherited paths included); the paths git actually reports as
    modified are 25 (16 replaced + 8 edited + 1 conditional). Both figures are now derived
    from the manifest and the document says which is which, instead of asserting one number
    everywhere.

The four escalations are unchanged and still require the author: they are decisions about
deployment, policy, release process and law, not about this document.

*Report status: resolved. Edits applied; see the Outcome section.*
