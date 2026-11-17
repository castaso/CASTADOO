# CASTADOO: Rebranded Fork of Odoo 17.0

*   **Author:** acer (castasoft@gmail.com)
*   **Status:** Draft
*   **Date:** 2026-11-17

*Convention: the present tense in this document describes the intended end state. Of that
state, only this document, the register it cites and the review trail exist so far — there is
no fork, no `17.0` mirror branch, no `castadoo/17.0` overlay branch and no CI file.*

--------------------------------------------------------------------------------

## Overview

Create a maintained fork of `github.com/odoo/odoo` at series 17.0, named
`castaso/CASTADOO`, that presents CASTADOO branding to users while remaining cheap to
sync with upstream at point releases. The operator is CASTASOFT
(https://castasoft.yukreasi.id).

The deliverable of this design is a **source tree**, not a product build. It is the
shape of a repository: which branches exist, which files differ from upstream, and how
those differences survive an upstream merge.

**Why a fork at all.** The fork exists for one reason: `setup/win32/setup.nsi` is not an
addon and cannot be reached from `addons_path`, so branding the Windows installer is
impossible without a fork. Every other in-tree file in scope is one, two or four lines. If
the installer surface ever leaves scope, the correct shape becomes an addon repository plus
a patch file, and the branch model, the sync procedure and Alternatives A–F cease to
apply.

The fork separates two concerns that are usually tangled together:

1.  **A pristine mirror.** Branch `17.0` is byte-identical to `odoo/odoo` branch `17.0`.
    "Pristine" is defined operationally, not rhetorically:
    `git rev-parse 17.0 == git rev-parse upstream/17.0`. A check, not a claim.
2.  **An overlay branch.** Every CASTADOO change lives on one long-lived branch that
    merges upstream point releases into itself. Nothing is edited on `17.0`.

Branding is applied through four mechanisms of very different cost, chosen per string
rather than per file: database configuration (zero code), QWeb inheritance in new files
(zero conflict surface), binary replacement at the same path (zero reference edits), and
in-place editing of upstream files (real, recurring conflict surface). The fourth is the
only one that costs anything to maintain, so the design treats it as the scarce resource.

Scope is bounded at **25 upstream paths touched, 103 edited lines, 39 additive files**,
excluding the seven `mail.template` body re-declarations by decision D1-C. The first figure is
the diff budget: 16 replaced artefacts, 8 edited upstream paths and 1 conditional edit. The
register's own headline of "37 files" is a *coverage* count — it includes the additive
overrides and the views the plan only inherits, neither of which makes a path differ in git —
so it is not the budget and must not be read as one. Every path is enumerated with a line
number in `docs/change_register.md`, measured against 17.0 tip
`9c58cae5d6e3cf91ac1cca7df39fb21f68ca6e15` (40,111 files in tree) and re-verified line by
line against `e57daa52dd19556990fb03f767dfcf516a24feec`, the tip at the time the fork was
cut; every figure here is a
rendering of the manifest and is not to be maintained by hand.

## The Problem

### The business need

CASTASOFT deploys Odoo 17.0 for customers who see the software as CASTASOFT's product.
Today those customers see Odoo's name on the login page, in the browser tab, on PDF
reports, at the bottom of every notification email, on the Windows installer, and on the
installable web app. The fork exists to put the operator's name on the surfaces a
customer actually looks at.

The licence permits modification and redistribution. It grants no trademark rights.
Presenting CASTADOO as the product name is a branding decision recorded here; whether it
engages Odoo's mark is a legal question flagged in Non-Functional Requirements and not
resolved by this design. What the design does commit to is keeping the derivation visible
and the notices intact, so the work is not "remove Odoo"; it is "make CASTADOO the product
name on user-facing surfaces while keeping the derivation attributable".

### Why this is hard

Rebranding and cheap syncing pull against each other:

*   Every string changed **inside an upstream-owned file** becomes a merge conflict the
    next time upstream touches that region. The Windows installer alone would be 89 such
    lines in one file — high volume, but a leaf file upstream touches once or twice a year.
*   Every string **left alone** is a place a customer still reads Odoo.

A naive fork picks one side. Edit everything and the first sync is a manual merge of
thousands of lines; edit nothing and the rebrand is incomplete. The design has to draw
the line deliberately, and on evidence about what the software actually does rather than
on how often the word appears.

### What the measurement changed

The first estimate was wrong in ways that would have caused production incidents, not
just extra work. The corrections that shaped this design:

| Claim before measuring | What 17.0 actually does | Consequence |
|---|---|---|
| `release.py` is a branding file; ~4 safe lines | `release.product_name` has exactly one consumer: `odoo/tools/config.py:50` → `appdirs.user_data_dir()`. It **is** the default datadir. | Renaming it silently relocates every filestore and creates an empty new one with no error. Freeze it. Net `release.py` change is **one line**: `description`. |
| Email footers are `mail.template` data, so not overridable | 20 sites: 11 are inheritable QWeb views, 7 are data bodies, 2 are Owl asset templates. A `<template>` element inside `data/` is still a QWeb view; and one footer's verb is `Sent by`, not `Powered by`. | ~90% of the email surface becomes additive, no upstream edit. |
| PDF report headers need rebranding | `external_layout_standard` renders `company.name`, `company.logo`, `company.street`. Zero literal `Odoo` in the rendered PDF body. | The PDF surface is two metadata `<title>` strings. Everything visible is company data. |
| The PWA manifest name is hardcoded | `webmanifest.py:48` reads `ir.config_parameter['web.web_app_name']`, with `'Odoo'` only as fallback | Zero edits for the name. |
| `setup.nsi` has 45 Odoo strings | 729 lines, **89** of them contain `Odoo` — **114 occurrences** (119 any-case) | Installer cost was understated ~2×. It is also the surface that justifies the fork existing at all. |
| Odoo purple is `#875A7B` / `#71639e` | **Four** distinct purples: `#714B67` (brand), `#71639e` (a stray `theme-color`), `#875A7B` (legacy email), and `#9E588B` (`hr_expense` mail, unique to that module). Only the `mail` and `digest` layouts read the company field. | Four of ten in-scope email sites are fixed by one setting; five hardcode a literal, one of them in a colour no summary had listed. The backend needs SCSS surgery to change, so it stays purple. |

The methodological correction behind all of them: **a case-sensitive grep cannot tell a
brand string from an identifier.** Measured at the 17.0 tip, counting one unit per term:

| Unit | Count |
|---|---|
| Files containing `Odoo` at least once | 26,552 |
| …of which translation files (`i18n/*.po`, `i18n/*.pot`) | 19,459 |
| …of which carry the mandated `# Part of Odoo. See LICENSE…` notice | 5,496 |
| Files that are neither — the real candidate set | **1,597** |

At line level the same tree gives 111,354 matching lines, of which 102,367 are inside
translation files; of the 8,987 non-translation matching lines, 5,496 are the licence
notice and **3,491** are everything else. Those 3,491 are overwhelmingly internal names —
`odoo_chart`, `OdooBarChart`, class names, docstrings, test fixtures.

A work budget derived from substring counts would be wrong in both directions, so this
design derives its budget from **surfaces that render**, and every per-file count it relies
on lives in `docs/change_register.md` rather than in this paragraph.

### The failure mode that survives a clean merge

The dangerous case is not a broken override. An xpath whose anchor upstream renamed fails
loudly at install, which is fine.

The dangerous case is an override that still applies cleanly when upstream **adds** new
brand copy nearby. Nothing conflicts, nothing errors, the new upstream string ships, and
a customer finds it. Git cannot catch that, and neither can a person reading a merge
diff over 40,000 files.

So the design includes three gates that run on every sync rather than one: the mirror
identity check (the `17.0` branch still equals `upstream/17.0`), the diff budget (the
overlay's modified upstream paths match the manifest, and stay within it), and the brand
lint (grep the post-sync tree for the enumerated patterns, fail on any hit that is not an
explicitly justified allowlist entry).

## Goals

*   **G1 — Real fork relationship.** `castaso/CASTADOO` is a GitHub fork of `odoo/odoo`,
    so objects are shared and local storage stays small. Verified by the GitHub API
    reporting `parent.full_name == "odoo/odoo"`.
*   **G2 — Pristine mirror, provable.** `git rev-parse 17.0` equals
    `git rev-parse upstream/17.0` after every sync. The check is a CI gate, not a habit.
*   **G3 — One overlay branch.** Every CASTADOO change is on one branch that merges
    upstream with `--no-ff` (decision D2). No history is force-pushed. Every commit SHA
    is stable across point releases.
*   **G4 — Branding on six named surfaces.** The six are: **S1** backend shell and browser
    tab, **S2** login, **S3** PDF report metadata, **S4** outgoing email, **S5** Windows
    installer, **S6** PWA manifest, offline page, favicon and app icons. "Branded" is
    defined by the assertions in the Verification Plan — the login body, the manifest name,
    the PDF text extraction — not by a prose claim. Leakage is stated in Non-Goals rather
    than denied here.
*   **G5 — Diff budget is bounded on two axes, and the second predicts cost.** (a) Volume:
    the overlay touches **≤ 25 upstream paths** for **≤ 103 edited lines** (94 register
    lines plus the 9 in items 39–40), with additive files reported separately and *not*
    counted. The 25 decomposes as 16 replaced artefacts at existing paths, 8 edited upstream
    paths, and 1 conditional edit. (b) Exposure: **≤ 6 of those 25 paths** whose upstream
    churn in the last N point releases overlaps an edited line. Measured as
    `git diff --stat --diff-filter=M upstream/17.0...HEAD` restricted to the paths in the
    change manifest, so added files are excluded by construction. `setup.nsi` is reported as
    high volume, low rate; `webmanifest.py` as low volume, high rate.
*   **G6 — Fresh clone is small.** A blobless clone of the fork stays under 500 MB
    (measured: 444 MB) with full history. Clone *duration* is not asserted; see Open
    Question 4.
*   **G7 — LGPL-3 compliance is traceable.** `# Part of Odoo` headers untouched,
    `release.author` frozen at its tree value, notices preserved in the installer and
    licence file, every modification dated in the commit that introduced it, and every new
    file carrying a header that names both CASTASOFT and the upstream derivation.
*   **G8 — Drift is caught by machine, within stated limits.** A sync that introduces a
    literal unbranded string *in an enumerated path*, or edits a file outside the register,
    fails CI before it reaches a customer. The gate cannot see a string composed at runtime
    or a view that still applies after upstream rearranges its surroundings; those are
    covered by the install-time smoke test and the rendered-output tier, not by the grep.
*   **G9 — Sync procedure is written down, and rehearsed.** Trigger, owner, conflict
    fallback and a rehearsal on a throwaway clone, so the fork does not depend on one
    person's memory.

## Non-Goals

*   **Relicensing.** LGPL-3 cannot become MIT or proprietary. The notices cannot be
    stripped. This is a constraint on the work, not a task within it.
*   **Renaming internal identifiers.** The `odoo` Python package, `odoo-bin`,
    `ODOO_RC`, `odoo.conf`, the datadir, `version_info` and `series` all keep their
    names. Renaming them breaks addons, upgrade paths and every future sync, and none of
    them is user-visible. Accepted leakage: `version_info` and `series` do surface in the
    database manager and in module-upgrade reports, so a determined administrator can read
    the upstream series. That is recorded here rather than claimed away.
*   **Changing `release.product_name`, `release.author`, or `release.nt_service_name`.**
    Datadir relocation, LGPL attribution, and service orphaning respectively. The
    reasoning is in The Problem above.
*   **Editing the 19,459 `.po` / `.pot` files in place.** Translation source strings keep
    saying Odoo in every non-English locale. Accepted leakage. A `msgstr`-only branding
    overlay is noted as future work, not part of this plan.
*   **Rewriting help text, tooltips, error messages, tour copy, and demo data.** Roughly
    1,150 additional strings, each needing a human judgement on whether `Odoo` there
    means *this product* or *the software it derives from*. Getting that wrong is a
    trademark statement, not a typo.
*   **Re-declaring the seven `mail.template` body records.** Decision D1-C. The
    consequence is stated rather than glossed: portal-invitation, portal-welcome,
    account-created, badge, lunch-supplier and lead-forward mails keep a `Powered by
    Odoo` footer and Odoo purple. Of these, portal-invitation and account-created are
    customer first-contact mail, so the leakage is on a named surface and not merely
    margin.
*   **Retheming the backend to `#303188`.** `primary_variables.scss:73` reads
    `$o-brand-odoo: $o-community-color !default;`. That `!default` makes *that line* yield
    to an earlier definition; it does not block a plain assignment in a later-loaded file,
    because Odoo concatenates a dependent module's SCSS after `primary_variables.scss`. The
    route exists — a new file in an asset bundle owned by a branding module. It was
    rejected on scope, not on mechanism: a backend palette is not one of the six surfaces,
    and the dependency weight needed to reach it costs more than the surface is worth. The
    backend stays purple by decision.
*   **Replacing `nologo.png`** (an intentional placeholder) or
    `account/…/Odoo_logo_O.svg` (a stencil inside the invoice QR code, where a change
    alters the QR payload).
*   **Building, signing, distributing or supporting a product.** No installer *pipeline*,
    no auto-update, no release artefacts, no signing. This plan produces a source tree; the
    installer is in scope as a source-tree edit to `setup.nsi`, and producing a build is a
    manual step whose preconditions are recorded in the runbook. A release build is not a
    deliverable of this design.
*   **Forking more than one series.** 17.0 only.

## Open Questions

Six questions remain open, and one more is carried here because it is the one that was last
to close. Each is stated rather than answered, because each changes something downstream.
Two of the six (#1, #4) change nothing in the source tree; three (#2, #5, #6) change one
file each; #3 changes an estimate and a verification cost. Where the plan depends on an
answer, the affected item names it.

1.  **17.0 upstream support window.** Does Odoo 17.0 Community still receive point
    releases? If upstream maintenance has ended, "sync at point releases" describes a
    process that will never fire, and the merge model in Goal G3 has nothing to merge.
    *Shapes:* the sync procedure's trigger and the CI gates' value. No file in the plan
    changes either way.
2.  **Phone-home default (D3).** `odoo/tools/config.py:78` defaults `publisher_warranty_url`
    to `http://services.openerp.com/publisher-warranty/` — note `openerp.com`, not
    `odoo.com`. It is a daily outbound call carrying instance metadata. Disable by default
    with a commented config line, or leave stock? *Shapes:* item 41 (a one-line source
    edit) **or** a key in the operator's `odoo.conf`. The config-key route removes item 41
    from the diff entirely and is the cheaper of the two; the source route applies to every
    deployment without operator action. That trade is the question, and no default has been
    chosen.
3.  **Deployment shape.** One tenant per install, or a shared multi-database host? *Shapes:*
    per-release asset recompilation goes from a constant to O(databases), and it changes
    how much the CI gates matter — a single-tenant install tolerates drift a
    multi-tenant host cannot.
4.  **Bandwidth figure.** Two measurements disagree by ~34×: 188 MB in 746 s (≈0.25 MB/s)
    versus a 4.7 GB clone in 544 s (≈8.6 MB/s). Every duration estimate for the initial
    clone depends on which is real. *Shapes:* nothing in the source tree; re-measure once
    with the exact intended command before quoting any duration to anyone.
5.  **Installer publisher (D6).** `PUBLISHER 'Odoo S.A.'` in `setup.nsi` line 44 declares
    the publisher of *this binary*, not a copyright notice. Left alone, the installer
    reports Odoo S.A. as its publisher and throws unknown-publisher warnings once signed
    with the CASTASOFT certificate. *Shapes:* one line in `setup.nsi`. Recommendation on
    record: `CASTASOFT` in `PUBLISHER`, LGPL notice preserved in `COPYRIGHT` / `NOTICE`.
6.  **Wordmark font (D5).** Convert with the installed Garamond (`GARA.TTF`) to match the
    current design exactly, or rebuild on EB Garamond (OFL) and accept a small shape
    change? Garamond as shipped is not freely redistributable, and outlining a wordmark
    fixes rendering but not the licence to embed those glyph shapes. *Shapes:* how the
    wordmark assets are produced, not which files they land in.

**Resolved while writing the plan — D7.** Overlay activation is decided: **Option B,
`post_init_hook`**. It is recorded in the Technical Plan and not repeated here, but the
decision exists because the naive `auto_install` reading is wrong on any database where the
target module was already installed — the overlay silently is not installed, and the footer
keeps reading Odoo. That is the failure the hook exists to close, and the one place where a
"correct" configuration still produces an unbranded surface.

## Critical User Journeys (CUJs)

### CUJ 1: A customer's first visit is branded

*   **Given**: A CASTADOO deployment exists and `castadoo_branding` is installed. The
    company record has `name`, `logo` and `email_secondary_color` set.
*   **When**: A customer opens the deployment URL and reaches the login page, then logs in
    and looks at the browser tab.
*   **Then**: The browser tab reads `CASTADOO` when no company name is set, and reads the
    company name once one is; the login card shows the CASTADOO logo, because
    `/web/binary/company_logo` serves `res.company.logo`. The footer under the card reads
    CASTADOO and links to the CASTASOFT site, not `odoo.com`. No string on the screen reads
    "Odoo" apart from the licence notice that is not rendered here.
*   **Verification**: automated assertion that `GET /web/login` response body contains no
    `>Odoo<` and contains `CASTADOO`; and that `GET /web` with no company name set renders
    `<title>CASTADOO</title>`. The tab title is data-driven on a configured deployment, so
    asserting "the tab reads CASTADOO" unconditionally would fail on any named company.

### CUJ 2: A maintenance sync happens and nothing silently regresses

*   **Given**: Upstream publishes a 17.0 point release. The overlay branch is one merge
    behind.
*   **When**: The maintainer runs the documented sync procedure: fetch upstream, fast-forward
    `17.0`, merge into the overlay with `--no-ff`, resolve conflicts, push.
*   **Then**:
    *   `17.0` equals `upstream/17.0` exactly.
    *   The merge commit message records the date and the upstream tag consumed.
    *   The diff-budget gate confirms the overlay still touches ≤ 25 upstream paths and
      ≤ 103 edited lines.
    *   The brand-lint gate either passes or names each new unlisted occurrence, so the
      maintainer handles a known list rather than discovering surprises in production.
    *   If upstream added new brand copy that the existing overrides do not reach, the
      lint fails and the sync stops before deployment.
*   **Verification**: all three gates green; `git diff --stat --diff-filter=M
    upstream/17.0...HEAD` inside the budget.

### CUJ 3: A customer receives a notification email

*   **Given**: A notification email is generated by `mail_notification_layout` (the
    layout under every internal notification), and `res.company.email_secondary_color`
    is `#303188`.
*   **When**: The email arrives at the customer.
*   **Then**: The footer reads `Powered by CASTADOO`, the link colour is brand navy, and
    the unfollow link still works. For the seven excluded `mail.template` bodies, the
    footer still reads Odoo — accepted consequence of D1-C, documented so it is not
    reported as a defect.
*   **Verification**: rendered-email snapshot test; a manual send through a real SMTP sink
    for the layout, since CSS-in-email renders differently across clients.

### CUJ 4: A customer installs the web app or goes offline

*   **Given**: `web.web_app_name` is `CASTADOO`, the icon set has been regenerated at the
    existing `odoo-icon-*` paths, and `webmanifest.py` carries brand colours.
*   **When**: The customer installs the PWA from a mobile browser, then loses network and
    opens the app.
*   **Then**: The install prompt shows the CASTADOO name, the home-screen icon is the
    CASTADOO mark, the splash/theme colour is `#303188`, and the offline page shows the
    CASTADOO mark with text that does not read Odoo. The "Check again" button is brand
    navy.
*   **Verification**: `GET /web/manifest.webmanifest` assertions on `name`,
    `background_color`, `theme_color`, and each `icons[].src` resolving to a 200; manual
    install on one Android and one iOS device. **Post-upgrade check:** after a deploy that
    changes the brand, an already-installed app must show the new brand. Measured at 17.0,
    the service worker caches one URL — `/web/offline` — under a constant cache name and
    reinstalls only when its own bytes change, so the manifest name and icons update on the
    first launch while a changed offline page can stay stale. The acceptance check is a
    reinstall on the test device; the asset section records why the design does not version
    the cache.

### CUJ 5: An administrator installs the Windows package

*   **Given**: `setup.nsi` has been edited per the register and the three pixmaps replaced,
    and a build has been produced from the branded tree. The build is a manual release step,
    not a deliverable of this design (see Non-Goals); what the design owns is the tree the
    build consumes.
*   **When**: An administrator runs the installer, then finds the entry in Add/Remove
    Programs.
*   **Then**: Every wizard page, caption and progress bar string reads CASTADOO. The
    Add/Remove entry is named CASTADOO 17.0. The publisher field reads CASTASOFT, not
    Odoo S.A., so signing with the CASTASOFT certificate does not produce an
    unknown-publisher warning. Uninstalling removes the same registry key it created.
*   **Verification**: build the installer, install on a clean Windows VM, check the
    uninstall registry key exists and uninstall removes it; verify installed service is
    still named `odoo-server-17.0`.

### CUJ 6: A printed report reaches a customer

*   **Given**: `res.company` carries the CASTADOO name, logo and address.
*   **When**: An invoice is printed to PDF and opened.
*   **Then**: The visible header shows the CASTADOO logo and company name; the PDF
    document title metadata reads CASTADOO rather than "Odoo Report". No Odoo string
    appears in the rendered body, because the body is company data.
*   **Verification**: PDF text extraction asserting the absence of `Odoo` and presence of
    the company name; title metadata read from the PDF trailer.

--------------------------------------------------------------------------------

## Glossary

Ten mechanisms are load-bearing in this document and none is defined by Odoo's own
documentation in the terms used here. One line each, in the order a reader meets them.

*   **QWeb** — Odoo's XML templating engine. Views are XML records stored in the database;
    `<template>` and `<div t-*>` are QWeb, and "a QWeb view" means a record in `ir.ui.view`.
*   **xpath inheritance** — a view declares `inherit_id` and an `<xpath expr="…">` that
    selects a node in the parent view and replaces or appends to it. Applied at render time,
    so the parent file is never modified. This is mechanism 2.
*   **Owl `t-inherit`** — Owl's *client-side* template inheritance, used by POS and the web
    client. It is not QWeb and not a database view; the parent is named by `t-name` in a
    static XML file, and a wrong name fails **silently**.
*   **`auto_install`** — a manifest key. `True` means "install me when my dependencies are";
    a list (`['mail']`) means "install me only when one of these is newly entering
    installation". The list form is why an overlay misses an already-installed `mail`.
*   **`noupdate`** — an XML data attribute. Records marked `noupdate="1"` are created once and
    **not** overwritten on later module updates, including upstream's own. This is what makes
    re-declaring a `mail.template` a standing obligation rather than a one-off edit.
*   **`ir.config_parameter`** — the key/value settings table, read as
    `env['ir.config_parameter'].get_param('web.web_app_name')`. Values here are database
    state, invisible to every CI gate.
*   **`addons_path`** — the ordered list of directories Odoo scans for modules.
    `module.get_module_path` returns the **first** match, so order is precedence.
*   **blobless clone** — `git clone --filter=blob:none`. History and commit objects are
    fetched; file contents are fetched on demand from the "promisor" remote. It is why the
    fork measures 444 MB instead of ~17.7 GB, and why the fork must be the promisor.
*   **promisor remote** — the remote a blobless clone fetches missing blobs from. If it is
    not the destination repository, materialising history there costs a full transfer — the
    reason for "fork first, then clone from the fork".
*   **`--no-ff`** — `git merge --no-ff` always creates a merge commit even when a
    fast-forward is possible. Used so each upstream sync leaves one dated, attributable
    commit, which is what discharges the LGPL modification-dating obligation.
*   **`post_init_hook`** — a manifest key naming a function the loader calls once, after a
    module is **first installed** (`loading.py:245`). It does not run on `-u`. It receives
    the `env`, and it is the mechanism D7 chose.
*   **`--diff-filter=M`** — restricts `git diff` to modified paths, excluding added and
    deleted ones. Used so the diff budget measures edited upstream files rather than counting
    the new addon tree.
*   **`--first-parent`** — `git log --first-parent` follows only the mainline of merges,
    hiding the commits brought in by each merge. The convention for reading overlay history
    under D2.

--------------------------------------------------------------------------------

## Technical Plan (Architecture)

### Repository topology

Two branches, one remote, one rule: nothing is edited on the mirror.

```text
   odoo/odoo (upstream)                     castaso/CASTADOO (fork)
        │                                          │
        │  17.0                                    ├── 17.0   ← fast-forward only
        └──────────────────────────────────────────┤            byte-identical to upstream
                                                   │
                                                   └── castadoo/17.0   ← the overlay
                                                            │
                          every CASTADOO change lives here ─┘
                          merges upstream/17.0 with --no-ff
```

*   **`17.0`** — a mirror. Updated only by `git merge --ff-only upstream/17.0`. If that
    command fails, the branch has diverged and something is wrong; it is never resolved
    by force-pushing.
*   **`castadoo/17.0`** — the overlay. Branched from `17.0` once, then merged forward at
    each point release. Never rebased, never force-pushed, so SHAs are stable and the
    branch is safe to publish.
*   **Remotes**: `origin` = the fork (push target), `upstream` = `odoo/odoo` (fetch only).
    `origin` is the default push, and `upstream` is configured with
    `remote.upstream.pushurl = no_push` so a mistyped push cannot reach upstream.

The fork's GitHub default branch must be `17.0`, not upstream's default `20.0`. This is
verified with `git ls-remote --symref origin HEAD` after the fork is created, not assumed. A
fork whose default is `20.0` hands an unqualified clone unbranded Odoo 20.0, which is the
worst possible first impression of the fork.

### The disposition rule

Every brand string in scope is assigned to exactly one of four mechanisms, and the order
is a preference order, not a menu. A string is moved to a more expensive mechanism only
when the cheaper ones are shown not to reach it.

| Rank | Mechanism | Touches upstream files | Conflict surface | Reached surfaces |
|---|---|---|---|---|
| 1 | **Configuration** | no | none | PWA name, login logo, PDF headers, email colours, website favicon |
| 2 | **Inheritance** (new files) | no | none, unless an anchor is renamed | backend title, login footer, offline page, PDF titles, notification email footers, POS Owl templates |
| 3 | **Binary replacement** (same path) | binary only | **whole-file conflict when upstream touches the same path** — resolved by taking the fork's blob, which discards the upstream change, so the diff must be reviewed | favicon, PWA icons, logo PNGs, installer pixmaps |
| 4 | **In-place edit** | yes | recurring, per upstream touch | `setup.nsi`, `database_manager.qweb.html`, `webmanifest.py`, `release.py` description |

Rank 3 is not free. When both sides modify the same binary path git reports
`CONFLICT (content)` and offers no hunk resolution; "take ours" then silently discards an
upstream fix while looking identical in review. Three of the sixteen rank-3 items are
**text**, not binary — `odoo_logo.svg`, `odoo_logo_dark.svg` and `odoo-icon.svg` are XML,
which git diffs line by line and which will conflict inside the file. The mitigation for the
thirteen true binaries is a path-scoped `.gitattributes` rule (`merge=ours`), created by
item 1b; the three SVGs are reclassified as `modify-text` in the manifest and reviewed like
edits, and are deliberately left out of that rule.

Mechanism 4 is the scarce resource. The design's goal is to keep the count of mechanism-4
lines small and enumerated, not to reach zero. Attempting zero would mean either leaving
the installer unbranded or building an installer-side override system that does not
exist — an installer addon is a contradiction.

### One manifest, and four derived views

Every quantity in this design that has ever been wrong has been wrong in the same way: a
number computed once by hand, typed into prose, and never recomputed. Four revisions of this
document produced four different file counts, three different `package.py` counts, and two
different binary counts. The repair is not to recount — it is to make the recount automatic.

**`castadoo/change_manifest.toml` is the single source of truth.** Four record types:

```toml
# A path this fork modifies. Gate 2 diffs these; Gate 3a lints them.
[[change]]
path = "setup/win32/setup.nsi"
kind = "modify-text"          # create | modify-text | modify-binary | none
surface = "S5"
upstream_owned = true         # counts against the diff budget
conflict_surface = "recurring" # none | anchor | whole-file | recurring
reversible_by_uninstall = false
counts_against_budget = true
lines = [44, 67, 74, 75, 78, 80, 82, 160, 423, 424, 425, 426]
note = "737 lines total; 89 contain Odoo. 134-139 are pixmap paths: do not edit."

# A value a deployment or a module seed supplies. Gate 2 and Gate 3 cannot see these.
[[setting]]
key = "web.web_app_name"
model = "ir.config_parameter"
supplied_by = "module-data"   # module-data | deployment
overlay = "castadoo_branding"
assertion = "manifest name == CASTADOO"

# A post-deploy or Tier A assertion. Named here so the verification plan is generated too.
[[assertion]]
tier = "A"                    # A = source tree/CI, B = post-deploy
target = "GET /web/manifest.webmanifest"
expect = "background_color == '#303188'"

# A string that is allowed to survive, with the reason. Gate 3a and 3b read only this list.
[[allowlist]]
path = "setup/package.py"
line = 50
reason = "internal identifier"
# Closed vocabulary — one of:
#   internal identifier | D1-C | licence notice | not user-visible
#   upstream documentation | upstream-owned, not user-visible
```

**Four views are generated from it**, and none is hand-edited:

| View | Generated by | Read by |
|---|---|---|
| `docs/change_register.md` | `render_manifest.py` | humans; the per-line enumeration |
| the file-count footnote | `render_manifest.py` | the Detailed Implementation Plan |
| Gate 2's path list | CI reads the manifest directly | the diff budget |
| Gate 3's pattern + allowlist | CI reads the manifest directly | the brand lint |

The Tier headings in the Implementation Plan are a **rendering of four boolean columns**, not
an ordinal scale. That distinction is why the same set of files could be described as
"4 irreversible" and "16 binaries" in the same document: one tier label was being asked four
different questions.
`conflict_surface`, `reversible_by_uninstall`, `counts_against_budget` and `upstream_owned`
are orthogonal, and each of those wrong figures is a `WHERE` clause over them.

This is the cheapest component in a plan priced in the tens of hours, and it is the only one
that makes the count defects unexpressible rather than merely fixed.

### Addon architecture: two tiers, and the activation trap

Branding is split into a base addon plus per-module overlays rather than one addon, because
of how Odoo resolves dependency edges.

**Why one addon cannot do it.** An inherited view whose parent XML ID is absent raises
`External ID not found in the system` at install (`odoo/addons/base/models/ir_model.py:2214`).
`mail_notification_layout` lives in `mail`; `portal_templates.xml` inherits from `portal`.
A single addon that inherits all of them must declare every one of those modules as a
`depends`, and `depends` is not advisory — Odoo installs the whole chain. One base addon
covering `sale`, `account`, `crm`, `hr_expense` and `mail` would force roughly 15–25
business modules onto every database, including minimal and test ones.

**The shape:**

```text
castadoo_branding            depends: ["web"]
  └── base tier: web views, PDF titles, PWA colours, release description, user-menu patch
      plus per-module overlays, each auto_install on the module whose XML ID it inherits:

      castadoo_branding_mail          auto_install: ["mail"]
      castadoo_branding_auth_signup   auto_install: ["auth_signup"]
      castadoo_branding_portal        auto_install: ["portal"]
      castadoo_branding_im_livechat   auto_install: ["im_livechat"]
      castadoo_branding_hr_expense    auto_install: ["hr_expense"]
      castadoo_branding_digest        auto_install: ["digest"]
      castadoo_branding_website_slides auto_install: ["website_slides"]
      castadoo_branding_pos           auto_install: ["point_of_sale"]
```

That is one base addon plus eight overlays, nine addons in total. All nine live in a new
top-level `castadoo/` directory, which enters `addons_path` **first** so that
`module.get_module_path` — which returns the first addons path containing a module
(`odoo/modules/module.py:165`) — can never resolve an upstream addon ahead of a CASTADOO
one. The base tier holds only what is reachable from `web`: the QWeb view inheritances, the
PDF titles, the PWA colours, the seeded `web.web_app_name` and the user-menu patch.
`release.py`, `webmanifest.py`, `setup.nsi` and `database_manager.qweb.html` are **not**
addon content — no addon can reach them — and are in-place edits instead.

`auto_install` as a list is stock practice, not a trick: `account_payment/__manifest__.py:9`
uses `['account']`, and four other stock manifests do the same. The list names the
modules that must be present *and newly installed* for the overlay to activate.

**The trap.** That last phrase is where the design breaks if it is not handled. In
`ir_module.py:420-422`:

```python
def must_install(module):
    states = {dep.state for dep in module.dependencies_id if dep.auto_install_required}
    return states <= install_states and 'to install' in states
```

`must_install` requires at least one `auto_install_required` dependency to be in state
`to install` — that is, newly entering installation in this run. On a database where
`mail` is **already installed**, `states == {'installed'}`, `'to install' in states` is
false, and the overlay **never auto-installs**. The same holds for every overlay, and it
is worst for the highest-traffic surface: the notification-email footer, whose overlay
depends on `mail`.

So the naive reading — "declare `auto_install` and the overlays follow their modules" —
is false on any existing database. It is true only on a fresh install where `mail` is
installed in the same run.

**D7 — overlay activation: decided. Option B (`post_init_hook`).**

Three mechanisms could close this, and they trade differently. The table is kept as the
record of what was weighed, not as an open menu:

| Option | Mechanism | Why not / why |
|---|---|---|
| **A. Explicit install list** | The sync and deployment runbook runs `-i castadoo_branding_mail,...` for each module present. No code. | Rejected: a human omits one and the email footer silently keeps Odoo. It fails in exactly the way the design's gates exist to prevent, and no gate covers it. Cheapest, most fragile. |
| **B. Self-activating base addon** | `castadoo_branding` gains a `post_init_hook` that searches `ir.module.module` for installed targets and marks the matching overlays for install. | **Chosen.** Covers the migration case the other two miss, needs no hook per overlay, and its one gap — a new overlay added later — is closed by a single explicit `-i` in that release. |
| **C. Base addon declares all overlays as `depends`** | Guaranteed activation, no hooks, no runbook step. | Rejected: forces every business module onto every database — the drag the two-tier split exists to avoid. It is simpler in every respect except the one that matters. |

**The residual gap, measured — and the `-u` claim is wrong.** An earlier draft of this
decision said the convention is `-u castadoo_branding`, on the assumption that an upgrade
re-runs the hook. It does not. At `odoo/modules/loading.py:178`:

```python
new_install = package.state == 'to install'
```

and the hook call at `:243–247` is inside `if needs_update:` → `if new_install:`. A module
in state `to upgrade` has `new_install False`, so **`post_init_hook` runs on first install
only and never on `-u`**. The convention has to be stated correctly or the deployment
checklist ships a step that does nothing.

With that corrected, the gap is narrower than the draft implied, and worth stating
precisely because the mechanism that closes it is different:

*   **Covered, no action.** A target module installed *before* `castadoo_branding` existed:
    the hook fires on the base addon's first install, sees `mail` already `installed`, and
    marks the overlay. This is the common migration case and it works.
*   **Covered, no action.** A target module installed *after* the overlays exist: `mail`
    entering installation has state `to install`, which satisfies `must_install` at
    `ir_module.py:420–422`, so `auto_install` fires on its own.
*   **Not covered.** A *new* overlay added to a later release, for a target module that is
    already installed and will not be re-installed. The hook cannot re-run and
    `auto_install` cannot fire. Closing this requires an explicit
    `-i castadoo_branding_<new>` in the release's deployment step, after which the hook's
    own table keeps working.

The deployment checklist therefore carries both: the explicit install for a release that
*adds* an overlay, and a step 3 verification that every installed target has its overlay
installed. The version-bump convention is retained for a different reason — so the upgrade
actually processes the module's new data files.

**The hook's shape.** In 17.0 the loader calls the hook with a single argument:

```python
# odoo/modules/loading.py:245
if new_install:
    post_init = package.info.get('post_init_hook')
    if post_init:
        getattr(py_module, post_init)(env)
```

So the signature is `def post_init_hook(env)`, not the older `(cr, registry)`. The body
searches `ir.module.module` for installed module names among the overlay targets and calls
`button_install()` on the matching `castadoo_branding_*` records.

**The registry-reload hazard.** Installing a module from inside a hook is a nested module
operation, and `_button_immediate_install` refuses to run when the registry is not ready:

```python
# odoo/addons/base/models/ir_module.py:590
def _button_immediate_function(self, function):
    if not self.env.registry.ready or self.env.registry._init:
        raise UserError(_("The method _button_immediate_install cannot be called on init
                          or non loaded registries. Please use button_install instead."))
```

and it raises outright inside tests (`RuntimeError: Module operations inside tests are not
transactional`). The hook must therefore use `button_install()` on the records and let the
loader's STEP 3 loop pick them up, not `button_immediate_install()`. It must be idempotent,
log what it installed, and not raise when an overlay is absent from `addons_path` — the
rollout check reports that, not an exception.

### Data and configuration model

Nothing in the branding paths stores state of its own except two company fields and two
system-level values, all of which are ordinary Odoo data. The `S` identifiers below are the
register's per-site keys (`S1.01`…`S6.0x`), where `S1`–`S6` are the six surfaces named in
G4: shell/tab, login, PDF, email, installer, PWA.

| Setting | Model | Set by | Effect |
|---|---|---|---|
| `name` | `res.company` | deployment | Login title, PDF headers, email footers, portal pages |
| `logo` | `res.company` | deployment | Login card, PDF header, portal, email |
| `email_secondary_color` = `#303188` | `res.company` — **defined in `mail`, not `base`** | deployment, or seeded by the `mail` overlay | Reaches the `mail` notification layout (S4.01, S4.02) and the `digest` footer (S4.10, S4.20). **Does not reach** S4.03, S4.04, S4.06, S4.07 or S4.09, which hardcode their colour. |
| `web.web_app_name` = `CASTADOO` | `ir.config_parameter` | **module data, `noupdate="1"`** | PWA install name |
| `website.favicon` | `website` | deployment, with a module-supplied default | Website and portal favicon |

Two of those rows carry a fact the convenient story gets wrong. `email_secondary_color` is
not a base field: it is declared at `addons/mail/models/res_company.py:33` as
`fields.Char(compute="_compute_email_secondary_color", readonly=False, store=True)`, computed
at `:83` as `company.secondary_color or '#875A7B'`. It is writable, so it can be seeded — but
only where `mail` is installed, which is why its seed belongs to the `mail` overlay and not
to the base addon that depends on `web` alone.

`website.favicon` gets its default from `website._default_favicon()`
(`addons/website/models/website.py:141`), which reads `web/static/img/favicon.ico`. Replacing
that one file (item 26) therefore sets the website default as a by-product; only an explicit
per-website override needs a deployment step.

`web.web_app_name` cannot be left to deployment. Its stock fallback is `'Odoo'`
(`addons/web/controllers/webmanifest.py` — `get_param('web.web_app_name', 'Odoo')`), so a
correctly built tree on a fresh database would ship a manifest whose name reads Odoo — the
exact surface CUJ 4 asserts. It is seeded as module data, and because the base addon depends
on `web` alone, it belongs in the base tier:

```xml
<!-- castadoo/castadoo_branding/data/ir_config_parameter.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<odoo noupdate="1">

    <record id="web_app_name" model="ir.config_parameter" forcecreate="0">
        <field name="key">web.web_app_name</field>
        <field name="value">CASTADOO</field>
    </record>

</odoo>
```

`noupdate="1"` on the root element and `forcecreate="0"` on the record is the stock idiom
for "create it once, never touch it again if it exists" — measured verbatim at
`addons/account_payment/data/ir_config_parameter.xml:2–6`, which is why this snippet matches
that file's shape rather than inventing one. `noupdate` keeps a later module update from
overwriting an operator who deliberately changed the value.
This file is item 1a in the Implementation Plan; it is referenced by item 1's `data` key and
would otherwise be a manifest entry pointing at a file no item creates.

The colour row is the one place where the convenient story and the measured tree disagree,
so it is stated precisely. Of the ten in-scope email/notification sites:

| Sites | Colour mechanism | Action |
|---|---|---|
| S4.01, S4.02 (`mail` layout) | `t-att-style` with `email_secondary_color or '#875A7B'` | data only, 0 edits |
| S4.10, S4.20 (`digest`) | `color_company` = `email_secondary_color or '#714B67'` | data only, 0 edits |
| S4.03, S4.04 (`auth_signup`) | inline `style="color: #875A7B;"` | replace in markup |
| S4.07 (`im_livechat`) | inline `style="color: #875A7B;"` | replace in markup |
| S4.09 (`website_slides`) | inline `style="color: #875A7B;"` | replace in markup |
| S4.06 (`hr_expense`) | inline `style="color:#9E588B;"` | replace in markup |
| S4.05 (portal), S4.08 (livechat page), S4.18, S4.19 (POS) | no colour, or an image | text only |

So four of the thirteen in-scope email/notification sites are free and five need the literal
replaced; the remaining four carry no colour or an image. The fourth purple — `#9E588B`,
used only by `hr_expense` — is a colour no summary of this tree had recorded, and it is the
concrete reason a single find-and-replace pass over `#875A7B` is not a valid implementation
strategy. (The tree also carries a fallback `#714B67` inside `digest_mail_layout:14`, which
is a third stock purple in the same surface.)

Consequence worth stating: the company name and logo are **data**, so the rebrand is
partly a deployment step, not purely a repository change. A fresh database installed from
the branded tree still shows a blank company logo until an operator uploads one. The
design does not seed a demo company record; that would put an administrative decision
inside a module and collide with every real deployment. `web.web_app_name` is the exception
recorded above — it is seeded, because its fallback would otherwise read Odoo and because
no deployment step can be assumed to set it.

### Asset pipeline

The committed artefacts are outputs; the pipeline is a reproducible recipe, kept in the
repo so the assets can be regenerated when the design changes.

```text
  logo.svg (mark, 89.94×110.97, portrait 0.81:1)
  CASTADOO.svg (wordmark, 683.22×107.6, live Garamond <text>)
        │
        ├─ 1. outline wordmark text  → opentype.js (Node 22)
        │      reads glyph paths from the font file; no rasteriser needed
        │      removes the empty <text> node and editor metadata
        │
        ├─ 2. compose lockups         → mark + outlined wordmark
        │      horizontal (portal, PDF header), stacked, inverse-white
        │
        └─ 3. rasterise               → sharp (npm)
               favicon.ico 16/32/48, 192², 512², 180² iOS, 62×20 badge, 206px inverse
```

**One toolchain, chosen.** Each step had a Node or a Python option. The pipeline uses Node
for both — `opentype.js` for outlining and `sharp` for rasterising — because a single
`package.json` with two pinned dependencies is one thing to install and one to remember,
where a mixed toolchain is two. `fontTools` and `cairosvg` would produce the same pixels;
neither is preferred on any technical ground. The recipe is `castadoo/assets/build_assets.sh`
(item 47) plus a `package.json` beside it, with both dependency versions pinned exactly, so
regenerating in two years reproduces the same bytes rather than whatever `sharp` ships then.

Two constraints the pipeline must respect:

*   **Square icons are derived from the mark, never the wordmark.** A 6.35:1 wordmark is
    illegible at 192 px and unusable at 32 px. PWA icons also need a maskable safe-area
    inset, or Android crops the mark.
*   **Filenames never change.** `odoo-icon-192x192.png` stays named that. The name is
    never shown to a user, and keeping it converts three code edits in `webmanifest.py`
    and `webclient_templates.xml` into zero.

Rasterisers are absent on the build machine (`inkscape`, `rsvg-convert`, `magick` are all
missing; `convert.exe` on Windows is the filesystem tool, not ImageMagick). Outlining is a
vector operation and needs no rasteriser; only step 3 does, and it is one `npm i sharp`.

**Cache versioning: decided, and the reasoning rests on what the worker actually caches.**
The seller's instinct — "the PWA caches everything, so a rebrand needs a cache-busting token" — is
wrong for this tree. Measured at 17.0,
`addons/web/static/src/service_worker.js` is 37 lines, sets `const cacheName =
"odoo-sw-cache"` and caches a single request: `cachedRequests = ["/web/offline"]`. It is not
an app-shell cache. The manifest name, the icons and the document title are all fetched over
the network on every launch, so they carry the new brand on the first load after a deploy.

The one genuinely stale element is the cached `/web/offline` response — and it is stale for
a structural reason worth recording: the browser reinstalls a service worker only when the
worker's own bytes change, and the worker is served verbatim from
`web/static/src/service_worker.js` (`webmanifest.py`, `_get_service_worker_content`). A
branding release that changes the offline page through QWeb inheritance leaves that file
byte-identical, so the client keeps the old worker and the old cached page indefinitely. The
blast radius is the offline page, shown only while the device is offline.

The decision: **no cache-busting change in the tree.** Bumping `cacheName` would be a
one-line edit to an upstream file that then recurs at every release — a permanent conflict
site, priced against a surface a customer sees only when their network is already down.
Instead, the runbook's deployment step notes that a release which changes the offline page
requires a client reinstall to take effect, and CUJ 4's post-upgrade check is exactly that
reinstall. If the offline page ever becomes brand-critical, the revisitable option is to
move it out of the cache rather than to version the cache.

### The gates that run on every sync

These exist because the dangerous failure is silent. An override that still applies when
upstream adds new brand copy nearby produces no conflict, no error, and a customer
discovery.

```text
  post-sync tree
       │
       ├── Gate 1: mirror identity ────────────────────────────┐
       │     git rev-parse 17.0 == git rev-parse upstream/17.0   │  fail → sync stops
       │     a fast-forward, not a merge                        │  before deploy
       │                                                       │
       ├── Gate 2: diff budget ────────────────────────────────┤
       │     git diff --stat --diff-filter=M upstream/17.0...HEAD
       │       -- $(manifest [[change]] paths that are upstream-owned)
       │     changed upstream paths ≤ 25, edited lines ≤ 103    │
       │     every changed path present in the change manifest  │
       │                                                       │
       ├── Gate 3a: pathlint ──────────────────────────────────┤
       │     for each manifest path: grep for "Odoo"            │
       │     every hit must be in [[allowlist]] with a reason;  │
       │     the allowlist may not exceed 40 entries            │
       │                                                       │
       └── Gate 3b: treelint ──────────────────────────────────┘
             coarse patterns only, whole tree:
               "Powered by Odoo" | "www.odoo.com"
             excluding i18n/**/*.po, i18n/**/*.pot, **/demo/**
             an unlisted hit outside the exclusions fails
```

**Gate 1 is the pristine-mirror claim, mechanised.** It was Goal G2's "CI gate, not a
habit" and appeared in no gate list, which meant a maintainer who merged the overlay
without fast-forwarding `17.0` shipped a stale mirror while every other gate passed — the
three-dot diff still computes off a correct merge-base. It is now a real step with a real
invocation, and it runs first because everything downstream assumes the base is right.

**Gate 2 is the falsifiable form of "small diff", and its metric needed three corrections.**
`git diff --stat` alone would fail the gate on its own first commit: it counts the ~28
added files, and it counts a one-line replacement as `+1/-1`, so 103 edited lines appear as
~206. It also cannot tell an upstream path the plan merely *inherits* from one it edits.
The gate therefore uses `--diff-filter=M` scoped to the manifest's upstream-owned paths,
which excludes additions and deletions by construction, and states its unit as **changed
upstream paths**, not files. Lines are counted as edited lines, not diff lines. Both numbers
are read from the manifest, never typed.

**Gate 3 is split because an unscoped grep cannot pass.** The tree holds 19,459 `.po`
files, 5,496 mandated licence headers, and 1,597 files with a hit that is neither. A single
"fail on any unlisted hit" rule over the whole tree needs thousands of allowlist entries,
fills with noise, and gets disabled — which the design previously predicted and did nothing
about. So:

*   **3a, pathlint** is exact and small: every manifest path, every `Odoo` hit, and every
    hit must carry an allowlist reason from a closed vocabulary — `internal identifier`,
    `D1-C`, `licence notice`, `not user-visible`, `upstream documentation`. The ceiling of
    40 entries is the gate's own health check: if the allowlist grows past it, the diff has
    grown past the design.
*   **3b, treelint** is coarse and broad: two literals — `Powered by Odoo` and
    `www.odoo.com` — over the whole tree, with translation data, demo data and the generated
    `i18n/` tree excluded by glob. Neither is permitted by default; where one is legitimate
    (the user-menu link to upstream's own documentation, item 6) the manifest carries an
    allowlist record, so the exception is one line with a reason rather than a pattern the
    gate learns to ignore. Measured scale is why the exclusions are globbed rather than
    argued: `git grep -l "Powered by Odoo"` returns 52 files and `"Sent by"` returns 180,
    almost all of them translation files.

None of the gates can see a string composed at runtime, a view that still applies after upstream
rearranges its surroundings, or a database. Those are covered by the install-time smoke test
and the post-deploy assertions in the Verification Plan, not by grep. Gate 3 is described
here as the control for *literal* drift only, which is what it can actually do.

### Sync procedure

```text
  1. git fetch upstream --tags
  2. git checkout 17.0 && git merge --ff-only upstream/17.0        # must succeed
  3. Gate 1: git rev-parse 17.0 == git rev-parse upstream/17.0
  4. git checkout castadoo/17.0 && git merge --no-ff upstream/17.0
  5. resolve conflicts once, here — setup.nsi is the expected site
  6. merge message: "Sync upstream 17.0 to <tag> (<date>); CASTADOO modifications
     staged <date>"                          ← discharges the LGPL dating obligation
  7. Gate 2 (diff budget), Gate 3 (brand lint)
  8. push origin 17.0 castadoo/17.0
```

**What a conflict is, and what "resolve once" means.** A conflict is a hunk where upstream
changed lines the overlay also changed, or lines adjacent enough that git cannot
three-way merge them. It is resolved by hand, in the overlay commit, with the upstream
change read first — the default of taking ours is prohibited, because on the 13 replaced
binaries and the three SVG files "ours" silently discards an upstream fix while looking
identical in review. The `.gitattributes` `merge=ours` rule (item 1b) is scoped to those
binaries and is a noise suppressor, not a licence to skip the read. Anything git merges
cleanly is reviewed by Gate 2's path list, not by eye.

**Step 2 is not ceremonial.** It is the only thing that distinguishes "I merged upstream"
from "I merged something", and it is the check that would have caught a mirror branch
drifting after a hand-resolved conflict. It is Gate 1 and it runs before the overlay merge,
because a wrong base invalidates everything after it.

Not every question in this document lands on a step here. Support-window (#1) decides
whether step 1 has anything to fetch; deployment shape (#3) decides whether Gate 3b's cost
repeats per database; bandwidth (#4) affects only the clone duration quoted in the runbook;
phone-home (#2), installer publisher (#5) and wordmark font (#6) change files, not steps.
Overlay activation (D7, now decided) adds one explicit `-i castadoo_branding_<new>` for a
release that introduces an overlay, and the rollout step that verifies the overlay set.

--------------------------------------------------------------------------------

## Alternatives Considered

The alternatives below fall into four groups: how the repository is obtained, how it is
kept in sync, which mechanism carries the branding, and how far the rebrand reaches. Every
one was weighed against a measurement rather than a preference, and several were rejected
because the measurement contradicted the premise they rested on.

### Repository acquisition

#### Alternative A: `--depth 75` shallow clone

*   **Pros**: Smallest possible transfer. No fork required. It was the cheapest option on
    paper, and 75 commits sounded like it would comfortably cover a year of 17.0 history.
*   **Cons**: The premise was false. Depth counts **commits**, not time: 75 commits on
    17.0 spans 34.5 days, while `16.0` — the branch the depth was chosen to reach — is
    four years back. Separately, `git push` refuses a shallow history outright
    (`! [remote rejected] (shallow update not allowed)`, reproduced against a local bare
    remote), and a shallow base destroys the merge base, so every subsequent point-release
    merge conflicts across every file.
*   **Reason for Rejection**: Rejected by author: the depth figure does not reach the
    intended history, and the shallow boundary makes both pushing and future merges
    impossible. It is not a smaller version of the chosen approach; it is incompatible
    with it.

#### Alternative B: Manual mirror pushed into `castaso/CASTADOO`

*   **Pros**: No dependence on GitHub's fork mechanics or org policy. Full control over
    which refs exist and in what order they arrive.
*   **Cons**: A single-branch 17.0 clone is ~4.76 GB against a GitHub-enforced 2 GB push
    limit, so it cannot be pushed in one operation. Progressive ref advancement can work
    but is a multi-hour, fragile procedure that must be babysat.
*   **Reason for Rejection**: Rejected by author: it is strictly more work than forking
    and has more ways to fail partway, leaving a half-populated repository that must be
    cleaned up before retrying.

#### Alternative C: Blobless clone of `odoo/odoo`, then push into the empty repo

*   **Pros**: Blobless clone is genuinely small, and it avoids any fork-network concerns
    during acquisition.
*   **Cons**: The blobs live only on the promisor remote. Materialising full history
    against a different, empty repository means the same ~17.7 GB transfer the approach
    was meant to avoid. The earlier local test of this idea was also invalid: the test
    remote printed `filtering not recognized by server, ignoring`, so bloblessness was
    never exercised.
*   **Reason for Rejection**: Rejected by author: the saving is an illusion once the
    destination is not the promisor. The surviving constraint is ordering — **fork first,
    then clone blobless from the fork** — which preserves the shared object store that
    makes the small clone possible.

#### Alternative D: Delete `castaso/CASTADOO` first, then fork into the freed name

*   **Pros**: Simplest sequencing on paper: free the name, create the fork, done. No
    rename step.
*   **Cons**: Destructive-first with no fallback. If fork creation fails — org policy, the
    fork-network restriction, name validation — there is no repository left and the name
    is unreserved during the gap for anyone to take.
*   **Reason for Rejection**: Rejected by author: the failure mode is unrecoverable, and
    the rename-then-fork sequence achieves the same result with the old repository intact
    as a fallback until the fork is verified.

### Sync model

#### Alternative E: Rebase the overlay, publishing immutable tags

*   **Pros**: Linear, readable history. `git log` on the overlay shows only CASTADOO
    commits, with no upstream noise.
*   **Cons**: Every commit SHA is rewritten on every point release, so any fork, pinned CI
    ref or submodule breaks at each sync. For an LGPL-3 work it also discards the
    modification provenance the licence asks you to keep, because history no longer shows
    what was changed when. The branch itself becomes unsupportable — only immutable
    annotated tags (`castadoo-17.0.<upstream>-r<n>`) can be published, and consumers must
    be forbidden from tracking the head.
*   **Reason for Rejection**: Rejected by author (decision D2): making the branch
    unpublishable is a worse default than a noisier graph, and the provenance loss is a
    compliance cost with no engineering benefit to offset it.

#### Alternative F: Patch series replayed onto a clean upstream tag at build time

*   **Pros**: Strongest auditability position — provable ancestry to a signed upstream
    tag, and the smallest possible conflict surface, since conflicts surface at replay
    rather than at merge.
*   **Cons**: Requires a build step before anything can be run, so a maintainer cannot
    simply clone and start a server. Managing a patch series over 89 `setup.nsi` lines plus
    36 other files is its own maintenance problem, and rebasing patches onto each upstream
    tag is the same conflict resolution work with less tooling.
*   **Reason for Rejection**: Rejected by author (decision D2): this plan produces a
    source tree, not a build pipeline, and introducing a mandatory build step to gain
    provenance that the merge-commit message already provides is a net loss.

### Branding mechanism

#### Alternative G: Edit every rendered file in place

*   **Pros**: Complete coverage by construction. No mechanism selection, no classification,
    no risk of an override failing to apply — if a string renders and you can find it, you
    replace it.
*   **Cons**: Guarantees divergence on exactly the lines upstream touches, making
    "pristine mirror" and "conflict-free sync" mutually exclusive. The real competitor is
    not "290 files" — that figure came from a grep that cannot distinguish `odoo_chart`
    from user-visible copy, and no count survives inspection. The competitor is an in-place
    edit of the roughly 30 files that actually render a brand string. Against that, the
    honest comparison is **rate rather than volume**: an inherited view carries an anchor
    that upstream may rename (loud failure at install), while an in-place edit carries a
    line that upstream may rewrite (silent, recurring, and merged without a conflict marker
    when the change is more than a few lines away).
*   **Reason for Rejection**: Rejected by author: it defeats the primary goal. The measured
    equivalent is 25 upstream paths and 103 edited lines, with 39 additive files that never
    touch an upstream path at all.

#### Alternative H: A single `castadoo_branding` addon depending on every touched module

*   **Pros**: One addon, one install step, no activation problem. Every override lands in
    one place, and there is no risk of a per-module overlay failing to auto-install (D7).
*   **Cons**: `depends` is not advisory. An inherited view whose parent XML ID is absent
    raises `External ID not found in the system` (`ir_model.py:2214`), so covering `sale`,
    `account`, `crm`, `hr_expense` and `mail` requires declaring all of them, and Odoo
    installs the whole chain. That forces roughly 15–25 business modules onto every
    database, including minimal and test ones.
*   **Reason for Rejection**: Rejected by author: the dependency cost lands on every
    deployment to save nothing that the two-tier split cannot save more cheaply. It is
    retained as option C under D7, because it is the simplest shape and the cost is
    confined to databases that should not be carrying those modules anyway.

#### Alternative I: Change `release.product_name` to `CASTADOO`

*   **Pros**: Appears to be the single most central branding string in the codebase. One
    line, and it looks like it renames the product everywhere.
*   **Cons**: It is not a display string. It has exactly one consumer —
    `odoo/tools/config.py:50` → `appdirs.user_data_dir()` — which computes the **default
    datadir**. Renaming it silently relocates every filestore, session directory and
    attachment, and Odoo creates an empty new one beside the old without an error. On
    Windows the path also includes `release.author`, which is why both fields are frozen.
*   **Reason for Rejection**: Rejected by author on measured evidence: this would have
    caused a data-visibility incident on the first upgrade. `product_name` is a directory
    name, and branding does not live in `release.py` at all. The one honest change there
    is `description`.

#### Alternative J: Retheme the backend to `#303188`

*   **Pros**: Full visual consistency — the whole interface in brand navy rather than Odoo
    purple with a navy favicon.
*   **Cons**: The tempting mechanism is an edit to `primary_variables.scss:73`, which reads
    `$o-brand-odoo: $o-community-color !default;`. That `!default` does **not** block a plain
    assignment in a later-loaded file: Odoo concatenates a dependent module's SCSS after
    `primary_variables.scss`, so a new file in an asset bundle owned by a branding module can
    set the variable without touching a single upstream file. The real cost of that route is
    the dependency it requires and the palette surface it then owns — every hardcoded purple
    elsewhere in the backend, of which this document has already catalogued three.
*   **Reason for Rejection**: Rejected by author on **scope**, not on mechanism: the backend
    palette is not one of the six named surfaces, and the dependency weight needed to reach
    it costs more than the surface is worth. The route exists and is recorded here so the
    rejection is not mistaken for a technical impossibility. The backend stays purple by
    decision.

#### Alternative K: A `post_init` migration rewriting the excluded `mail.template` bodies

*   **Pros**: Would remove the `Powered by Odoo` footer from the seven excluded records
    (portal invitation, portal welcome, account-created, badge, lunch supplier, lead
    forward, validation) without re-declaring them, leaving upstream's records intact for
    future syncs.
*   **Cons**: A database migration that mutates `body_html` in place has its own rollback
    hazard — there is no clean way to un-rewrite it, and a partial failure leaves bodies in
    an unknown state. It also creates permanent divergence at the data level rather than
    the declaration level, which is harder to audit.
*   **Reason for Rejection**: Rejected by author (decision D1-C): the accepted consequence
    is preferable to a mutation with no clean reversal. Recorded in
    `docs/change_register.md` §4b as an option, not a plan.

#### Alternative K2: Render-time post-processing via `mail.template._render_template`

*   **Pros**: This is the distinct third path that K's rejection does not cover, and the
    one a reader will otherwise assume was never considered. Odoo's extension point for
    template output is the model layer: subclass `mail.template`, override the render
    method, and post-process the resulting body. No data record is created, no
    `noupdate="1"` row is touched, no migration exists to fail — and the whole thing
    disappears on uninstall, which is the strongest rollback position of any option in this
    document. It also reaches the seven D1-C records *and* the four hardcoded-purple sites
    that `email_secondary_color` cannot reach, in one mechanism.
*   **Cons**: One small `models/` package living in an overlay that must depend on `mail`.
    It puts brand logic on the mail render path, so a bug there is a bug in every outgoing
    message rather than in one template — a materially worse failure mode than a wrong
    colour. It also operates on strings, so its correctness depends on the footer markup
    being recognisable after upstream edits it, which is the same silent-drift class the
    gates exist to catch and cannot, for runtime-composed output.
*   **Reason for deferral, not rejection**: D1-C **stands**. This design records K2 because
    the alternative list is otherwise incomplete, and because the colour finding makes it
    more attractive than the earlier draft assumed; but pricing it is a separate decision
    with its own risk statement, and adopting an unreviewed mechanism on the mail path to
    save seven footers is not a trade this document should make unilaterally. It is the
    named next step for D1-C if the leakage proves unacceptable in practice. Recorded in
    Future Improvements accordingly.

### Scope

#### Alternative L: Edit all readable text — help strings, tooltips, error messages, tours, doc links

*   **Pros**: No Odoo string anywhere a user can read. Removes the "accepted leakage" that
    this design documents.
*   **Cons**: Roughly 1,150 additional strings, each needing a human judgement on whether
    `Odoo` there means *this product* or *the software it derives from*. Getting that wrong
    is a trademark statement rather than a typo, and the judgement cannot be automated. It
    also removes the diff budget's meaning, since the register would no longer be
    enumerable.
*   **Reason for Rejection**: Rejected by author: unbounded cost with a legal-risk profile
    instead of a maintenance profile.

#### Alternative M: Edit the `.po` files containing `Odoo` in a `msgid`

*   **Pros**: The operator is Indonesian, so `id_ID` is plausibly a primary locale. Leaving
    it means Indonesian users read "Odoo" in the interface.
*   **Cons**: Renaming an English source string changes its `msgid`, which drops **every**
    locale back to the new English text until retranslated. That trades a partial brand
    leak for a total translation regression in every language — and it means editing a
    large share of the 19,459 translation files, each of which is an upstream-owned path.
*   **Reason for Rejection**: Rejected by author as a **recorded decision**, not a
    deferral: `.po` editing is out of scope for 17.0. The sanctioned route if it ever
    returns is stated positively in Future Improvements — a branding-module translation file
    that overrides `msgstr` only, never `msgid`, which fixes the localised surface without
    touching a single upstream translation file.

#### Alternative N: Re-declare the seven `mail.template` bodies to remove their footers

*   **Pros**: Removes the last customer-visible `Powered by Odoo` in the email surface,
    including the portal invitation and account-created mails.
*   **Cons**: Seven `noupdate="1"` records that must be re-checked whenever upstream edits
    them, in exchange for one line of boilerplate. The records are skipped on every module
    update including upstream's own (`odoo/models.py:5103`), so the cost is a standing
    review obligation rather than the data-loss trap an earlier draft claimed — but it is
    a standing obligation nonetheless.
*   **Reason for Rejection**: Rejected by author (decision D1-C): seven watched records for
    a footer line is a standing review obligation that outlives the benefit. The opposition
    is real and is stated rather than smoothed over — two of the seven are customer
    first-contact mail (portal invitation, account-created), so this is not a
    staff-facing-only surface and the accepted leakage sits on a named surface. It is
    documented in Non-Goals so it is not later reported as a defect, and K2 is the route if
    it becomes unacceptable.

#### Alternative O: Re-target the fork to 18.0 or 19.0

*   **Pros**: Builds on a series with a longer remaining maintenance window, which would
    make "sync at point releases" a live process for longer.
*   **Cons**: All measurements in this design are against 17.0 (`9c58cae5`, 40,111 files).
    Re-targeting invalidates the register, the surface enumeration and every count in it.
    It also does not address the underlying risk, only delays it.
*   **Reason for Rejection**: Rejected by author: 17.0 is confirmed, and re-targeting
    invalidates every measurement in this design. Raised as a standing risk in Open
    Question 1 rather than dismissed — if 17.0 Community is already at or past end of
    upstream maintenance, the sync premise weakens over time, and that is a fact to
    confirm rather than a preference to hold.

#### Alternative P: A separate branding repository on `addons_path`, no fork

*   **Pros**: This is the strongest shape on everything except one surface, and it deserves
    to be stated plainly rather than omitted. 39 of the 64 files are additive and never touch
    upstream, and another 16 are replacement blobs at existing paths — so a standalone addon
    repository on `addons_path` delivers the large majority of the rebrand with no fork, no
    merge ritual, no pristine-mirror goal, no `--no-ff` history and no CI diff budget. The
    nine in-place edits (eight paths plus one conditional) could ship as a patch file applied
    at build time, which is smaller than a whole branch model. It also removes the
    `castaso/CASTADOO` naming and trademark surface from the repository itself.
*   **Cons**: `setup/win32/setup.nsi` is not an addon. No `addons_path` entry reaches it, so
    a separate repository cannot brand the Windows installer by any mechanism — not by
    inheritance, not by configuration, not by overriding a model. Six of the six in-scope
    surfaces minus one is 83% of a rebrand with a customer-visible installer still saying
    Odoo, and the installer is the surface a customer sees *before* they see anything else.
    A patch file would close the gap but moves the fork's whole maintenance problem into an
    unversioned build step with worse tooling (Alternative F).
*   **Reason for Rejection**: Rejected by author, explicitly because Surface 5 is in scope.
    **This is the rejection that justifies the fork** — see Overview and Alternative Q. If
    the installer ever leaves scope, this alternative is the correct answer and roughly a
    third of this document should be deleted rather than amended.

#### Alternative Q: Defer Surface 5, ship the addon repository now and the installer later

*   **Pros**: Gets 83% of the rebrand in the first release, with none of the fork
    overhead — no blobless clone, no mirror branch, no merge ritual, no diff budget. The
    installer can be branded later, once the addon shape has proven itself in production and
    the effort estimate is real rather than modelled. It also removes the trademark
    question from the repository name in the interim.
*   **Cons**: The deferral has no natural end. Once the addon repository exists and works,
    the cost of *then* creating a fork is to migrate a live addon repository into a fork
    branch — re-doing acquisition, re-establishing the mirror, and re-justifying every
    decision in this document against a tree that has already diverged. The installer, in
    the meantime, is the first thing an installing customer reads.
*   **Reason for Rejection**: Rejected by author's Surface 5 decision. The consequence is
    recorded rather than argued: with Surface 5 deferred, the fork loses its only
    justification (Alternative P), so this is not a sequencing choice between two viable
    plans — it is a choice between the fork and no fork.

--------------------------------------------------------------------------------

## Non-Functional Requirements

Only the concerns that carry real risk for this design are listed. Generic concerns that
apply to any Odoo deployment are omitted deliberately.

### Security and privacy

*   **`publisher_warranty_url` is an outbound call by default.** `odoo/tools/config.py:78`
    sets `http://services.openerp.com/publisher-warranty/`, and Odoo contacts it daily with
    instance metadata. This is unchanged upstream behaviour, but a fork that markets itself
    as a distinct product inherits the expectation that it does not phone home. Whether to
    disable it is Open Question 2, and it is a policy decision, not a technical one.
*   **The database manager is unauthenticated by default.** `database_manager.qweb.html`
    line 33 says so in its own words, and it is reachable before login. Rebranding those
    four strings must not be read as making the surface safer. The mitigation is
    `list_db = False` and `admin_passwd` in deployment, and the deployment checklist below
    is a deliverable of this plan precisely so that mitigation stops being a reference to a
    document nobody writes.
*   **Brand strings sit in templates, not in secrets.** No credential **value** is modified
    by any file in this plan — no key, token or password is changed, generated or committed.
    The one credential-adjacent line is `DEFAULT_POSTGRESQL_PASSWORD 'openpgpwd'` at
    `setup.nsi:87`, the only instance in the tree. It ships in a product installer, and it
    is recorded here as an **accepted risk with a named mitigation**, not as a non-issue:
    the installer forces `admin_passwd` on first run, so the PostgreSQL default is never the
    credential that admits a remote actor to a configured instance. The earlier draft's
    objection — that changing it would break existing installs — does not apply, because
    this fork's install base is new installs by definition; CUJ 5 validates a clean VM.
    Changing the shipped default is E3, a release-process decision, and is not made here.
*   **Fork visibility.** Publishing the overlay branch exposes the diff, which is the point.
    It also discloses the exact set of unrebranded surfaces. That is acceptable for an LGPL
    derivative and is arguably required by the licence, but it is a disclosure decision.

### Performance and footprint

*   **Clone size.** The blobless clone of the fork measured 444 MB against a ~17.7 GB
    equivalent full history. The target is under 500 MB. Bandwidth for the initial clone is
    Open Question 4 and the two measurements disagree by ~34×, so no duration is quoted.
*   **Asset regeneration.** Regenerating the 11 committed binaries is a one-off build step,
    not a runtime cost. On a multi-database host it repeats per database at install time if
    assets are rebuilt; on a single-tenant install it is constant. This is why Open
    Question 3 matters.
*   **No runtime overhead.** Every in-scope mechanism is either configuration, a new file,
    or a replaced binary. Nothing adds a query, a hook on a hot path, or a per-request
    lookup. The one code path added is the user-menu registry patch, which runs once at
    client asset load.

### Rollout and rollback

**Rollout — an existing stock database moving to branded.** This is the path the earlier
draft did not describe, and it is the common case for a deployment that is already running.
At the specificity of the sync procedure:

```text
  1. deploy the branded tree, restart the service
  2. -i castadoo_branding                    # once, per database
       → its post_init_hook installs the matching overlays (D7-B)
  3. verify: which castadoo_branding_* are installed; any target module present
     without its overlay is a rollout failure, not a warning
  4. upload res.company.logo, set res.company.name       (deployment data, two values)
  5. verify the seeded three: web.web_app_name, email_secondary_color (mail only),
     website.favicon default via the replaced favicon.ico
  6. asset recompile on multi-database hosts; single-tenant needs none
  7. service-worker: manifest name and icons update on next launch; an already-cached
     offline page needs a client reinstall to change (see Asset pipeline)
  8. visual check of S1, S2, S6 — one page each
```

Step 3 is the gate the earlier design lacked: the failure mode D7-B exists to prevent is an
overlay that silently is not installed, and a checklist item is the only place to catch it.
Steps 4–5 are the five configuration values, split into the two that are genuinely
deployment data and the three that the tree now seeds.

**Rollback — what uninstalling actually restores, by mechanism.** An earlier draft claimed
that "22 of the items are new files or replaced binaries, so uninstalling restores stock".
That is false for the second of those two classes. Split by mechanism:

| Class | Count | Uninstall restores stock behaviour? |
|---|---|---|
| Additive — new files anywhere in the tree | 39 | **Yes.** Removing the addons removes those files and every inheritance with them. |
| Replaced binaries, same path (13 of the 16 in items 26–33) | 13 | **No.** The blob stays replaced; restoring means checking out the upstream path. |
| Replaced SVGs, text-diffed (`odoo-icon.svg` in item 26, both in item 30) | 3 | **No.** Same, and they conflict *inside* the file rather than at whole-file granularity. |
| In-place edits of upstream source (items 35–40) | 6 | **No.** `release.py`, `database_manager.qweb.html`, `webmanifest.py`, `setup.nsi`, `package.py`, `License.rtf` stay edited. |
| In-place edits of upstream prose (items 43, 44) | 2 | **No.** `README.md` and `CONTRIBUTING.md` keep the fork text. |
| Conditional in-place edit (item 41) | 0 or 1 | **No**, if it lands at all. |

So the non-reversible set is **16 replaced artefacts plus up to 9 edited upstream paths** —
not 4, and not one class. Anyone planning a rollback needs every row except the first, and
needs to know that the last one may not exist.

*   **Registry key changes are one-way in practice.** `DISPLAY_NAME` feeds
    `UNINSTALL_REGISTRY_KEY` (`setup.nsi:78`) and `REGISTRY_KEY` (`:82`), and `.onInit`
    reads the latter at `:466` to find a prior install. The first CASTADOO-named installer
    must therefore also look for the old key, or the previous install is orphaned. This
    must not be split across two patch releases.
*   **The service name stays `odoo-server-17.0`** (`release.py:37`,
    `setup.nsi:67`). Changing it would orphan every installed service, and the new
    uninstaller would have nothing to remove.

### Deployment checklist (a third deliverable)

The rebrand is partly deployment data, and every CI gate is blind to a database. Rather
than leave the controls as references to a runbook that no item produces, this plan ships
**`docs/deployment-checklist.md`** as a deliverable, alongside the source tree and the
register. Its content is:

*   `admin_passwd` forced to a non-default value before the instance is reachable.
*   `list_db = False` unless the database manager is deliberately exposed.
*   `proxy_mode = True` behind TLS, with `web.base.url` set to the real origin.
*   `publisher_warranty_url` — the D3 decision (Open Question 2), stated as an action rather
    than left as the current silence.
*   Database backup: location, schedule, and **a named backup maintainer** (E1).
*   `addons_path` with `castadoo/` **first**, before the upstream addons directory.
*   `git config merge.ours.driver true` in the clone, or the `merge=ours` rules in item 1b's
    `.gitattributes` degrade to a normal merge and every replaced binary conflicts. This is
    repo-local config, not a tracked file, which is exactly why it needs a checklist line.
*   For a release that **adds** an overlay: an explicit `-i castadoo_branding_<new>`, then
    the step-3 verification below. `-u` does **not** re-run `post_init_hook` (measured:
    `loading.py:178`), so this is the only route for a target module that is already
    installed.
*   The rollout steps above, in order — including step 3, which asserts that every installed
    target module has its overlay installed.

Three of those checklist lines are decisions this document cannot make: E1 (deployment platform
and **a named backup maintainer**), E2 (the phone-home default, Open Question 2) and E3 (the
installer's superuser password policy, accepted risk until decided). The checklist ships with
them named and marked `DECISION REQUIRED`, so the deliverable is complete and its gaps are
visible rather than absent. The fourth escalation, E4, is a legal question about the mark and
does not appear here because no deployment step answers it.

--------------------------------------------------------------------------------

## Additional Resources

*   `docs/designs/concepts_brief.md` — the predecessor brief from the brainstorm phase. Every
    measurement in this design traces back to it, and it records every open question in its
    original framing.
*   `castadoo/change_manifest.toml` → `docs/change_register.md` — the per-line enumeration of
    all six surfaces, plus the decision sheet. The manifest is the source; the register is its
    rendering (item 45). The register is committed; the manifest and its renderer are not yet.
*   `docs/designs/reviews/` — the five stage reports and the consolidated review, plus
    `reviews/goldfish_review_report.md`, which records what happened to each finding. Cited
    here as provenance for the repairs, not as current guidance.
*   `docs/designs/verified_ground_truth.md` and `docs/designs/anchor_verification.md` — the
    citations that were checked against the 17.0 tree, including the seven the draft had
    wrong. `docs/designs/design_draft.md` is the superseded pre-review draft.
*   Odoo 17.0 source at `9c58cae5d6e3cf91ac1cca7df39fb21f68ca6e15`, read directly for line
    numbers. The files cited most often: `odoo/addons/base/models/ir_module.py`
    (auto-install logic), `odoo/modules/loading.py` (hook calls),
    `odoo/models.py:5103` (`noupdate` handling), `odoo/tools/config.py:50` (datadir),
    `addons/web/views/webclient_templates.xml` (backend shell),
    `addons/web/static/src/service_worker.js` (the PWA cache),
    `setup/win32/setup.nsi` (installer).
*   `C:\Users\Yongky\Dropbox\Sandbox\logo.svg` — the CASTADOO mark source (89.94 × 110.97,
    `#303188` navy + `#FAA61A` orange).
*   `C:\Users\Yongky\Dropbox\Sandbox\CASTADOO.svg` — the wordmark source (683.22 × 107.6,
    live Garamond `<text>` nodes that must be outlined).
*   GNU LGPL-3.0, the licence the fork inherits and cannot change.

## Future Improvements

*   **The idea**: A `msgstr`-only `.po` overlay for `id_ID`.
    **What it fixes**: Indonesian users currently read English strings that say "Odoo".
    Renaming `msgid`s would drop every language back to new English text, so the safe form
    is a branding-module translation file that overrides only `msgstr`, never `msgid`.
*   **The idea**: D1-C's leakage closed by **render-time post-processing** (Alternative K2),
    not by the `post_init` rewrite this entry used to name.
    **What it fixes**: Portal-invitation and account-created mails keep a `Powered by Odoo`
    footer under D1-C, and four sites keep a hardcoded purple. A model-layer override of
    `mail.template`'s render path reaches both without re-declaring a record and is
    reversible by uninstall. It is deferred, not rejected — the risk is that it puts brand
    logic on the path of every outgoing mail.
*   **The idea**: Backend retheme to `#303188` via a new SCSS file in a branding module's
    asset bundle.
    **What it fixes**: The backend stays Odoo purple. The mechanism exists (see
    Alternative J — `!default` does not block a later-loaded file), so this is a scope
    decision that could be revisited rather than a technical dead end.
*   **The idea**: Automate asset regeneration in CI rather than committing binaries.
    **What it fixes**: The committed binaries are outputs with no automated provenance. A CI
    job would prove the assets match their sources, at the cost of a rasteriser dependency in
    the build.
*   **The idea**: Extend the gate from grep patterns to rendered-output assertions.
    **What it fixes**: Grep catches strings in files; it cannot see a string composed at
    runtime, which is exactly how `web.web_app_name` and the PDF title are assembled. A
    headless render of the six surfaces would be a stronger gate than Gate 3b as written.

--------------------------------------------------------------------------------

## Detailed Implementation Plan

Every file below carries four fields: **Action** (Create / Modify / None), **Type / Scope**,
**Proposed Changes** and **Gate** (which check covers it). Line numbers are from the 17.0 tip
`9c58cae5d6e3cf91ac1cca7df39fb21f68ca6e15`. No production code is written here. Item 7's
hook is given as code because it is a shape, not an implementation; the other items give the
literals to write. Where an item says a choice remains, it names the open decision it
belongs to, and those are counted in §Open Questions rather than left to be discovered.

**Placement decision.** All new addons live in a new top-level `castadoo/` directory. This
requires **one** `addons_path` entry, which the deployment supplies (see item 42). The
alternative — placing them under the existing `addons/` — needs no config but mixes product
code into upstream's directory and shows up in every `git diff` of `addons/`. Since
`module.get_module_path` returns the **first** addons path containing a module
(`odoo/modules/module.py:165`), `castadoo/` being first also guarantees an upstream addon
can never shadow these.

**The wiring rule that applies to every addon below.** Odoo loads a module through its
manifest, and an empty manifest installs cleanly and does nothing. Two keys are therefore
load-bearing and are stated per item rather than assumed:

*   `'data': [...]` — XML views are parsed only if they are listed. A view file created and
    never listed is inert; the module still installs, and Gate 3 still greps the file and
    finds it branded. This is the design's own failure mode, mechanised in the manifest.
*   `'assets': {...}` — `static/src/**` is *served*, not loaded. JS and Owl templates reach
    the browser only through a named bundle.

### Target Files to Create/Modify

The headings below group the 47 numbered items (50 entries, counting the three suffixed items
`1a`, `1b` and `22a`) by mechanism tier so the conflict surface is visible at a glance. The grouping
is a rendering of four manifest fields — `upstream_owned`, `conflict_surface`,
`reversible_by_uninstall`, `counts_against_budget` — and the tier names are conveniences over
those columns, not an ordinal scale. A reader who needs to know whether an item is counted
should read the column, not the heading.

### Tier 1 — base addon `castadoo_branding`

#### 1. `castadoo/castadoo_branding/__manifest__.py` (Create)

*   **Action**: Create.
*   **Type / Scope**: Odoo addon manifest.
*   **Proposed Changes**: `name` = "CASTADOO Branding", `depends: ['web']` only,
    `auto_install: False` (explicitly installed by the deployment), `license: 'LGPL-3'`,
    `author` recording both CASTASOFT and the upstream derivation. `application: False` so
    it does not appear as a top-level app. The `depends` list is the load-bearing part: it
    must contain `web` and nothing else, or the dependency-drag problem in Alternative H
    returns. Three further keys:

    ```python
    'data': [
        'views/webclient_templates.xml',
        'views/offline_templates.xml',
        'views/report_templates.xml',
        'data/ir_config_parameter.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'castadoo_branding/static/src/user_menu/castadoo_user_menu.js',
        ],
    },
    'post_init_hook': 'post_init_hook',
    ```

    The `data` key is not optional decoration: without it, 14 view files across the nine
    addons are created and never parsed. `addons/account_payment/__manifest__.py:9` shows
    `'auto_install': ['account']` immediately followed by `'data': [...]`, so the omission in
    the earlier draft was an omission, not a convention. `post_init_hook` is D7-B.
*   **Gate**: Gate 3a (pathlint) plus the install-time smoke test — a manifest omission fails
    no grep, which is why the smoke test exists.

#### 1a. `castadoo/castadoo_branding/data/ir_config_parameter.xml` (Create)

*   **Action**: Create.
*   **Type / Scope**: Seeded configuration — the one configuration value that cannot be left
    to deployment.
*   **Proposed Changes**: The `web.web_app_name` record shown in the data model, matching the
    stock `<odoo noupdate="1">` shape. Without it a correctly built tree on a fresh database
    serves a manifest named `Odoo`, because `webmanifest.py:48` falls back to `'Odoo'` when
    the parameter is absent. Listed in item 1's `data` key.
*   **Gate**: Tier A manifest assertion (`name == 'CASTADOO'` on a fresh database). No grep
    can see a database value; this is the assertion that covers the gap.

#### 1b. `.gitattributes` at the repository root (Create)

*   **Action**: Create.
*   **Type / Scope**: Merge driver configuration. Upstream-owned path that **does not exist
    in the 17.0 tree** — measured, `git cat-file -p e57daa52:.gitattributes` returns
    "path does not exist" — so this is an addition, not an edit, and it counts as additive.
*   **Proposed Changes**: The mechanism this design mandates in three places (Tier 3
    introduction, the sync procedure's conflict paragraph, and G7) had no item that created
    it. This is that item. Content is one line per replaced binary:

    ```gitattributes
    # CASTADOO: replaced branding binaries. Conflicts on these paths are resolved by
    # inspecting the upstream change, then taking the fork's blob; merge=ours suppresses
    # the whole-file conflict that binary paths otherwise produce.
    addons/web/static/img/*.png merge=ours
    addons/web/static/img/*.ico merge=ours
    addons/web/static/img/*.jpg merge=ours
    setup/win32/static/pixmaps/*.ico merge=ours
    setup/win32/static/pixmaps/*.bmp merge=ours
    ```

    It is scoped by glob to the binary directories rather than by explicit path list, so a
    new upstream icon in those directories is covered without a manifest edit — the failure
    direction this design prefers, because a missing rule produces a loud conflict while a
    stale rule produces a silent takeover of a file the fork owns anyway.

    The three SVGs are deliberately **not** listed: `odoo_logo.svg`,
    `odoo_logo_dark.svg` and `odoo-icon.svg` are XML, git diffs them line by line, and
    `merge=ours` on a text path would silently discard upstream edits inside the file. They
    are `modify-text` in the manifest and are resolved by hand.

    `merge=ours` requires the driver to be configured, or git falls back to a normal merge.
    The rule is therefore paired with one repo-local config line, which the deployment
    checklist states: `git config merge.ours.driver true`.
*   **Gate**: none directly. Its effect is observable only at merge time, and the sync
    procedure's conflict step is where a missing driver surfaces — as a conflict that
    should not have appeared.

#### 2. `castadoo/castadoo_branding/__init__.py` (Create)

*   **Action**: Create.
*   **Type / Scope**: Package init.
*   **Proposed Changes**: Exactly one line, `from . import hooks`. There is no `models`
    package in this addon — the earlier draft's import of one would raise `ImportError` at
    module load, and the base tier is deliberately model-free so it can depend on `web`
    alone. The hook module exists unconditionally under D7-B; if D7 were ever revisited, this
    line and the `post_init_hook` key are the only two places to change.
*   **Gate**: install-time smoke test.

#### 3. `castadoo/castadoo_branding/views/webclient_templates.xml` (Create)

*   **Action**: Create.
*   **Type / Scope**: QWeb view inheritance, base tier.
*   **Proposed Changes**: Four inherited records, all `inherit_id` + `<xpath>`:
    *   `web.layout` → `//title` → replace the `t-esc` fallback `'Odoo'` with
        `'CASTADOO'` (targets `addons/web/views/webclient_templates.xml:22`). The parent's
        external id is **`web.layout`**: `:17` declares `id="layout"`, so `web.web_layout`
        would raise `External ID not found` at install.
    *   `web.brand_promotion_message` → the `<img>` at line 94–95 → set `alt` to
        CASTADOO and `src` to the replaced `odoo_logo_tiny.png`; the anchor `href` at
        line 92 must point at the CASTASOFT site, not `odoo.com`.
    *   `web.login_layout` → the footer anchor at line 130 → set `href` to the CASTASOFT
        site and replace the `Powered by <span>Odoo</span>` text with CASTADOO.
    *   `web.webclient_bootstrap` → `<meta name="theme-color">` at line 251 → set
        `content` to `#303188`. Note the stock value is `#71639e`, a third purple
        inconsistent with the brand `#714B67`; the replacement resolves that
        inconsistency rather than matching it.
*   **Gate**: install-time smoke test (a wrong `inherit_id` fails loudly at install) plus
    Gate 3a.

#### 4. `castadoo/castadoo_branding/views/offline_templates.xml` (Create)

*   **Action**: Create.
*   **Type / Scope**: QWeb inheritance for the offline page.
*   **Proposed Changes**: Three inherited records on `web.webclient_offline`
    (`addons/web/views/webclient_templates.xml:285`):
    *   the `<img>` `alt` at line 330 → `CASTADOO`;
    *   the paragraph at line 332 → text with no `Odoo` in it;
    *   the `.card button` colour. The inline `<style>` block at lines 293–326 carries
        `background-color: #714B67` at line 317 and `border: 1px solid #714B67` at line 319.

    The colour is the fragile part, and the mechanism is **decided, not left to the
    implementer**: append a new `<style>` rule after the existing block that redeclares
    `.card button`'s background and border, rather than replacing the block's contents.
    Replacing the content is self-contained but breaks silently on any upstream CSS edit
    inside those 34 lines; an appended rule survives upstream reordering and fails visibly
    if the selector changes. It is also the only one of the two that the Tier A
    computed-style assertion can distinguish, which is why that assertion reads
    `getComputedStyle` rather than the stylesheet source.
*   **Gate**: Gate 3a plus the `browser_js` computed-style assertion (Tier A).

#### 5. `castadoo/castadoo_branding/views/report_templates.xml` (Create)

*   **Action**: Create.
*   **Type / Scope**: QWeb inheritance for PDF metadata.
*   **Proposed Changes**: Two inherited records, because upstream declares the same string
    twice in two separate templates:
    *   `web.report_layout` → `<title>` at `report_templates.xml:16`;
    *   `web.report_preview_layout` → `<title>` at `report_templates.xml:50`.
    Both replace `title or 'Odoo Report'` with a CASTADOO fallback. Sharing one `<xpath>`
    between two parents is not possible. This is metadata only; the visible header is
    `res.company` data, which the deployment checklist supplies.
*   **Gate**: install-time smoke test plus a PDF text extraction in the post-deploy tier.

#### 6. `castadoo/castadoo_branding/static/src/user_menu/castadoo_user_menu.js` (Create)

*   **Action**: Create.
*   **Type / Scope**: Owl/JS registry patch, loaded through `web.assets_backend` (item 1).
*   **Proposed Changes**: Patches the `user_menuitems` registry to remove the
    `odoo_account` entry and handle the `documentation` entry. Two distinct problems in one
    file:
    *   `odoo_account` — registered at
        `addons/web/static/src/webclient/user_menu/user_menu_items.js:128` as
        `.add("odoo_account", odooAccountItem)`, so **`odoo_account` is the registry key**;
        the item's own `id: "account"` at `:91` is a different string and is not what the
        registry is addressed by. Its `description` is the literal `"My Odoo.com account"`
        (`:92`) and its callback calls `/web/session/account` and opens the returned URL,
        falling back to `https://accounts.odoo.com/account` on failure (`:94–101`) —
        both routes lead to Odoo's own account service. Removal
        is the honest option: the account it points at is Odoo's, and a CASTASOFT customer
        has no account there. A renamed entry that still opens an Odoo URL is worse than no
        entry. The 17.0 registry API is `registry.category("user_menuitems").remove("odoo_account")`
        — `remove(key)` is defined at `addons/web/static/src/core/registry.js:122`. There is
        no `?` on it.
    *   `documentation` — `documentationURL` is
        `"https://www.odoo.com/documentation/17.0"` (line 12). **Decided: the entry stays,
        pointing where it points.** The reasoning is that this is the one place where the
        Odoo name is *accurate* rather than a leak — the documentation at that URL documents
        the software this fork actually is, and a customer following it gets correct
        answers. Repointing at a CASTASOFT copy that does not exist ships a broken menu;
        removing it deletes a working link to the product's own manual. The item carries an
        allowlist reason of `upstream documentation, accurate for this product` so Gate 3b
        does not fail on `www.odoo.com` here. If a CASTASOFT-hosted mirror ever exists, this
        is the one line to change.
*   **Gate**: Gate 3a. The removal of `odoo_account` is asserted by a `browser_js` test
    (Tier A); the retained `documentation` entry is a named allowlist record.

#### 7. `castadoo/castadoo_branding/hooks.py` (Create)

*   **Action**: Create.
*   **Type / Scope**: Module hook — D7 option B.
*   **Proposed Changes**: The signature and the reload hazard are the whole content of this
    item, so both are given as code rather than prose. In 17.0 the loader calls the hook with
    a single `env` argument (`odoo/modules/loading.py:245`):

    ```python
    # castadoo/castadoo_branding/hooks.py
    import logging

    _logger = logging.getLogger(__name__)

    # upstream module -> overlay that brands it. Keeping this table here, and not in
    # nine manifests, is what covers the migration case: a target module that was
    # already installed before castadoo_branding existed.
    _OVERLAYS = {
        'mail': 'castadoo_branding_mail',
        'auth_signup': 'castadoo_branding_auth_signup',
        'portal': 'castadoo_branding_portal',
        'im_livechat': 'castadoo_branding_im_livechat',
        'hr_expense': 'castadoo_branding_hr_expense',
        'digest': 'castadoo_branding_digest',
        'website_slides': 'castadoo_branding_website_slides',
        'point_of_sale': 'castadoo_branding_pos',
    }

    def post_init_hook(env):
        """Mark an overlay for install wherever its target module is already installed.

        Runs once, on first install of castadoo_branding. Not on -u: the loader gates
        the call on new_install (loading.py:178, :243-247).
        """
        Module = env['ir.module.module']
        installed = set(
            Module.search([('state', '=', 'installed')]).mapped('name')
        )
        to_install = Module.browse()
        for target, overlay in _OVERLAYS.items():
            if target not in installed or overlay in installed:
                continue
            overlay_module = Module.search([('name', '=', overlay)])
            if not overlay_module:
                # overlay absent from addons_path: report, do not raise. A missing
                # overlay is a deployment defect the rollout check surfaces, not an
                # error that must abort the install of the base addon.
                _logger.warning(
                    "castadoo_branding: %s is installed but %s was not found on "
                    "addons_path; that surface will stay unbranded.",
                    target, overlay)
                continue
            to_install |= overlay_module
            _logger.info("castadoo_branding: marking %s for install (%s present)",
                         overlay, target)
        if to_install:
            # button_install(), not button_immediate_install(): the immediate variant
            # raises UserError while the registry is initialising (ir_module.py:591)
            # and RuntimeError inside tests (ir_module.py:594). button_install only
            # marks the modules 'to install'; the loader's STEP 3 loop re-queries
            # that state and loads them (loading.py:479-487).
            to_install.button_install()
    ```

    Three properties are load-bearing and each is a way this code fails if changed:
    **idempotent** (`overlay in installed` guard, so re-running over a partially-branded
    database does not re-install), **non-fatal** (a missing overlay logs and continues —
    raising here would make the base addon uninstallable on a deployment that ships it
    without an overlay), and **non-immediate** (see the comment; `_button_immediate_function`
    at `ir_module.py:590` raises `UserError` when
    `not self.env.registry.ready or self.env.registry._init`, and raises `RuntimeError`
    outright when `threading.current_thread().testing` is set, at `:594`).

    **The residual gap, and why `button_install()` is the right call.** Two facts measured
    in the tree, both of which change what the deployment must do:

    *   `post_init_hook` fires **only on first install**. `odoo/modules/loading.py:178`
        sets `new_install = package.state == 'to install'`, and the call at `:243–247` is
        guarded by `if needs_update: if new_install:`. An upgrade therefore does **not**
        re-run the hook, whatever the version bump says.
    *   `button_install()` only **marks** modules — it calls `_state_update('to install', …)`
        at `ir_module.py:427` and returns an action dict. It does not itself load them. The
        loader's STEP 3 loop (`loading.py:479–487`) then picks up everything in state
        `to install`, which is why a plain `button_install()` from inside a hook reaches
        the overlays: they are loaded by the same outer loop that will re-read the graph.
        Calling `_button_immediate_install` here instead would nest a whole load inside the
        current one and raise (`ir_module.py:590`).

    The gaps that remain, and their covers: a target module installed *before* the base
    addon is covered (the hook sees `installed` and marks the overlay); a target module
    installed *after* is covered (`auto_install` fires on `to install`); an overlay **added
    to a later release** for an already-installed target is **not** covered, and needs one
    explicit `-i castadoo_branding_<new>` in that release's deployment step. The version
    bump is still required, but for the module's own data files, not to re-run the hook.
*   **Gate**: the install-time smoke test and the rollout step 3 check — both of which assert
    the overlay set, because no gate can see a database.

### Tier 2 — per-module overlays

Each overlay is one manifest, one `__init__.py` and one view file. All are `Create`, all are
additive, and all follow the same shape: `depends: ['castadoo_branding', '<module>']`,
`auto_install: ['<module>']`, `'data': ['views/<name>.xml']`, one inherited record. The
`auto_install` list form is stock practice (`addons/account_payment/__manifest__.py:9` uses
`['account']`).

**The eight `__init__.py` files are one item, not eight.** Every overlay directory needs an
empty `__init__.py`, or Odoo does not see the directory as a module and it never appears in
the apps list — silently, since nothing is declared and nothing fails. The files are
byte-identical and contain nothing; they are listed here once so the register is not
inflated by eight rows that say the same thing (this is item 22a, and it is the one item
that spans every Tier-2 directory).

#### 8. `castadoo/castadoo_branding_mail/__manifest__.py` (Create)

*   **Action**: Create.
*   **Type / Scope**: Overlay manifest — highest-traffic overlay.
*   **Proposed Changes**: `depends: ['castadoo_branding', 'mail']`,
    `auto_install: ['mail']`, `'data': ['views/mail_templates_email_layouts.xml']`, plus the
    `email_secondary_color` seed described in the data model — this overlay is the only
    place that field exists, because it is a `mail` field.
*   **Gate**: install-time smoke test; Gate 3a.

#### 9. `castadoo/castadoo_branding_mail/views/mail_templates_email_layouts.xml` (Create)

*   **Action**: Create.
*   **Type / Scope**: QWeb inheritance on the notification-email footers.
*   **Proposed Changes**: Two inherited records:
    *   `mail.mail_notification_layout` → the footer `<div>` at
        `addons/mail/data/mail_templates_email_layouts.xml:103–109`. Replace the
        `href` `https://www.odoo.com?utm_source=db&utm_medium=email` and the anchor text
        `Odoo` on lines 104–105. The anchor's inline `t-att-style` already reads
        `company.email_secondary_color or '#875A7B'` — leave that expression intact, so the
        company setting still drives the colour, and set the field instead of hardcoding
        navy here.
    *   `mail.mail_notification_light` → the same footer at lines 177–183.
    These two carry the footer under every internal notification. Note both live in a `data/`
    file but are `<template>` QWeb views, not `mail.template` records — that distinction is
    why they are inheritable at all.
*   **Gate**: Gate 3a; a `MailCase` render assertion (Tier A) rather than a grep.

#### 10. `castadoo/castadoo_branding_auth_signup/__manifest__.py` (Create)

*   **Action**: Create.
*   **Type / Scope**: Overlay manifest.
*   **Proposed Changes**: `depends: ['castadoo_branding', 'auth_signup']`,
    `auto_install: ['auth_signup']`, `'data': ['views/auth_signup_templates_email.xml']`.

#### 11. `castadoo/castadoo_branding_auth_signup/views/auth_signup_templates_email.xml` (Create)

*   **Action**: Create.
*   **Type / Scope**: QWeb inheritance, four anchors across **two** templates.
*   **Proposed Changes**: Measured at
    `addons/auth_signup/views/auth_signup_templates_email.xml`: `reset_password_email` is
    declared at `:3` and carries its button colour at `:36` and its footer at `:81`;
    `alert_login_new_device` is declared at `:88` and carries the same two at `:122` and
    `:143`. That is **four sites and two parents**, so two inherited records are the
    minimum and four if button and footer are anchored separately — one `<xpath>` cannot
    span two templates. Each footer hardcodes `style="color: #875A7B;"` **inline**, so
    unlike item 9 these do not honour `company.email_secondary_color` and the colour must be
    replaced in the markup as well as the text and `href`.
*   **Gate**: Gate 3a; MailCase render assertion.

#### 12. `castadoo/castadoo_branding_portal/__manifest__.py` (Create)

*   **Action**: Create.
*   **Type / Scope**: Overlay manifest.
*   **Proposed Changes**: `depends: ['castadoo_branding', 'portal']`,
    `auto_install: ['portal']`, `'data': ['views/portal_templates.xml']`.

#### 13. `castadoo/castadoo_branding_portal/views/portal_templates.xml` (Create)

*   **Action**: Create.
*   **Type / Scope**: QWeb inheritance.
*   **Proposed Changes**: One inherited record on `portal.portal_record_sidebar`, line 288
    of `addons/portal/views/portal_templates.xml`. Note this is a sidebar in the portal
    *web* UI, not an email — the register lists it under Surface 4 because the string is
    identical, but the anchor is a page element.

#### 14. `castadoo/castadoo_branding_im_livechat/__manifest__.py` (Create)

*   **Action**: Create.
*   **Type / Scope**: Overlay manifest.
*   **Proposed Changes**: `depends: ['castadoo_branding', 'im_livechat']`,
    `auto_install: ['im_livechat']`, `'data': ['views/im_livechat_templates.xml']`.

#### 15. `castadoo/castadoo_branding_im_livechat/views/im_livechat_templates.xml` (Create)

*   **Action**: Create.
*   **Type / Scope**: QWeb inheritance, two different parents.
*   **Proposed Changes**: Two inherited records: `im_livechat.livechat_email_template`
    (line 91 of `addons/im_livechat/data/mail_templates.xml`) and
    `im_livechat.support_page` (line 79 of
    `addons/im_livechat/views/im_livechat_channel_templates.xml`). One parent is a data
    template, one is a web view; both are QWeb, so one file can carry both records.

#### 16. `castadoo/castadoo_branding_hr_expense/__manifest__.py` (Create)

*   **Action**: Create.
*   **Type / Scope**: Overlay manifest.
*   **Proposed Changes**: `depends: ['castadoo_branding', 'hr_expense']`,
    `auto_install: ['hr_expense']`, `'data': ['views/hr_expense_templates.xml']`.

#### 17. `castadoo/castadoo_branding_hr_expense/views/hr_expense_templates.xml` (Create)

*   **Action**: Create.
*   **Type / Scope**: QWeb inheritance, **two** parents in one file.
*   **Proposed Changes**: Measured at `addons/hr_expense/data/mail_templates.xml`:
    `hr_expense_template_register` is declared at `:11` and its button carries
    **`style="color:#9E588B;"` at `:31`**; `hr_expense_template_register_no_user` is declared
    at `:35` and its footer carries the same literal at `:49`. So this is **two inherited
    records**, not one: the button and the footer are in different templates. `#9E588B` is a
    fourth purple, distinct from `#714B67`, `#71639e` and `#875A7B`, and not reachable from
    `email_secondary_color`. Replacing `#875A7B` everywhere would miss this file entirely,
    which is why it is called out per-site rather than covered by the company setting — and
    why both anchors, not just the footer, are in the register.
*   **Gate**: Gate 3a. The `#9E588B` literal is a lint pattern precisely because it appears
    nowhere else.

#### 18. `castadoo/castadoo_branding_digest/__manifest__.py` (Create)

*   **Action**: Create.
*   **Type / Scope**: Overlay manifest.
*   **Proposed Changes**: `depends: ['castadoo_branding', 'digest']`,
    `auto_install: ['digest']`, `'data': ['views/digest_templates.xml']`.

#### 19. `castadoo/castadoo_branding_digest/views/digest_templates.xml` (Create)

*   **Action**: Create.
*   **Type / Scope**: QWeb inheritance, **two parents** — and the earlier draft named the
    wrong one for the colours.
*   **Proposed Changes**: Measured at `addons/digest/data/digest_data.xml`:
    *   **`digest.digest_mail_layout`** is declared at `:5` and holds the colour machinery:
        `:14` defines `color_company = company.email_secondary_color or '#714B67'`, and
        `:58`, `:87`, `:147` apply it. **All colour anchors are here, not in `digest_mail_main`.**
    *   **`digest.digest_mail_main`** spans `:270–451` and holds the two footers:
        `:398` `Sent by <a href="https://www.odoo.com"…><span class="odoo_link_text">Odoo</span></a>`,
        and `:436` `Powered by <a href="https://www.odoo.com"…>…</a>`.
    Both footers are needed: a single-line grep for `Powered by` finds only the second,
    because the first says `Sent by`. They are in one template but are separate anchors, and
    the colour is in a third place — so this item is two records over two parents.
    Keep the classes `odoo_link` / `odoo_link_text`; they are styling hooks, not branding.
    No colour edit is needed at all: setting `email_secondary_color` reaches this file with
    zero source changes (S4.10/S4.20 in the register), and the fallback here is `#714B67`,
    the 17.0 brand purple, not `#875A7B`.
*   **Gate**: Gate 3a; MailCase render assertion.

#### 20. `castadoo/castadoo_branding_website_slides/__manifest__.py` (Create)

*   **Action**: Create.
*   **Type / Scope**: Overlay manifest.
*   **Proposed Changes**: `depends: ['castadoo_branding', 'website_slides']`,
    `auto_install: ['website_slides']`, `'data': ['views/website_slides_templates.xml']`.

#### 21. `castadoo/castadoo_branding_website_slides/views/website_slides_templates.xml` (Create)

*   **Action**: Create.
*   **Type / Scope**: QWeb inheritance.
*   **Proposed Changes**: One inherited record on
    `website_slides.mail_notification_channel_invite`, lines 67–70 of
    `addons/website_slides/data/mail_templates.xml`. The colour here is a hardcoded
    `style="color: #875A7B;"` rather than a `t-att-style` expression, so unlike item 9 it
    must be replaced in the markup — setting `res.company.email_secondary_color` does not
    reach it.

#### 22. `castadoo/castadoo_branding_pos/__manifest__.py` (Create)

*   **Action**: Create.
*   **Type / Scope**: Overlay manifest for Owl asset templates.
*   **Proposed Changes**: `depends: ['castadoo_branding', 'point_of_sale']`,
    `auto_install: ['point_of_sale']`, plus the bundle membership the Owl files need.
    Measured: 17.0 declares **`point_of_sale.assets_prod`** and
    **`point_of_sale.assets_qunit_tests`**; there is no `point_of_sale.assets` key in the
    tree, so naming one would produce a silent no-op:

    ```python
    'assets': {
        'point_of_sale.assets_prod': [
            'castadoo_branding_pos/static/src/overrides/receipt.xml',
            'castadoo_branding_pos/static/src/overrides/customer_display.xml',
            'castadoo_branding_pos/static/src/overrides/odoo_logo.js',
            'castadoo_branding_pos/static/src/overrides/odoo_logo.xml',
        ],
    },
    ```

    This overlay is **required**, not optional: without it the POS receipt still reads
    `Powered by Odoo`. What was optional in earlier drafts was the logo *component* rename
    (item 25), not the overlay.

#### 22a. Eight overlay `__init__.py` files (Create)

*   **Action**: Create.
*   **Type / Scope**: Package initialisers — `castadoo_branding_mail`,
    `_auth_signup`, `_portal`, `_im_livechat`, `_hr_expense`, `_digest`, `_website_slides`,
    `_pos`.
*   **Proposed Changes**: Eight empty files, one per overlay directory. Without them the
    directory is not a module: Odoo finds no package, the addon never appears in the apps
    list, and `auto_install` has nothing to install. The failure is silent in the tree —
    Gate 2 counts the directory's files as present and Gate 3 greps them as branded.
*   **Gate**: install-time smoke test. This item exists because no gate can see it.

#### 23. `castadoo/castadoo_branding_pos/static/src/overrides/receipt.xml` (Create)

*   **Action**: Create.
*   **Type / Scope**: Owl `t-inherit` template, bundled via `point_of_sale.assets_prod`.
*   **Proposed Changes**: Inherit `point_of_sale.OrderReceipt`. Parent stated explicitly
    because Owl inheritance fails **silently** if the name is wrong: it does not raise, it
    simply does not apply. Measured: `t-name="point_of_sale.OrderReceipt"` is declared at
    `addons/point_of_sale/static/src/app/screens/receipt_screen/receipt/order_receipt.xml:3`,
    and the footer `<p>Powered by Odoo</p>` is at `:140`. A wrong parent here leaves a
    printed receipt reading Odoo, and no gate can see it — this is why the verification
    plan carries a POS print check rather than only a browser check.
*   **Gate**: none automated. Manual POS receipt print, listed in the verification plan.

#### 24. `castadoo/castadoo_branding_pos/static/src/overrides/customer_display.xml` (Create)

*   **Action**: Create.
*   **Type / Scope**: Owl `t-inherit` template, bundled via `point_of_sale.assets_prod`.
*   **Proposed Changes**: Inherit **`point_of_sale.CustomerFacingDisplayOrder`**, which is
    declared at
    `addons/point_of_sale/static/src/app/customer_display/customer_display_template.xml:43`;
    the text to change is at `:84`, inside it. Stating the parent is not pedantry — the
    earlier draft gave only the line number, in an item whose own text warns that a wrong
    name fails silently, which made the item unimplementable.
*   **Gate**: none automated; manual check on the customer display.

#### 25. `castadoo/castadoo_branding_pos/static/src/overrides/odoo_logo.js` and `odoo_logo.xml` (Create — optional)

*   **Action**: Create, optional.
*   **Type / Scope**: POS logo component.
*   **Proposed Changes**: The POS has its own logo component at
    `addons/point_of_sale/static/src/app/generic_components/odoo_logo/odoo_logo.{js,xml}`.
    These are the two files that are genuinely optional in the register. The `js` file
    references the component name; renaming it is cosmetic and can be skipped without
    affecting user-visible branding, because the image it renders is `logo2.png`, which is
    replaced in place by item 28. **Explicitly optional**: omitting it changes no rendered
    string, while items 22–24 are required. It is one of exactly two optional items in the
    plan; the other is item 47.
*   **Gate**: none — omitting it is a permitted outcome, not a defect.

#### 26. Web icon and badge binaries at their existing upstream paths (Modify — binary)

*   **Action**: Modify.
*   **Type / Scope**: Binary replacements, kept at the **existing** upstream paths. Filed
    under the binary group, not the base tier: these are upstream blobs, and the base addon
    does not contain them.
*   **Proposed Changes**: These are **not** new files in `castadoo/`. They are overwrites
    of upstream blobs at the same path:
    *   `addons/web/static/img/favicon.ico` — 16/32/48 multi-size, mark only;
    *   `addons/web/static/img/odoo-icon-192x192.png` — square, maskable safe area;
    *   `addons/web/static/img/odoo-icon-512x512.png` — square;
    *   `addons/web/static/img/odoo-icon-ios.png` — 180 px, opaque background;
    *   `addons/web/static/img/odoo-icon.svg` — vector mark;
    *   `addons/web/static/img/odoo_logo_tiny.png` — 62×20 wordmark badge.
    Keeping the filenames is deliberate: it converts three code edits in
    `webmanifest.py` and `webclient_templates.xml` into zero. Filenames are never shown
    to a user.

### Tier 3 — binary replacements at existing paths

These are `Modify` in git terms (a new blob at an existing path). The conflict surface is not
"none": when both sides modify the same path git reports `CONFLICT (content)` and offers no
hunk-level resolution, so resolving it means taking the fork's blob — which silently discards
the upstream change while looking identical in review. The mitigation is a path-scoped
`.gitattributes` rule (`merge=ours`) over the 13 true binaries — created by **item 1b** — and
the discipline of reading the upstream change before taking ours. Three of the SVGs below are
text, not binary, and conflict *inside* the file; they are `modify-text` in the manifest and
deliberately excluded from the rule.

#### 27. `addons/web/static/img/logo.png` (Modify — binary)

*   **Action**: Modify.
*   **Type / Scope**: Horizontal lockup.
*   **Proposed Changes**: Portal footer and public pages; 35 references. Mark + outlined
    wordmark, horizontal.

#### 28. `addons/web/static/img/logo2.png` (Modify — binary)

*   **Action**: Modify.
*   **Type / Scope**: Horizontal lockup, POS display.
*   **Proposed Changes**: 2 references. Same lockup as item 27.

#### 29. `addons/web/static/img/logo_inverse_white_206px.png` (Modify — binary)

*   **Action**: Modify.
*   **Type / Scope**: Inverse 206 px mark.
*   **Proposed Changes**: Used on dark backgrounds.

#### 30. `addons/web/static/img/odoo_logo.svg` and `odoo_logo_dark.svg` (Modify — text)

*   **Action**: Modify.
*   **Type / Scope**: Website configurator logo, light and dark. **Text, not binary** — both
    are SVG/XML and git diffs them line by line, which is why they are classified
    `modify-text`. They are two distinct files despite sharing a byte count (1,581 B each,
    different SHA256), so both are edited rather than one being a copy of the other.
*   **Proposed Changes**: Wordmark with text **outlined**, not live `<text>`.

#### 31. `addons/point_of_sale/static/src/img/favicon.ico` (Modify — binary)

*   **Action**: Modify.
*   **Type / Scope**: POS favicon.
*   **Proposed Changes**: Mark-derived `.ico`.

#### 32. `addons/website_links/static/img/default_favicon.png` (Modify — binary)

*   **Action**: Modify.
*   **Type / Scope**: Fallback icon for the link-tracker preview, used when the favicon
    service fails.
*   **Proposed Changes**: Mark-derived square PNG. Its consumer is
    `addons/website_links/static/src/xml/recent_link.xml:12`, which references
    `/website_links/static/img/default_favicon.png` through an `onerror=` handler on the
    Google favicon `<img>` — so the file is reached only when that external service fails,
    which is why earlier passes over `views/` and `i18n/` found no reference to it.

#### 33. `setup/win32/static/pixmaps/odoo-icon.ico`, `odoo-intro.bmp`, `odoo-slogan.bmp` (Modify — binary)

*   **Action**: Modify.
*   **Type / Scope**: Installer visuals.
*   **Proposed Changes**: `.ico` multi-size; two 24-bit BMPs. `odoo-intro.bmp` is used for
    both the welcome and the uninstall-welcome page (`setup.nsi:136–137`), so one file
    covers both. **The filenames do not change**, and `setup.nsi:134–139` are pixmap *paths*
    that must not be touched by item 38's string work — replacing those paths would point
    the installer at files that do not exist.

#### 34. `addons/web/static/img/nologo.png` — **excluded**

*   **Action**: None.
*   **Type / Scope**: Deliberate non-change.
*   **Proposed Changes**: None. It is an intentional placeholder shown when no logo is set.
    Replacing it would misrepresent "no logo" as "CASTADOO logo". Recorded so its absence
    from the diff is not read as an oversight.

### Tier 4 — in-place edits of upstream files

The only files with a recurring conflict surface. Each entry states the mitigation, because
these are the ones a future merge will fight over.

#### 35. `odoo/release.py` (Modify)

*   **Action**: Modify.
*   **Type / Scope**: Package metadata.
*   **Proposed Changes**: **One line.** `description` at line 20, `'Odoo Server'` →
    `'CASTADOO Server'`. That is the whole item — the earlier draft stated the freeze rule
    without ever supplying the replacement string.
    `product_name` (line 19), `author` (line 33), `author_email`, `version_info` (line 15),
    `url` (line 32) and `nt_service_name` (line 37) all stay, and the reason is measurable
    rather than ceremonial: `product_name` **and** `author` both feed the datadir through
    `config.py:50` → `appdirs.user_data_dir()`, so changing either relocates every filestore
    and attachment to an empty new directory with no error. `author` is also LGPL
    attribution, and its tree value is `'OpenERP S.A.'` at `:33` — **not** `'Odoo S.A.'` as
    an earlier draft said, which matters because the register quotes it.
    `nt_service_name` is service identity. `version_info` and `series` still surface in the
    database manager; that leakage is recorded in Non-Goals rather than denied.

#### 36. `addons/web/static/src/public/database_manager.qweb.html` (Modify)

*   **Action**: Modify.
*   **Type / Scope**: Raw QWeb HTML, loaded by file path.
*   **Proposed Changes**: Four strings: `<title>Odoo</title>` (line 4), the unprotected-
    manager warning (line 33), the "sent to Odoo online services" notice with its
    `odoo.com/privacy` link (line 102), and the moved-or-copied notice (line 144). This
    file is **not** an `ir.ui.view` — it is read from disk by a controller — so no
    inheritance reaches it. That is the entire reason it is in this tier. Line 102 also
    carries a privacy policy link; repointing it to a CASTASOFT policy page that does not
    exist would be worse than leaving the Odoo one, so the link target needs a decision at
    implementation time.

#### 37. `addons/web/controllers/webmanifest.py` (Modify)

*   **Action**: Modify.
*   **Type / Scope**: Python controller.
*   **Proposed Changes**: Two lines. `background_color` and `theme_color`, both `'#714B67'`
    → `'#303188'`. The name is **not** edited: it reads
    `ir.config_parameter['web.web_app_name']` with a stock default of `'Odoo'`, which is why
    the parameter is seeded as module data (data model, and item 8's overlay) rather than
    left to deployment. The icon paths are **not** edited: filenames are preserved by
    item 26. Two lines, but upstream touches this file most years — per
    `docs/change_register.md`, these are the most expensive lines in the register per conflict.
    The service-worker route in the same file is untouched; see the cache decision in Asset
    pipeline.

#### 38. `setup/win32/setup.nsi` (Modify)

*   **Action**: Modify.
*   **Type / Scope**: NSIS installer script — the largest single item, and the reason the
    fork exists. Measured baseline at the 17.0 tip: **729 lines**, of which **89** contain
    `Odoo` (**114 occurrences**, 119 any-case). The register enumerates them line by line;
    the count is not restated here because three different figures have appeared in this
    document and none survived checking.
*   **Proposed Changes**: The register's per-line replacements, plus four rules that must not
    be re-decided at implementation time:
    *   **`PUBLISHER` (line 44)** — `'Odoo S.A.'` → `'CASTASOFT'` (D6). This is the NSIS
        binary publisher, not a copyright notice. Left alone, signing with the CASTASOFT
        certificate produces unknown-publisher warnings. The LGPL notice must be preserved
        in `COPYRIGHT` / `NOTICE` instead.
    *   **`PRODUCT_NAME` (line 74)** — `"Odoo"` → `"CASTADOO"`. This is dual-purpose, and
        it is the second instance of the same trap as `release.product_name`. It feeds
        `DISPLAY_NAME` (line 75) → `UNINSTALL_REGISTRY_KEY` (line 78) and
        `REGISTRY_KEY` (line 82), and `.onInit` reads `REGISTRY_KEY` at line 466 to find a
        prior install directory. Changing it relocates the registry identity, so the
        transition must land in **one** release that both writes the new key and reads the
        old one, or the prior install is orphaned. It cannot be split across patch
        releases.
    *   **`SERVICENAME` (line 67)** and `UNINSTALL_REGISTRY_KEY_SERVER` (line 80) —
        **leave both.** `SERVICENAME` is `odoo-server-${VERSION}` and is used by every
        `nssm` install/set/stop/delete call (lines 295–298, 446–447, 717–718). Changing it
        orphans installed services. `UNINSTALL_REGISTRY_KEY_SERVER` hardcodes `Odoo Server`
        separately from `PRODUCT_NAME` and is used at line 440 to chain-uninstall a prior
        server install; it is an identity string, not a display string, and it is easy to
        miss because it does not reference `${PRODUCT_NAME}`.
    *   **`DEFAULT_POSTGRESQL_PASSWORD` (line 87, `'openpgpwd'`)** — **not** changed here.
        It is the only instance in the tree and it is E3, a release-process decision; the
        mitigation is the forced `admin_passwd` on first run recorded in the deployment
        checklist.
    *   **Lines 134–139 are pixmap paths and must not be replaced.** They are `File`
        directives pointing at `odoo-intro.bmp`, `odoo-slogan.bmp` and `odoo-icon.ico`;
        item 33 preserves those filenames precisely so that these six lines need no edit.
        A blanket string replace over this file breaks the installer's image references.
    *   Contact details at lines 423–426 (`support@odoo.com`, `sales@odoo.com`,
        `https://www.odoo.com`, the Odoo phone number) are display strings and must be
        replaced with CASTASOFT equivalents.
    *   `MUI_FINISHPAGE_LINK_LOCATION` (line 160) points at
        `https://www.odoo.com/page/contactus`; it needs a CASTASOFT target.
    *   **The `LANG_FRENCH` block (31 lines, around 203–236) needs translation, not
        substitution.** `CASTADOO` is not a French word and may or may not be the string to
        put there; that is a copywriting decision, recorded as such rather than folded into
        a count of replacements.
*   **Gate**: Gate 3a over the register's line list, plus a manual installer build and
    install on a clean VM (CUJ 5). No automated gate can run an NSIS script.

#### 39. `setup/package.py` (Modify)

*   **Action**: Modify.
*   **Type / Scope**: Build/test script.
*   **Proposed Changes**: **9** case-sensitive `Odoo` lines (`:2`, `:50`, `:54`, `:78`,
    `:83`, `:257`, `:269`, `:270`, `:323`), of which **8 are not changed**: the licence
    header on line 2 (`# Part of Odoo. See LICENSE…`), the class names
    `OdooTestError` / `OdooTestTimeoutError` (`:50`, `:54`), and the internal log and
    exception text (`:78`, `:83`, `:257`, `:269`, `:270`). **One is user-visible**: `:323`
    `Odoo Bot <info@odoo.com>` → `CASTASOFT <info@castasoft.yukreasi.id>`, so generated
    packages are attributed correctly in the Debian changelog.
*   **Gate**: Gate 3a with all eight retained lines allowlisted as `internal identifier`.

#### 40. `setup/win32/static/doc/License.rtf` (Modify)

*   **Action**: Modify.
*   **Type / Scope**: Licence text shown in the installer. Path is
    `setup/win32/static/doc/License.rtf` — the earlier draft omitted `static/doc/`.
*   **Proposed Changes**: **2** `Odoo` occurrences. Keep the licence body **verbatim** —
    do not rename Odoo to CASTADOO inside it, which would misstate the licence's provenance.
    Append one line: `Portions Copyright (c) 2026 CASTASOFT.` That resolves the earlier
    draft's self-contradiction ("keep verbatim" and "add the CASTASOFT copyright line" as if
    they conflicted); they do not, because one is the body and one is an appended notice.
    **Not** renamed to CASTADOO; this is the one place where "Odoo" must survive verbatim.

#### 41. `odoo/tools/config.py` (Modify — conditional on Open Question 2)

*   **Action**: Modify, conditional.
*   **Type / Scope**: Python config defaults.
*   **Proposed Changes**: **Only if** the phone-home question resolves to "disable by
    default". Line 78, `publisher_warranty_url`, would be blanked with a commented
    explanation. If the answer is "leave stock", this file is untouched and the plan's file
    count drops by one. **The alternative shape must be stated**, because three parts of the
    document have pointed in three directions: the same outcome is reachable by a key in the
    operator's `odoo.conf`, which removes this item from the diff entirely and is the
    cheaper of the two. The source edit applies to every deployment without operator action;
    the config key does not. That trade is exactly what Open Question 2 asks, and no
    default is chosen here.
*   **Gate**: Gate 3a if the edit lands; nothing if it does not.

#### 42. `odoo.conf` / deployment configuration (None — deployment artefact, not a repo file)

*   **Action**: None in the repository.
*   **Type / Scope**: Runtime configuration. There is **no root `odoo.conf`** in the 17.0
    tree — measured: the root carries `README.md`, `CONTRIBUTING.md`, `LICENSE`, `COPYRIGHT`,
    `SECURITY.md`, `ruff.toml` and `setup.cfg`, and the only config files are
    `debian/odoo.conf` and the POS box config. So this item creates nothing and modifies
    nothing in git; its whole content is a deployment instruction.
*   **Proposed Changes**: One `addons_path` entry adding `<repo>/castadoo`, **first** in the
    list, so `module.get_module_path` cannot resolve an upstream addon ahead of a CASTADOO
    one. `debian/odoo.conf` has a commented `addons_path` line that documents the shape.
    **Not** modified in the repo: `debian/odoo.conf` is upstream packaging and editing it
    creates conflict surface for a value that belongs to the deployment. The line goes in
    the operator's own `odoo.conf`, and the deployment checklist states it, because without
    it every addon in `castadoo/` is invisible and the rebrand silently does not apply.

    One further deployment action shares this item because it is also repo-local config that
    no tracked file can carry: `git config merge.ours.driver true`. Item 1b's
    `.gitattributes` names the driver; git refuses to use a driver it has no definition for,
    and falls back to a normal merge silently, so the rule becomes decoration. The
    deployment checklist states it for the same reason `addons_path` is stated there.
*   **Gate**: none. This is precisely the configuration tier that every gate is blind to,
    which is why it appears in the deployment checklist as an action rather than a
    reference.

### Tier 5 — non-code artefacts

#### 43. `README.md` (Modify)

*   **Action**: Modify.
*   **Type / Scope**: Repository documentation — an **upstream path**, so it enters the
    diff budget and the LGPL dating obligation.
*   **Proposed Changes**: State that this is a fork of Odoo 17.0 by CASTASOFT, link
    upstream, state the licence and that it is unchanged, and describe the branch model
    (`17.0` mirror + `castadoo/17.0` overlay) so a visitor does not clone the wrong branch.
    **Rewrite any passage carrying a brand hex or an `odoo.com` link so that it carries
    none** — the stock `README.md` contains `#875A7B`, and no allowlist reason is true for a
    colour in a README. A prose rewrite is cheaper and more honest than an allowlist entry,
    and it is the reason this item is a *Modify* rather than a lint exclusion. The earlier
    draft claimed items 27 and 9 fixed that hex; neither can — item 27 replaces a PNG blob
    and item 9 is a new QWeb view in a different module.
*   **Gate**: Gate 3a over this path; the rewrite is what keeps it clean.

#### 44. `CONTRIBUTING.md` (Modify)

*   **Action**: **Modify**, not Create — `CONTRIBUTING.md` **does exist** at the 17.0 root
    (measured), so this is an upstream path like item 43.
*   **Type / Scope**: Maintainer documentation.
*   **Proposed Changes**: The sync procedure, the `git log --first-parent` convention for
    reading overlay history (a direct consequence of D2's merge model), the D7 activation
    mechanism, and the rule that `17.0` is never edited. Without this, the next maintainer
    edits the mirror and the pristine guarantee is gone. Because it is an upstream file, the
    edit is additive prose in the existing document, and it counts against the budget.

#### 45. `docs/change_register.md` (Create — committed ahead of the plan)

*   **Action**: Create. Note the 17.0 tree has **no `docs/` directory**, so this item creates
    the directory as well as the file. In this repository it is already committed, ahead of
    the rest of the plan, because the design cites it and the design is committed first.
*   **Type / Scope**: The register, as a versioned artefact.
*   **Proposed Changes**: The register is **not** hand-maintained prose: it becomes a
    *derived view* of `castadoo/change_manifest.toml`, generated by
    `castadoo/tools/render_manifest.py`, and the manifest is the file Gate 2 and Gate 3 read.
    Both are versioned with the code they describe, or the gates compare against a stale list.
    The interim state is deliberate — the register exists before the manifest that will
    generate it, so the design has a citable enumeration from the first commit. The manifest
    and renderer supersede the hand-written file; they do not accompany it.
*   **Gate**: this item *is* the gates' input; see 46.

#### 46. `.github/workflows/brand-gates.yml` (Create)

*   **Action**: Create.
*   **Type / Scope**: CI workflow — the three gates, in the order the sync procedure runs
    them.
*   **Proposed Changes**: One workflow, three jobs:

    ```yaml
    # Gate 1 — mirror identity. Fails if 17.0 is not exactly upstream/17.0.
    # Gate 2 — diff budget. Modified upstream paths only; additions excluded.
    # Gate 3 — brand lint, split into pathlint (exact, allowlisted) and
    #          treelint (coarse, whole tree, i18n and demo excluded).
    ```

    *   **Gate 1**: `test "$(git rev-parse 17.0)" = "$(git rev-parse upstream/17.0)"`. This
        is G2's only enforcement, and it must run before the others because a stale base
        invalidates them.
    *   **Gate 2**: `git diff --stat --diff-filter=M upstream/17.0...HEAD --
        $(manifest paths where upstream_owned)`, asserting **≤ 25 changed upstream paths**
        and **≤ 103 edited lines**, and that every changed path appears in
        `castadoo/change_manifest.toml`. `--diff-filter=M` is not a refinement: without it
        the gate fails on its own first commit, because `--stat` counts the ~38 added files
        and counts each one-line replacement as `+1/-1`.
    *   **Gate 3a, pathlint**: for each manifest path, grep for `Odoo`; every hit must carry
        an allowlist reason from a closed vocabulary in the manifest (`internal identifier`,
        `D1-C`, `licence notice`, `not user-visible`, `upstream documentation`). The
        allowlist is capped at **40 entries** — if it grows past that, the diff has grown
        past the design. It must include the six excluded `mail.template` data files with
        reason `D1-C` (`auth_signup`, `portal`, `gamification`, `lunch`,
        `website_crm_partner_assign`, `website_profile`) or the first sync fails on them,
        and it must carry one `upstream documentation` record for item 6's retained
        `documentation` entry.
    *   **Gate 3b, treelint**: coarse literals only — `Powered by Odoo` and `www.odoo.com` —
        over the whole tree, with `i18n/**/*.po`, `i18n/**/*.pot` and `**/demo/**` excluded
        by glob. Measured scale justifies the exclusion rather than a per-case decision:
        `git grep -l "Powered by Odoo"` returns 52 files and `"Sent by"` returns 180, almost
        all of them translations.
*   **Gate**: it is the gate. Its own correctness is asserted by running it against a
    known-good tree once, in the sync rehearsal.

#### 47. `castadoo/assets/build_assets.sh` (Create — tooling)

*   **Action**: Create.
*   **Type / Scope**: Asset generation recipe, plus its pinned `package.json`.
*   **Proposed Changes**: Records the pipeline from the Technical Plan so the binaries in
    items 26–33 can be regenerated: outline the wordmark with `opentype.js`, compose lockups,
    rasterise with `sharp`. Both dependency versions are pinned exactly, so regenerating
    later reproduces the same bytes. Committed as a recipe, not automated in CI, because
    asset regeneration is a design change, not a build step. This is the only other
    genuinely optional item: the artefacts can be committed without it, at the cost of
    losing the ability to regenerate consistently — but unlike item 25, omitting it is a
    real loss rather than a cosmetic one.

### Verification Plan

The suite has two tiers, because three of the five configuration values are deployment data
that no source-tree test can see. Tier A runs in CI; Tier B runs against a deployed
instance and is the deployment checklist's step 8.

**Tier A — source-tree tests.**

*   **Build / install**: `odoo-bin -d <test_db> --addons-path=<repo>/castadoo,<repo>/addons,<repo>/odoo/addons -i castadoo_branding --stop-after-init`
    must complete with no `External ID not found` and no `ImportError`. `--addons-path` is
    not optional here: it is the thing item 42 exists to supply, and omitting it makes every
    assertion below run against stock Odoo.
*   **Module presence**: query `ir.module.module` for `state = 'installed'` and assert the
    module names are present — **not** `--version`, which lists nothing about modules.
    Required after D7-B: `castadoo_branding`, plus one overlay per installed target module.
    Absent is allowed for an overlay whose target module is not installed, and for
    `castadoo_branding_pos` only if `point_of_sale` is absent.
*   **`tests/test_branding.py`** as an `HttpCase`, extending the pattern of the existing
    `addons/web/tests/test_webmanifest.py`, which already exercises exactly the manifest
    fields this design asserts:
    *   `GET /web/login` → body contains no `>Odoo<` and contains `CASTADOO`;
    *   `GET /web/manifest.webmanifest` → `name == 'CASTADOO'` (hermetic now that the
        parameter is seeded), `background_color == theme_color == '#303188'`, every
        `icons[].src` returns 200;
    *   `browser_js` assertion that the offline page's `.card button` computed
        `background-color` is `#303188` — a grep cannot read computed style, and the append
        strategy chosen in item 4 is precisely what needs a computed-style check;
    *   `MailCase` render of `mail_notification_layout`, `reset_password_email` and
        `digest_mail_main`, asserting the rendered body contains `CASTADOO` and no
        `Powered by Odoo` / `Sent by Odoo`;
    *   `browser_js` assertion that the `user_menuitems` registry has no `odoo_account` key.
*   **Static analysis**: the three CI gates (item 46) on every push, plus `ruff` on the new
    addons' Python (17.0 ships `ruff.toml`).
*   **Coverage**: no percentage target. The meaningful metrics are the diff budget
    (≤ 25 changed upstream paths, ≤ 103 edited lines) and zero unlisted brand hits — both
    pass/fail, neither a percentage.

**Tier B — post-deploy assertions.** These cannot be hermetic because they read data a
deployment supplies:

*   `res.company.name` set → the browser tab reads the company name; unset → `CASTADOO`
    (the inheritance fixes the fallback only, so asserting `CASTADOO` unconditionally would
    fail on any named company);
*   `res.company.logo` uploaded → login card renders it;
*   invoice PDF text extraction contains no `Odoo` and its title metadata reads CASTADOO;
*   PWA install on one Android and one iOS device, plus the post-upgrade reinstall check;
*   POS receipt print and customer display — Owl `t-inherit` fails silently, so this cannot
    be inferred from a browser check;
*   Windows installer on a clean VM (CUJ 5): install, verify the uninstall registry key,
    verify publisher reads CASTASOFT, uninstall, verify the key is removed and the service
    name never changed;
*   notification email opened in at least two clients, since CSS-in-email differs.

**Sync rehearsal.** Run the full sync procedure against a real upstream point release before
declaring the design done. All three gates must pass, and the conflict count must be zero or
confined to `setup.nsi`. A sync that requires hand-resolving an inherited view means an
anchor moved, which is the drift the gates exist to catch. **This step is blocked on Open
Question 1** (whether 17.0 still receives point releases) — without a point release there is
nothing to rehearse against, and that must be reported as a blocker rather than quietly
skipped.

#### Footnote on file count

Two numbers in this document are easy to confuse, and the difference is definitional rather
than drift. The **diff budget is 25 upstream paths**: 16 replaced artefacts at existing paths,
8 edited upstream paths, and 1 conditional edit — the paths git reports as modified after the
overlay applies. The register's headline of **37** is a *coverage* count: it lists every path
the rebrand reasons about, including overrides that are new files and views the plan only
inherits, neither of which makes a path differ.

This plan, in turn, is numbered 1–47 across 50 entries, because it also counts files that
must *exist* without being upstream-owned — the whole `castadoo/` tree, the gates, the
tooling. The table below is a **derived view**: it is generated from
`castadoo/change_manifest.toml` by `castadoo/tools/render_manifest.py` and must not be
hand-edited; if a number here disagrees with the manifest, the manifest is right.

The last column is what makes the two totals derivable rather than asserted: **25** of those
files are upstream-owned (a path git will report as modified), and the rest are additive. A
reader can add the column and get both numbers.

| Group | Items | Entries | Files | Upstream-owned |
|---|---|---|---|---|
| Base addon, required | 1–6 | 6 | 6 | 0 |
| Seeded config parameter | 1a | 1 | 1 | 0 |
| `.gitattributes` merge driver | 1b | 1 | 1 | 0 |
| Hook (D7-B) | 7 | 1 | 1 | 0 |
| Per-module overlays | 8–24 | 17 | 17 | 0 |
| Overlay `__init__.py` files | 22a | 1 | 8 | 0 |
| Optional POS component | 25 | 1 | 2 | 0 |
| Upstream artefacts replaced at existing paths | 26–33 | 8 | 16 | **16** |
| Deliberate non-change | 34 | 1 | 0 | 0 |
| In-place edits of upstream source | 35–40 | 6 | 6 | **6** |
| Conditional in-place edit (`config.py`) | 41 | 1 | 1 | **1** |
| Deployment instruction, not a repo file | 42 | 1 | 0 | 0 |
| Upstream prose edited (`README.md`, `CONTRIBUTING.md`) | 43–44 | 2 | 2 | **2** |
| New repo artefacts (`docs/change_register.md` + gates + tooling) | 45–47 | 3 | 3 | 0 |
| **Total** | **1–47** | **50** | **64** | **25** |

Of those, **2 are optional** (items 25 and 47 — the only two) and **1 is conditional**
(item 41, which exists only if the phone-home question resolves to "disable"). The optional
and conditional items are inside the 63: item 25 is additive, item 47 is additive, and item 41
is counted as upstream-owned because it lands in `odoo/tools/config.py` if it lands at all.

Two entries are not repo changes and are numbered anyway so nothing is silently missing:
**item 34** is a documented non-change, and **item 42** is a deployment instruction that
lives in the operator's config, not the tree. Neither counts in either total, which is why the
Files column contains two zeros.

The register's headline of 37 is a **coverage** count and is neither of these numbers. It is a
per-surface list of every path the rebrand reasons about — including the overrides that are
new files and the views the plan only *inherits* — so it neither equals the 25 paths git will
report as modified nor the 39 additive files this plan creates. It is the right list for
asking "did we forget a surface" and the wrong list for asking "how big is the diff".

--------------------------------------------------------------------------------

<!-- Provenance: Indicates initial structural drafting via EGM. -->

*Drafted with EGM*
