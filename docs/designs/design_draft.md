# CASTADOO: Rebranded Fork of Odoo 17.0

> **Superseded — do not implement from this file.** This is the pre-review draft. It was
> reviewed in five stages, and the resulting repairs changed figures, decisions and
> mechanisms throughout (the `-u` hook convention, the service-worker behaviour, the
> file-count arithmetic, and roughly 30 sections besides). The current design is
> [`castadoo-rebrand-fork.md`](castadoo-rebrand-fork.md); where the
> two disagree, that file is correct and this one is the artefact that was corrected.

*   **Author:** acer (castasoft@gmail.com)
*   **Status:** Superseded by `docs/designs/castadoo-rebrand-fork.md`
*   **Date:** 2026-11-17

--------------------------------------------------------------------------------

## Overview

Create a maintained fork of `github.com/odoo/odoo` at series 17.0, named
`castaso/CASTADOO`, that presents CASTADOO branding to users while remaining cheap to
sync with upstream at point releases. The operator is CASTASOFT
(https://castasoft.yukreasi.id).

The deliverable of this design is a **source tree**, not a product build. It is the
shape of a repository: which branches exist, which files differ from upstream, and how
those differences survive an upstream merge.

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

Scope is fixed at **37 files, 94 edit lines, 23 additive overrides**, excluding the seven
`mail.template` body re-declarations by decision D1-C. Every one of those files is
enumerated with a line number in `change_register.md`, measured against the real 17.0 tip
`9c58cae5d6e3cf91ac1cca7df39fb21f68ca6e15` (40,111 files in tree).

## The Problem

### The business need

CASTASOFT deploys Odoo 17.0 for customers who see the software as CASTASOFT's product.
Today those customers see Odoo's name on the login page, in the browser tab, on PDF
reports, at the bottom of every notification email, on the Windows installer, and on the
installable web app. The fork exists to put the operator's name on the surfaces a
customer actually looks at.

LGPL-3 permits this. It does not permit the fork to *claim* to be Odoo, or to strip the
attribution that identifies what the software is derived from. So the work is not
"remove Odoo"; it is "make CASTADOO the product name on user-facing surfaces while
keeping the derivation visible and the notices intact".

### Why this is hard

Rebranding and cheap syncing pull against each other:

*   Every string changed **inside an upstream-owned file** becomes a merge conflict the
    next time upstream touches that region. The Windows installer alone would be 87 such
    lines in one file.
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
| `setup.nsi` has 45 Odoo strings | 87 | Installer cost was understated 2×. |
| Odoo purple is `#875A7B` / `#71639e` | **Four** distinct purples: `#714B67` (brand), `#71639e` (a stray `theme-color`), `#875A7B` (legacy email), and `#9E588B` (`hr_expense` mail, unique to that module). Only the `mail` and `digest` layouts read the company field. | Four of ten in-scope email sites are fixed by one setting; five hardcode a literal, one of them in a colour no summary had listed. The backend needs SCSS surgery to change, so it stays purple. |

The methodological correction behind all of them: **a case-sensitive grep cannot tell a
brand string from an identifier.** 26,560 files contain `Odoo`; 5,496 of the matching
lines are the mandated `# Part of Odoo. See LICENSE…` notice; 18,920 are translation
files. Of the remaining 1,343 hits, most are internal names — `odoo_chart`,
`OdooBarChart`, class names, docstrings. A work budget derived from substring counts
would be wrong in both directions, so this design derives its budget from **surfaces that
render**.

### The failure mode that survives a clean merge

The dangerous case is not a broken override. An xpath whose anchor upstream renamed fails
loudly at install, which is fine.

The dangerous case is an override that still applies cleanly when upstream **adds** new
brand copy nearby. Nothing conflicts, nothing errors, the new upstream string ships, and
a customer finds it. Git cannot catch that, and neither can a person reading a merge
diff over 40,000 files.

So the design includes two gates that run on every sync rather than one: an allowlisted
change register (the diff matches the register or the sync fails), and a brand lint
(grep the post-sync tree for the enumerated patterns, fail on any hit that is not an
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
*   **G4 — Branding on six named surfaces.** Backend shell and browser tab, login, PDF
    report metadata, outgoing email, Windows installer, PWA manifest, offline page,
    favicon and app icons. "Branding" means a user reading those surfaces sees
    CASTADOO, with the exclusions in Non-Goals stated as accepted leakage.
*   **G5 — Diff budget is bounded and checkable.** The overlay differs from upstream in
    **≤ 37 files** and **≤ 94 editor lines**, of which **≥ 23** items are additive
    (inheritance, new JS, new Owl templates) and therefore carry no conflict surface.
    Measured as `git diff --stat upstream/17.0...HEAD` on the overlay branch.
*   **G6 — Fresh clone is small.** A blobless clone of the fork stays under 500 MB
    (measured: 444 MB) with full history, so a maintainer can clone in minutes rather
    than hours.
*   **G7 — LGPL-3 compliance is structural, not documentary.** `# Part of Odoo` headers
    untouched, `release.author` frozen, notices preserved in the installer and licence
    file, and every modification dated in the merge commit that introduced it.
*   **G8 — Drift is caught by machine.** A sync that introduces an unbranded
    user-visible string, or edits a file outside the register, fails CI before it reaches
    a customer.
*   **G9 — Sync procedure is written down.** Trigger, owner, and conflict fallback
    documented, so the fork does not depend on one person's memory.

## Non-Goals

*   **Relicensing.** LGPL-3 cannot become MIT or proprietary. The notices cannot be
    stripped. This is a constraint on the work, not a task within it.
*   **Renaming internal identifiers.** The `odoo` Python package, `odoo-bin`,
    `ODOO_RC`, `odoo.conf`, the datadir, `version_info` and `series` all keep their
    names. Renaming them breaks addons, upgrade paths and every future sync, and none of
    them is user-visible.
*   **Changing `release.product_name`, `release.author`, or `release.nt_service_name`.**
    Datadir relocation, LGPL attribution, and service orphaning respectively. The
    reasoning is in The Problem above.
*   **Editing the 18,920 `.po` / `.pot` files in place.** Translation source strings keep
    saying Odoo in every non-English locale. Accepted leakage. A `msgstr`-only branding
    overlay is noted as future work, not part of this plan.
*   **Rewriting help text, tooltips, error messages, tour copy, and demo data.** Roughly
    1,150 additional strings, each needing a human judgement on whether `Odoo` there
    means *this product* or *the software it derives from*. Getting that wrong is a
    trademark statement, not a typo.
*   **Re-declaring the seven `mail.template` body records.** Decision D1-C. The
    consequence, stated rather than glossed: portal-invitation, portal-welcome,
    account-created, badge, lunch-supplier and lead-forward mails keep a `Powered by
    Odoo` footer and Odoo purple.
*   **Retheming the backend to `#303188`.** `primary_variables.scss:73` reads
    `$o-brand-odoo: $o-community-color !default;` — `!default` resolves before any later
    file in the bundle, so the change requires editing a compiled-variable file that
    changes between releases. Permanent conflict site, no user-visible brand gain. The
    backend stays purple by decision.
*   **Replacing `nologo.png`** (an intentional placeholder) or
    `account/…/Odoo_logo_O.svg` (a stencil inside the invoice QR code, where a change
    alters the QR payload).
*   **Building, signing, distributing or supporting a product.** No installer build
    pipeline, no auto-update, no release artefacts. This plan produces a source tree.
*   **Forking more than one series.** 17.0 only.

## Open Questions

Six questions remain open. Each one is carried here rather than answered in the plan,
because each changes what gets implemented. Where the plan has a dependency on an
answer, the Detailed Implementation Plan names it in the affected file's entry.

1.  **17.0 upstream support window.** Does Odoo 17.0 Community still receive point
    releases? If upstream maintenance has ended, "sync at point releases" describes a
    process that will never fire, and the merge model in Goal G3 has nothing to merge.
    *Shapes:* the sync procedure's trigger and the CI gates' value. No file in the plan
    changes either way.
2.  **Phone-home default.** `odoo/tools/config.py:78` defaults `publisher_warranty_url` to
    `http://services.openerp.com/publisher-warranty/` — note `openerp.com`, not
    `odoo.com`. It is a daily outbound call carrying instance metadata. Disable by
    default with a commented config line, or leave stock? *Shapes:* whether the shipped
    `odoo.conf` template carries an extra line, and whether this fork makes a privacy
    statement it then has to honour.
3.  **Deployment shape.** One tenant per install, or a shared multi-database host? *Shapes:*
    per-release asset recompilation goes from a constant to O(databases), and it changes
    how much the two CI gates matter — a single-tenant install tolerates drift a
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

A seventh question surfaced while writing the Technical Plan, and it is the one with the
sharpest failure mode. It is recorded there as **D7 — overlay activation**, because it
needs an answer before the Detailed Implementation Plan can be executed.

## Critical User Journeys (CUJs)

### CUJ 1: A customer's first visit is branded

*   **Given**: A CASTADOO deployment exists and `castadoo_branding` is installed. The
    company record has `name`, `logo` and `email_secondary_color` set.
*   **When**: A customer opens the deployment URL and reaches the login page, then logs in
    and looks at the browser tab.
*   **Then**: The browser tab reads `CASTADOO`. The login card shows the CASTADOO logo,
    because `/web/binary/company_logo` serves `res.company.logo`. The footer under the
    card reads CASTADOO and links to the CASTASOFT site, not `odoo.com`. No string on
    the screen reads "Odoo" apart from the licence notice that is not rendered here.
*   **Verification**: automated assertion that `GET /web/login` response body contains no
    `>Odoo<` and contains `CASTADOO`; manual check of the rendered tab title.

### CUJ 2: A maintenance sync happens and nothing silently regresses

*   **Given**: Upstream publishes a 17.0 point release. The overlay branch is one merge
    behind.
*   **When**: The maintainer runs the documented sync procedure: fetch upstream, fast-forward
    `17.0`, merge into the overlay with `--no-ff`, resolve conflicts, push.
*   **Then**:
    *   `17.0` equals `upstream/17.0` exactly.
    *   The merge commit message records the date and the upstream tag consumed.
    *   The diff-budget gate confirms the overlay still touches ≤ 37 files and ≤ 94 lines.
    *   The brand-lint gate either passes or names each new unlisted occurrence, so the
      maintainer handles a known list rather than discovering surprises in production.
    *   If upstream added new brand copy that the existing overrides do not reach, the
      lint fails and the sync stops before deployment.
*   **Verification**: both CI gates green; `git diff --stat upstream/17.0...HEAD` inside
    the budget.

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
    install on one Android and one iOS device.

### CUJ 5: An administrator installs the Windows package

*   **Given**: `setup.nsi` has been edited per the register and the three pixmaps replaced.
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
verified with `git ls-remote --symref origin HEAD`, not assumed. A fork whose default is
`20.0` hands an unqualified clone unbranded Odoo 20.0, which is the worst possible first
impression of the fork.

### The disposition rule

Every brand string in scope is assigned to exactly one of four mechanisms, and the order
is a preference order, not a menu. A string is moved to a more expensive mechanism only
when the cheaper ones are shown not to reach it.

| Rank | Mechanism | Touches upstream files | Conflict surface | Reached surfaces |
|---|---|---|---|---|
| 1 | **Configuration** | no | none | PWA name, login logo, PDF headers, email colours, website favicon |
| 2 | **Inheritance** (new files) | no | none, unless an anchor is renamed | backend title, login footer, offline page, PDF titles, notification email footers, POS Owl templates |
| 3 | **Binary replacement** (same path) | binary only | none — git sees a new blob, not a hunk | favicon, PWA icons, logo PNGs, installer pixmaps |
| 4 | **In-place edit** | yes | recurring, per upstream touch | `setup.nsi`, `database_manager.qweb.html`, `webmanifest.py`, `release.py` description |

Mechanism 4 is the scarce resource. The design's goal is to keep the count of mechanism-4
lines small and enumerated, not to reach zero. Attempting zero would mean either leaving
the installer unbranded or building an installer-side override system that does not
exist — an installer addon is a contradiction.

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

That is one base addon plus eight overlays, nine addons in total.

`auto_install` as a list is stock practice, not a trick: `account_payment/__manifest__.py:9`
uses `['account']`, and four other stock manifests do the same. The list names the
modules that must be present *and newly installed* for the overlay to activate.

**The trap.** That last phrase is where the design breaks if it is not handled. In
`ir_module.py:420-422`:

```text
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

**D7 — overlay activation.** Three mechanisms can close this, and they trade differently:

| Option | Mechanism | Fails when |
|---|---|---|
| **A. Explicit install list** | The sync and deployment runbook runs `-i castadoo_branding_mail,...` for each module present. No code. | A human omits one; the email footer silently keeps Odoo. Cheapest, most fragile. |
| **B. Self-activating base addon** | `castadoo_branding` gains a `post_init_hook` that searches `ir.module.module` for installed targets and installs the matching overlays. Runs once at base install. | A later database gains `mail` after `castadoo_branding` is installed — the hook does not re-run without a module upgrade. Needs an accompanying `-u castadoo_branding` convention. |
| **C. Base addon declares all overlays as `depends`** | Guaranteed activation, no hooks, no runbook step. | Forces every business module onto every database. This is the option the two-tier split exists to avoid. |

Option B is the only one that is both reliable on existing databases and does not drag
business modules in, at the cost of one hook and one documented `-u` step. Option A is
adequate if deployments are scripted and the runbook is followed exactly. Option C is
listed because it is what a reader will think of first, and because it is genuinely simpler
in every respect except the one that matters. **This is an author decision, not a drafting
decision**, and the Detailed Implementation Plan is written so that any of the three can
be applied to the same file set.

### Data and configuration model

Nothing in the branding paths stores state of its own except two company fields and one
system parameter, all of which are ordinary Odoo data:

| Setting | Model | Set by | Effect |
|---|---|---|---|
| `name` | `res.company` | deployment | Login title, PDF headers, email footers, portal pages |
| `logo` | `res.company` | deployment | Login card, PDF header, portal, email |
| `email_secondary_color` = `#303188` | `res.company` | deployment | Reaches the `mail` notification layout (S4.01, S4.02) and the `digest` footer (S4.10, S4.20). **Does not reach** S4.03, S4.04, S4.06, S4.07 or S4.09, which hardcode their colour. |
| `web.web_app_name` = `CASTADOO` | `ir.config_parameter` | deployment | PWA install name |
| `website.favicon` | `website` | deployment | Website and portal favicon |

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

So four of ten are free and five need the literal replaced. The fifth purple — `#9E588B`,
used only by `hr_expense` — is a colour no summary of this tree had recorded, and it is the
concrete reason a single find-and-replace pass over `#875A7B` is not a valid implementation
strategy.

Consequence worth stating: the company name and logo are **data**, so the rebrand is
partly a deployment step, not purely a repository change. A fresh database installed from
the branded tree still shows a blank company logo until an operator uploads one. The
design does not seed a demo company record; that would put an administrative decision
inside a module and collide with every real deployment.

### Asset pipeline

The committed artefacts are outputs; the pipeline is a reproducible recipe, kept in the
repo so the assets can be regenerated when the design changes.

```text
  logo.svg (mark, 89.94×110.97, portrait 0.81:1)
  CASTADOO.svg (wordmark, 683.22×107.6, live Garamond <text>)
        │
        ├─ 1. outline wordmark text  → opentype.js (Node 22) or fontTools (Python 3.14)
        │      reads glyph paths from the font file; no rasteriser needed
        │      removes the empty <text> node and editor metadata
        │
        ├─ 2. compose lockups         → mark + outlined wordmark
        │      horizontal (portal, PDF header), stacked, inverse-white
        │
        └─ 3. rasterise               → sharp (npm) for PNG/ICO, or cairosvg (pip)
               favicon.ico 16/32/48, 192², 512², 180² iOS, 62×20 badge, 206px inverse
```

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

### The two gates that run on every sync

These exist because the dangerous failure is silent. An override that still applies when
upstream adds new brand copy nearby produces no conflict, no error, and a customer
discovery.

```text
  post-sync tree
       │
       ├── Gate 1: diff budget ──────────────────────────────┐
       │     git diff --stat upstream/17.0...HEAD            │  fail → sync stops
       │     files ≤ 37, lines ≤ 94                          │  before deploy
       │     every changed path present in change_register   │
       │                                                     │
       └── Gate 2: brand lint ───────────────────────────────┘
             grep post-sync tree for the enumerated patterns
             every hit must be in an allowlist with a reason:
               "internal identifier" | "D1-C" | "licence notice" | "not user-visible"
             an unlisted hit fails the gate
```

Gate 1 is the falsifiable form of "small diff". Gate 2 is the only mechanism that catches
*uplift* drift — new upstream strings the overrides do not reach. The allowlist must be
able to state "internal identifier, not user-visible" explicitly, because otherwise it
fills with noise and gets disabled, at which point drift is caught by customers.

Neither gate is optional. Without Gate 1 the diff budget is an aspiration; without Gate 2
the rebrand decays one point release at a time.

### Sync procedure

```text
  1. git fetch upstream --tags
  2. git checkout 17.0 && git merge --ff-only upstream/17.0        # must succeed
  3. verify: git rev-parse 17.0 == git rev-parse upstream/17.0
  4. git checkout castadoo/17.0 && git merge --no-ff upstream/17.0
  5. resolve conflicts once, here — setup.nsi is the expected site
  6. merge message: "Sync upstream 17.0 to <tag> (<date>); CASTADOO modifications
     staged <date>"                          ← discharges the LGPL dating obligation
  7. Gate 1, Gate 2
  8. push origin 17.0 castadoo/17.0
```

Step 3 is not ceremonial. It is the only thing that distinguishes "I merged upstream" from
"I merged something", and it is the check that would have caught a mirror branch drifting
after a hand-resolved conflict.

### Where the open questions bite

Each open question from the section above lands on a specific part of this plan rather
than floating above it:

*   **#1 support window** — if upstream 17.0 no longer receives point releases, step 1 of
    the sync procedure has nothing to fetch. The branch model stays valid; its trigger
    does not. No file changes.
*   **#2 phone-home** — decides whether the shipped `odoo.conf` template carries one extra
    commented line. It is a one-line change with a policy consequence, so it is not made
    here.
*   **#3 deployment shape** — single-tenant means asset regeneration is a constant;
    multi-database means O(databases), and Gate 2 becomes load-bearing rather than
    precautionary.
*   **#4 bandwidth** — affects only the initial clone duration quoted in the runbook.
*   **#5 installer publisher** — one line in `setup.nsi`, plus the decision about where
    the LGPL notice lives.
*   **#6 wordmark font** — affects step 1 of the asset pipeline and nothing downstream.
*   **#7 overlay activation (D7)** — affects whether the per-module overlays install at
    all on existing databases. The highest-consequence of the seven.

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
    simply clone and start a server. Managing a patch series over 87 lines of `setup.nsi`
    plus 36 other files is its own maintenance problem, and rebasing patches onto each
    upstream tag is the same conflict resolution work with less tooling.
*   **Reason for Rejection**: Rejected by author (decision D2): this plan produces a
    source tree, not a build pipeline, and introducing a mandatory build step to gain
    provenance that the merge-commit message already provides is a net loss.

### Branding mechanism

#### Alternative G: Edit all 290 user-visible files in place

*   **Pros**: Complete coverage by construction. No mechanism selection, no classification,
    no risk of an override failing to apply.
*   **Cons**: Guarantees divergence on exactly the lines upstream touches, making
    "pristine mirror" and "conflict-free sync" mutually exclusive. The 290 figure was also
    never a count of brand strings — it came from a grep that cannot distinguish
    `odoo_chart` from user-visible copy.
*   **Reason for Rejection**: Rejected by author: it defeats the primary goal. The
    measured equivalent is 37 files and 94 lines, of which 23 items never touch an upstream
    file at all.

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
*   **Cons**: `primary_variables.scss:73` reads
    `$o-brand-odoo: $o-community-color !default;`, and `!default` resolves before any later
    file in the bundle, so Odoo's own customisation mechanism cannot be used. Achieving it
    requires editing a compiled-variable file that changes between releases — a permanent
    conflict site in a high-churn file.
*   **Reason for Rejection**: Rejected by author: permanent conflict cost for a colour
    that is not part of the six named surfaces. The backend stays purple, and the rebrand
    is confined to surfaces a customer is shown.

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
    `change_register.md` §4b as an option, not a plan.

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

#### Alternative M: Edit the 3,410 `.po` files containing `Odoo` in a `msgid`

*   **Pros**: The operator is Indonesian, so `id_ID` is plausibly a primary locale. Leaving
    it means Indonesian users read "Odoo" in the interface.
*   **Cons**: Renaming an English source string changes its `msgid`, which drops **every**
    locale back to the new English text until retranslated. That trades a partial brand
    leak for a total translation regression in every language.
*   **Reason for Rejection**: Rejected by author, provisionally: renaming a `msgid`
    trades a partial brand leak for a total translation regression in every language. The
    cheap mitigation is recorded as future work — a small branding-module `.po` that
    overrides `msgstr` only, never `msgid`, which fixes the Indonesian surface without
    touching upstream translation files.

#### Alternative N: Re-declare the seven `mail.template` bodies to remove their footers

*   **Pros**: Removes the last customer-visible `Powered by Odoo` in the email surface,
    including the portal invitation and account-created mails.
*   **Cons**: Seven `noupdate="1"` records that must be re-checked whenever upstream edits
    them, in exchange for one line of boilerplate. The records are skipped on every module
    update including upstream's own (`odoo/models.py:5103`), so the cost is a standing
    review obligation rather than the data-loss trap an earlier draft claimed — but it is
    a standing obligation nonetheless.
*   **Reason for Rejection**: Rejected by author (decision D1-C): seven watched records for
    a footer line, on mails that are largely staff- or supplier-facing. The accepted
    consequence is documented in Non-Goals so it is not later reported as a defect.

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
    `list_db = False` and `admin_passwd` in deployment, which is outside this plan but must
    be in the runbook.
*   **Brand strings sit in templates, not in secrets.** No credential, key or token is
    touched by any file in this plan. The one credential-adjacent line is
    `DEFAULT_POSTGRESQL_PASSWORD 'openpgpwd'` in `setup.nsi:87`, which is a stock installer
    default and is left alone — changing it silently would break existing installs without
    improving security.
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

*   **The overlay is additive by construction.** Because 22 of the items are new files or
    replaced binaries, removing the branding addon restores stock behaviour for those
    without touching upstream files. That is the rollback story, and it is why the
    mechanism split matters beyond conflict cost.
*   **The 4 in-place edit sites are not reversible by uninstalling.** `setup.nsi`,
    `database_manager.qweb.html`, `webmanifest.py` and `release.py` stay edited. Rolling
    those back means checking out the upstream file, which is a deliberate, visible act.
*   **Registry key changes are one-way in practice.** `DISPLAY_NAME` feeds
    `UNINSTALL_REGISTRY_KEY` (`setup.nsi:78`) and `REGISTRY_KEY` (`:82`), and `.onInit`
    reads the latter at `:466` to find a prior install. The first CASTADOO-named installer
    must therefore also look for the old key, or the previous install is orphaned. This
    must not be split across two patch releases.
*   **The service name stays `odoo-server-17.0`** (`release.py:37`,
    `setup.nsi:67`). Changing it would orphan every installed service, and the new
    uninstaller would have nothing to remove.

--------------------------------------------------------------------------------

### Additional Resources

*   `concepts_brief.md` — the predecessor brief from the brainstorm phase. Every
    measurement in this design traces back to it, and it records the six open questions in
    their original framing.
*   `change_register.md` — the per-line enumeration of all six surfaces: 37 files, 94 edit
    lines, 23 additive items, plus the decision sheet D1–D6. This is the artefact the diff
    budget gate checks against, so it becomes a versioned file in the repo (item 45).
*   Odoo 17.0 source at `9c58cae5d6e3cf91ac1cca7df39fb21f68ca6e15`, read directly for line
    numbers. The files cited most often: `odoo/addons/base/models/ir_module.py`
    (auto-install logic), `odoo/models.py:5103` (`noupdate` handling),
    `odoo/tools/config.py:50` (datadir), `addons/web/views/webclient_templates.xml`
    (backend shell), `setup/win32/setup.nsi` (installer).
*   `C:\Users\Yongky\Dropbox\Sandbox\logo.svg` — the CASTADOO mark source (89.94 × 110.97,
    `#303188` navy + `#FAA61A` orange).
*   `C:\Users\Yongky\Dropbox\Sandbox\CASTADOO.svg` — the wordmark source (683.22 × 107.6,
    live Garamond `<text>` nodes that must be outlined).
*   GNU LGPL-3.0, the licence the fork inherits and cannot change.

### Future Improvements

*   **The idea**: A `msgstr`-only `.po` overlay for `id_ID`.
    **What it fixes**: Indonesian users currently read English strings that say "Odoo".
    Renaming `msgid`s would drop every language back to new English text, so the safe form
    is a branding-module translation file that overrides only `msgstr`, never `msgid`.
*   **The idea**: Remove the seven excluded `mail.template` footers via a reversible
    migration.
    **What it fixes**: Portal-invitation and account-created mails keep a `Powered by Odoo`
    footer under D1-C. A `post_init` rewrite would remove it without re-declaring the
    records, but needs a rollback path that does not exist yet (Alternative K).
*   **The idea**: Backend retheme to `#303188`.
    **What it fixes**: The backend stays Odoo purple. Achieving it requires either an
    upstream change making `$o-brand-odoo` overridable without `!default`, or accepting a
    permanent edit to a compiled-variable file.
*   **The idea**: Automate asset regeneration in CI rather than committing binaries.
    **What it fixes**: The 16 committed binaries are outputs with no automated provenance.
    A CI job would prove the assets match their sources, at the cost of a rasteriser
    dependency in the build.
*   **The idea**: Extend Gate 2 from grep patterns to rendered-output assertions.
    **What it fixes**: Grep catches strings in files; it cannot see a string composed at
    runtime, which is exactly how `web.web_app_name` and the PDF title are assembled. A
    headless render of the six surfaces would be a stronger gate.

--------------------------------------------------------------------------------

## Detailed Implementation Plan

Every file below is either **Create** (new, additive, no conflict surface) or **Modify**
(upstream-owned, recurring conflict surface). Line numbers are from the 17.0 tip
`9c58cae5d6e3cf91ac1cca7df39fb21f68ca6e15`. No implementation code is given; the
pseudocode and shapes are what the implementer needs to make no further decisions.

**Placement decision.** All new addons live in a new top-level `castadoo/` directory. This
requires **one** `addons_path` entry in `odoo.conf` (see item 35). The alternative —
placing them under the existing `addons/` — needs no config but mixes product code into
upstream's directory and shows up in every `git diff` of `addons/`. Since
`module.get_module_path` returns the **first** addons path containing a module
(`odoo/modules/module.py:165`), `castadoo/` being first also guarantees an upstream addon
can never shadow these.

### Tier 1 — base addon `castadoo_branding`

#### 1. `castadoo/castadoo_branding/__manifest__.py` (Create)

*   **Type / Scope**: Odoo addon manifest.
*   **Proposed Changes**: `name` = "CASTADOO Branding", `depends: ['web']` only,
    `auto_install: False` (explicitly installed by the deployment), `license: 'LGPL-3'`,
    `author` recording both CASTASOFT and the upstream derivation. `application: False` so
    it does not appear as a top-level app. The `depends` list is the load-bearing part: it
    must contain `web` and nothing else, or the dependency-drag problem in Alternative H
    returns.

#### 2. `castadoo/castadoo_branding/__init__.py` (Create)

*   **Type / Scope**: Package init.
*   **Proposed Changes**: Imports `models` (for `res_company` defaults if used) and `hooks`
    if D7 option B is chosen. Must stay empty of logic.

#### 3. `castadoo/castadoo_branding/views/webclient_templates.xml` (Create)

*   **Type / Scope**: QWeb view inheritance, base tier.
*   **Proposed Changes**: Four inherited records, all `inherit_id` + `<xpath>`:
    *   `web.web_layout` → `//title` → replace the `t-esc` fallback `'Odoo'` with
        `'CASTADOO'` (targets `addons/web/views/webclient_templates.xml:22`).
    *   `web.brand_promotion_message` → the `<img>` at line 94–95 → set `alt` to
        CASTADOO and `src` to the replaced `odoo_logo_tiny.png`; the anchor `href` at
        line 92 must point at the CASTASOFT site, not `odoo.com`.
    *   `web.login_layout` → the footer anchor at line 130 → set `href` to the CASTASOFT
        site and replace the `Powered by <span>Odoo</span>` text with CASTADOO.
    *   `web.webclient_bootstrap` → `<meta name="theme-color">` at line 251 → set
        `content` to `#303188`. Note the stock value is `#71639e`, a third purple
        inconsistent with the brand `#714B67`; the replacement resolves that
        inconsistency rather than matching it.

#### 4. `castadoo/castadoo_branding/views/offline_templates.xml` (Create)

*   **Type / Scope**: QWeb inheritance for the offline page.
*   **Proposed Changes**: Two inherited records on `web.webclient_offline`
    (`addons/web/views/webclient_templates.xml:285`):
    *   the `<img>` `alt` at line 330 → CASTADOO;
    *   the paragraph at line 332 → text without the word Odoo.
    *   The inline `<style>` block at lines 293–326 carries `background-color: #714B67`
        and `border: 1px solid #714B67` on `.card button` (lines 317, 319). Overriding
        text inside a `<style>` node is the most fragile item in the whole register. Two
        options, and the implementer must pick one deliberately: inherit and replace the
        whole `<style>` node's content (fragile to upstream CSS edits, but self-contained),
        or append a new `<style>` rule after it in the inherited `<head>` that redeclares
        `.card button` background and border (survives upstream CSS changes, and cannot
        break if the original block is reordered). The second is preferred.

#### 5. `castadoo/castadoo_branding/views/report_templates.xml` (Create)

*   **Type / Scope**: QWeb inheritance for PDF metadata.
*   **Proposed Changes**: Two inherited records, because upstream declares the same string
    twice in two separate templates:
    *   `web.report_layout` → `<title>` at `report_templates.xml:16`;
    *   `web.report_preview_layout` → `<title>` at `report_templates.xml:50`.
    Both replace `title or 'Odoo Report'` with a CASTADOO fallback. Sharing one `<xpath>`
    between two parents is not possible. This is metadata only; the visible header is
    `res.company` data.

#### 6. `castadoo/castadoo_branding/static/src/user_menu/castadoo_user_menu.js` (Create)

*   **Type / Scope**: Owl/JS registry patch.
*   **Proposed Changes**: Patches the `user_menuitems` registry to replace the
    `odoo_account` entry (`addons/web/static/src/webclient/user_menu/user_menu_items.js:128`)
    and the `documentation` entry. Two distinct problems in one file:
    *   `odoo_account` — the item's `description` is the literal string
        `"My Odoo.com account"` (line 92) and its callback opens
        `https://accounts.odoo.com/account` (line 100). Removal is the honest option: the
        account it points at is Odoo's, and a CASTASOFT customer has no account there. A
        renamed entry that still opens an Odoo URL is worse than no entry.
    *   `documentation` — `documentationURL` is
        `"https://www.odoo.com/documentation/17.0"` (line 12). Either repoint to a
        CASTASOFT-hosted copy or remove the item. Repointing to a URL that does not exist
        yet would ship a broken menu.
    *   The patch must use `registry.category("user_menuitems").remove?`/`.add` semantics
        available in 17.0 and must not depend on load order beyond the asset bundle.

#### 7. `castadoo/castadoo_branding/hooks.py` (Create — conditional on D7)

*   **Type / Scope**: Module hook.
*   **Proposed Changes**: **Only created if D7 option B is chosen.** A `post_init_hook`
    that searches `ir.module.module` for installed modules among the overlay targets
    (`mail`, `auth_signup`, `portal`, `im_livechat`, `hr_expense`, `digest`,
    `website_slides`, `point_of_sale`) and installs the matching
    `castadoo_branding_*` overlays. Must be idempotent, must not raise if an overlay is
    missing from the path, and must log what it installed. Its existence changes
    `__manifest__.py` (item 1) to declare `'post_init_hook'`. Under D7 option A this file
    does not exist and the runbook carries the install list instead.

### Tier 2 — per-module overlays

Each overlay is one manifest plus one view file. All are `Create`, all are additive, and
all follow the same shape: `depends: ['castadoo_branding', '<module>']`, `auto_install:
['<module>']`, one inherited record. The `auto_install` list form is stock practice
(`addons/account_payment/__manifest__.py:9` uses `['account']`).

#### 8. `castadoo/castadoo_branding_mail/__manifest__.py` (Create)

*   **Type / Scope**: Overlay manifest — highest-traffic overlay.
*   **Proposed Changes**: `depends: ['castadoo_branding', 'mail']`,
    `auto_install: ['mail']`.

#### 9. `castadoo/castadoo_branding_mail/views/mail_templates_email_layouts.xml` (Create)

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
    These two carry the footer under every internal notification. Fixing them is the
    single highest-value change in the email surface. Note both live in a `data/` file but
    are `<template>` QWeb views, not `mail.template` records — that distinction is why
    they are inheritable at all.

#### 10. `castadoo/castadoo_branding_auth_signup/__manifest__.py` (Create)

*   **Type / Scope**: Overlay manifest.
*   **Proposed Changes**: `depends: ['castadoo_branding', 'auth_signup']`,
    `auto_install: ['auth_signup']`.

#### 11. `castadoo/castadoo_branding_auth_signup/views/auth_signup_templates_email.xml` (Create)

*   **Type / Scope**: QWeb inheritance.
*   **Proposed Changes**: Two inherited records on
    `auth_signup.reset_password_email` (line 81) and
    `auth_signup.alert_login_new_device` (line 143). Each footer hardcodes
    `style="color: #875A7B;"` **inline**, so unlike the `mail` layout these two do not
    honour `company.email_secondary_color` and the colour must be replaced in the markup
    as well as the text and `href`. The same file also hardcodes `#875A7B` as the button
    background at lines 36 and 122; those are inside the same template region, so replacing
    all four occurrences is a single inheritance edit rather than two.

#### 12. `castadoo/castadoo_branding_portal/__manifest__.py` (Create)

*   **Type / Scope**: Overlay manifest.
*   **Proposed Changes**: `depends: ['castadoo_branding', 'portal']`,
    `auto_install: ['portal']`.

#### 13. `castadoo/castadoo_branding_portal/views/portal_templates.xml` (Create)

*   **Type / Scope**: QWeb inheritance.
*   **Proposed Changes**: One inherited record on `portal.portal_record_sidebar`, line 288
    of `addons/portal/views/portal_templates.xml`. Note this is a sidebar in the portal
    *web* UI, not an email — the register lists it under Surface 4 because the string is
    identical, but the anchor is a page element.

#### 14. `castadoo/castadoo_branding_im_livechat/__manifest__.py` (Create)

*   **Type / Scope**: Overlay manifest.
*   **Proposed Changes**: `depends: ['castadoo_branding', 'im_livechat']`,
    `auto_install: ['im_livechat']`.

#### 15. `castadoo/castadoo_branding_im_livechat/views/im_livechat_templates.xml` (Create)

*   **Type / Scope**: QWeb inheritance, two different parents.
*   **Proposed Changes**: Two inherited records: `im_livechat.livechat_email_template`
    (line 91 of `addons/im_livechat/data/mail_templates.xml`) and
    `im_livechat.support_page` (line 79 of
    `addons/im_livechat/views/im_livechat_channel_templates.xml`). One parent is a data
    template, one is a web view; both are QWeb, so one file can carry both records.

#### 16. `castadoo/castadoo_branding_hr_expense/__manifest__.py` (Create)

*   **Type / Scope**: Overlay manifest.
*   **Proposed Changes**: `depends: ['castadoo_branding', 'hr_expense']`,
    `auto_install: ['hr_expense']`.

#### 17. `castadoo/castadoo_branding_hr_expense/views/hr_expense_templates.xml` (Create)

*   **Type / Scope**: QWeb inheritance.
*   **Proposed Changes**: One inherited record on
    `hr_expense.hr_expense_template_register_no_user` (line 49 of
    `addons/hr_expense/data/mail_templates.xml`). This footer carries
    **`style="color:#9E588B;"`** — a fourth purple, distinct from `#714B67`, `#71639e` and
    `#875A7B`, and not overridable by `email_secondary_color`. The same literal is the
    button background at line 31. Replacing `#875A7B` everywhere would miss this file
    entirely, which is why it is called out per-site rather than covered by the company
    setting.

#### 18. `castadoo/castadoo_branding_digest/__manifest__.py` (Create)

*   **Type / Scope**: Overlay manifest.
*   **Proposed Changes**: `depends: ['castadoo_branding', 'digest']`,
    `auto_install: ['digest']`.

#### 19. `castadoo/castadoo_branding_digest/views/digest_templates.xml` (Create)

*   **Type / Scope**: QWeb inheritance.
*   **Proposed Changes**: **Two** inherited records inside `digest.digest_mail_main`
    (template spans lines 270–447 of `addons/digest/data/digest_data.xml`):
    *   line 398 — `Sent by <a href="https://www.odoo.com"…><span class="odoo_link_text">Odoo</span></a>`
        in the unsubscribe/preferences footer;
    *   lines 436–437 — `Powered by <a href="https://www.odoo.com"…><span class="odoo_link_text">Odoo</span></a>`.

    Both are needed: a single-line grep for `Powered by` finds only the second, because the
    first footer uses `Sent by`. They share one parent template, so one `<xpath>` cannot
    cover both — two records, two anchors.

    Keep the classes `odoo_link` / `odoo_link_text`; they are styling hooks, not branding.
    The colour is **already data-driven**: line 14 sets
    `color_company = company.email_secondary_color or '#714B67'` and line 147 applies it to
    `.odoo_link_text`. So setting `email_secondary_color` reaches this file with zero edits,
    and the fallback here is `#714B67` (the 17.0 brand purple), not `#875A7B`.

#### 20. `castadoo/castadoo_branding_website_slides/__manifest__.py` (Create)

*   **Type / Scope**: Overlay manifest.
*   **Proposed Changes**: `depends: ['castadoo_branding', 'website_slides']`,
    `auto_install: ['website_slides']`.

#### 21. `castadoo/castadoo_branding_website_slides/views/website_slides_templates.xml` (Create)

*   **Type / Scope**: QWeb inheritance.
*   **Proposed Changes**: One inherited record on
    `website_slides.mail_notification_channel_invite`, lines 67–70 of
    `addons/website_slides/data/mail_templates.xml`. The colour here is a hardcoded
    `style="color: #875A7B;"` rather than a `t-att-style` expression, so unlike item 9 it
    must be replaced in the markup — setting `res.company.email_secondary_color` does not
    reach it.

#### 22. `castadoo/castadoo_branding_pos/__manifest__.py` (Create)

*   **Type / Scope**: Overlay manifest for Owl asset templates.
*   **Proposed Changes**: `depends: ['castadoo_branding', 'point_of_sale']`,
    `auto_install: ['point_of_sale']`. This overlay is **optional** per the register's
    35-required / 2-optional split; it is the second optional item.

#### 23. `castadoo/castadoo_branding_pos/static/src/overrides/receipt.xml` (Create)

*   **Type / Scope**: Owl `t-inherit` template.
*   **Proposed Changes**: Inherit `point_of_sale.OrderReceipt`
    (`addons/point_of_sale/static/src/app/screens/receipt_screen/receipt/order_receipt.xml`,
    template `t-name="point_of_sale.OrderReceipt"`, footer `<p>Powered by Odoo</p>` at
    line 140). Owl inheritance fails **silently** if the parent name is wrong — it does not
    raise, it simply does not apply — so this needs a POS-specific verification step, not
    a browser check.

#### 24. `castadoo/castadoo_branding_pos/static/src/overrides/customer_display.xml` (Create)

*   **Type / Scope**: Owl `t-inherit` template.
*   **Proposed Changes**: Inherit the customer-display template
    (`addons/point_of_sale/static/src/app/customer_display/customer_display_template.xml`,
    line 84). Same silent-failure caveat as item 23.

#### 25. `castadoo/castadoo_branding_pos/static/src/overrides/odoo_logo.js` and `odoo_logo.xml` (Create — optional)

*   **Type / Scope**: POS logo component.
*   **Proposed Changes**: The POS has its own logo component at
    `addons/point_of_sale/static/src/app/generic_components/odoo_logo/odoo_logo.{js,xml}`.
    These are the two optional files in the register's count. The `js` file references the
    component name; renaming it is cosmetic and can be skipped without affecting user-visible
    branding, because the image it renders is `logo2.png`, which is replaced in place.

#### 26. Web icon and badge binaries at their existing upstream paths (Modify — binary, base tier)

*   **Type / Scope**: Binary replacements, kept at the **existing** upstream paths.
*   **Proposed Changes**: These are **not** new files in `castadoo/`. They are overwrites
    of upstream blobs at the same path, grouped here because they belong to the base tier
    conceptually rather than to the per-module overlays:
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

These are `Modify` in git terms (a new blob at an existing path) but carry **no** conflict
surface: git records a changed binary, not a hunk, so an upstream edit to the same file is
a whole-file replacement rather than a merge conflict.

#### 27. `addons/web/static/img/logo.png` (Modify — binary)

*   **Type / Scope**: Horizontal lockup.
*   **Proposed Changes**: Portal footer and public pages; 35 references. Mark + outlined
    wordmark, horizontal.

#### 28. `addons/web/static/img/logo2.png` (Modify — binary)

*   **Type / Scope**: Horizontal lockup, POS display.
*   **Proposed Changes**: 2 references. Same lockup as item 27.

#### 29. `addons/web/static/img/logo_inverse_white_206px.png` (Modify — binary)

*   **Type / Scope**: Inverse 206 px mark.
*   **Proposed Changes**: Used on dark backgrounds.

#### 30. `addons/web/static/img/odoo_logo.svg` and `odoo_logo_dark.svg` (Modify — binary)

*   **Type / Scope**: Website configurator logo, light and dark.
*   **Proposed Changes**: Wordmark with text **outlined**, not live `<text>`.

#### 31. `addons/point_of_sale/static/src/img/favicon.ico` (Modify — binary)

*   **Type / Scope**: POS favicon.
*   **Proposed Changes**: Mark-derived `.ico`.

#### 32. `addons/website_links/static/img/default_favicon.png` (Modify — binary)

*   **Type / Scope**: Default link-preview icon.
*   **Proposed Changes**: Mark-derived square PNG.

#### 33. `setup/win32/static/pixmaps/odoo-icon.ico`, `odoo-intro.bmp`, `odoo-slogan.bmp` (Modify — binary)

*   **Type / Scope**: Installer visuals.
*   **Proposed Changes**: `.ico` multi-size; two 24-bit BMPs. `odoo-intro.bmp` is used for
    both the welcome and the uninstall-welcome page (`setup.nsi:136–137`), so one file
    covers both.

#### 34. `addons/web/static/img/nologo.png` — **excluded**

*   **Type / Scope**: Deliberate non-change.
*   **Proposed Changes**: None. It is an intentional placeholder shown when no logo is set.
    Replacing it would misrepresent "no logo" as "CASTADOO logo". Recorded so its absence
    from the diff is not read as an oversight.

### Tier 4 — in-place edits of upstream files

The only files with a recurring conflict surface. Each entry states the mitigation, because
these are the ones a future merge will fight over.

#### 35. `odoo/release.py` (Modify)

*   **Type / Scope**: Package metadata.
*   **Proposed Changes**: **One line.** `description` at line 20, `'Odoo Server'` →
    a CASTADOO string. `product_name` (line 19), `author` (line 33), `author_email`,
    `version_info` (line 15), `url` (line 32) and `nt_service_name` (line 37) all stay.
    `product_name` feeds the datadir via `config.py:50`; `author` is LGPL attribution and
    also part of the Windows datadir path; `nt_service_name` is service identity. This is
    the single most important non-change in the plan.

#### 36. `addons/web/static/src/public/database_manager.qweb.html` (Modify)

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

*   **Type / Scope**: Python controller.
*   **Proposed Changes**: Two lines. `background_color` (line 54) and `theme_color`
    (line 55), both `'#714B67'` → `'#303188'`. The name (line 48) is **not** edited: it
    reads `ir.config_parameter['web.web_app_name']`. The icon paths (lines 60, 89) are
    **not** edited: filenames are preserved by items 26. Two lines, but upstream touches
    this file most years — per `change_register.md`, these are the most expensive lines in
    the register per conflict.

#### 38. `setup/win32/setup.nsi` (Modify)

*   **Type / Scope**: NSIS installer script — 87 strings, the largest single item.
*   **Proposed Changes**: The 87 replacements, plus three decisions that must not be made
    twice:
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
    *   Contact details at lines 423–426 (`support@odoo.com`, `sales@odoo.com`,
        `https://www.odoo.com`, the Odoo phone number) are display strings and must be
        replaced with CASTASOFT equivalents.
    *   `MUI_FINISHPAGE_LINK_LOCATION` (line 160) points at
        `https://www.odoo.com/page/contactus`; it needs a CASTASOFT target.
    *   The French translation block (around lines 203–236) is part of the 87 and must be
        replaced consistently, not partially.

#### 39. `setup/package.py` (Modify)

*   **Type / Scope**: Build/test script.
*   **Proposed Changes**: 8 occurrences, of which **two must not change**: the licence
    header on line 2 (`# Part of Odoo. See LICENSE…`) and the class names
    `OdooTestError` / `OdooTestTimeoutError` (lines 50, 54), which are internal
    identifiers. The display-facing ones are the log and exception messages (lines 78, 83,
    257, 269, 270) and the Debian changelog author on line 323
    (`Odoo Bot <info@odoo.com>`), which should become the CASTASOFT maintainer identity so
    generated packages are attributed correctly.

#### 40. `setup/win32/static/doc/License.rtf` (Modify)

*   **Type / Scope**: Licence text shown in the installer.
*   **Proposed Changes**: Keep the LGPL-3 text verbatim. Add the CASTASOFT copyright line
    and the modification date. **Do not** rename Odoo to CASTADOO in the licence body —
    doing so would misstate the licence's provenance and is the one place where "Odoo"
    must survive verbatim.

#### 41. `odoo/tools/config.py` (Modify — conditional on Open Question 2)

*   **Type / Scope**: Python config defaults.
*   **Proposed Changes**: **Only if** the phone-home question resolves to "disable by
    default". Line 78, `publisher_warranty_url`, would be blanked with a commented
    explanation. If the answer is "leave stock", this file is untouched and the plan's file
    count drops by one. Recorded as conditional rather than assumed, because a privacy
    default is a policy choice.

#### 42. `odoo.conf` / deployment configuration (Modify — deployment artefact, not a repo file)

*   **Type / Scope**: Runtime configuration.
*   **Proposed Changes**: One `addons_path` entry adding `<repo>/castadoo`, so the new
    addons load. `debian/odoo.conf` has a commented `addons_path` line that documents the
    shape. **Not** modified in the repo: `debian/odoo.conf` is upstream packaging and
    editing it creates conflict surface for a value that belongs to the deployment. The
    line goes in the operator's own `odoo.conf`, and the runbook must state it, because
    without it every addon in `castadoo/` is invisible and the rebrand silently does not
    apply.

### Tier 5 — non-code artefacts

#### 43. `README.md` (Modify)

*   **Type / Scope**: Repository documentation.
*   **Proposed Changes**: State that this is a fork of Odoo 17.0 by CASTASOFT, link
    upstream, state the licence and that it is unchanged, and describe the branch model
    (`17.0` mirror + `castadoo/17.0` overlay) so a visitor does not clone the wrong branch.
    The `/web/static/img/logo.png` and `#875A7B` references inside the stock README are
    replaced by items 27 and 9 anyway; this entry covers the prose that explains what the
    fork *is*.

#### 44. `CONTRIBUTING.md` (Create — fork-specific)

*   **Type / Scope**: Maintainer documentation.
*   **Proposed Changes**: The sync procedure, the `git log --first-parent` convention for
    reading overlay history (a direct consequence of D2's merge model), the D7 activation
    mechanism, and the rule that `17.0` is never edited. Without this, the next maintainer
    edits the mirror and the pristine guarantee is gone.

#### 45. `docs/change_register.md` (Create — promoted from working copy)

*   **Type / Scope**: The register, as a versioned artefact.
*   **Proposed Changes**: The existing `change_register.md` moves into the repo and becomes
    the allowlist that Gate 1 checks against. It must be versioned with the code it
    describes, or the gate compares against a stale list.

#### 46. `.github/workflows/brand-gates.yml` (Create)

*   **Type / Scope**: CI workflow — the two gates.
*   **Proposed Changes**: Two jobs on push and on PR into `castadoo/17.0`:
    *   **diff budget**: `git diff --stat upstream/17.0...HEAD`, assert file count ≤ 37 and
        changed-line count ≤ 94, and assert every changed path appears in
        `docs/change_register.md`.
    *   **brand lint**: grep the tree for the enumerated patterns, allowlist by reason
        (`internal identifier`, `D1-C`, `licence notice`, `not user-visible`), fail on any
        unlisted hit. The allowlist must include the six excluded data files with reason
        `D1-C` — `auth_signup`, `portal`, `gamification`, `lunch`,
        `website_crm_partner_assign`, `website_profile` — or the first sync fails on them.
    *   It must also assert `git rev-parse 17.0 == git rev-parse upstream/17.0`, which is
        Goal G2's only enforcement.

#### 47. `castadoo/assets/build_assets.sh` (Create — tooling, optional)

*   **Type / Scope**: Asset generation recipe.
*   **Proposed Changes**: Records the pipeline from the Technical Plan so the binaries in
    items 26–33 can be regenerated: outline the wordmark with `opentype.js` or `fontTools`,
    compose lockups, rasterise with `sharp` or `cairosvg`. Committed as a recipe, not
    automated in CI, because asset regeneration is a design change, not a build step. This
    item is optional: the artefacts can be committed without it, at the cost of losing the
    ability to regenerate consistently.

### Verification Plan

*   **Build / install**: `odoo-bin -d <test_db> -i castadoo_branding --stop-after-init` must
    complete with no warning about missing XML IDs. Repeat with `-i` including each overlay
    whose module is present, or verify D7's chosen mechanism fires.
*   **Path resolution**: `odoo-bin --addons-path=... --version` and a module listing must
    show all 9 addons (1 base + 8 overlays). If `castadoo/` is not on `addons_path`, every
    test below passes against unbranded stock Odoo — so this is checked first, not last.
*   **Unit / integration**: install the test database, then assert on rendered output rather
    than on files:
    *   `GET /web/login` contains no `>Odoo<` and contains `CASTADOO`;
    *   `GET /web/manifest.webmanifest` returns `name`, `background_color: #303188`,
        `theme_color: #303188`, and every `icons[].src` resolves 200;
    *   the offline page renders and its `.card button` computed style is `#303188`;
    *   a rendered notification email contains `Powered by CASTADOO` and no Odoo footer;
    *   a rendered invoice PDF has no `Odoo` in extracted text and reads CASTADOO in title
        metadata.
*   **Static analysis and linting**: the two CI gates (item 46) on every push. `ruff` on the
    new addons' Python (Odoo 17.0 ships `ruff.toml`), and standard Odoo manifest
    validation via `odoo-bin --test-tags /castadoo_branding`.
*   **Test coverage requirement**: not a coverage target. The meaningful metric is the
    diff budget (≤ 37 files, ≤ 94 lines) and a zero-unlisted-hits brand lint. Those are
    pass/fail gates, not percentages.
*   **E2E / manual**:
    *   PWA install on one Android and one iOS device (CUJ 4) — the manifest assertions do
        not prove the install prompt shows the right name.
    *   POS receipt print and customer display (item 23–24) — Owl inheritance fails
        silently, so this cannot be inferred from a browser check.
    *   Windows installer on a clean VM (CUJ 5): install, verify the uninstall registry key,
        verify publisher reads CASTASOFT, uninstall, verify the key is removed and the
        service name never changed.
    *   Email rendering across at least two clients, since CSS-in-email differs.
*   **Sync rehearsal**: run the full sync procedure against a real upstream point release
    before declaring the design done. Both gates must pass, and the conflict count must be
    zero or confined to `setup.nsi`. A sync that requires hand-resolving an inherited view
    means an anchor moved, which is the drift the gates exist to catch.

#### Footnote on file count

The register's headline is **37 upstream files touched**. This plan is numbered 1–47, and
the two figures measure different things, so a reader comparing them should expect a
difference rather than read it as drift:

| Group | Items | Entries | Files |
|---|---|---|---|
| Base addon, required | 1–6 | 6 | 6 |
| Conditional hook (D7 option B only) | 7 | 1 | 1 |
| Per-module overlays | 8–24 | 17 | 17 |
| Optional POS component | 25 | 1 | 2 |
| Upstream binaries overwritten at existing paths | 26–33 | 8 | 16 |
| Deliberate non-change | 34 | 1 | 0 |
| In-place edits of upstream files | 35–40 | 6 | 6 |
| Conditional in-place edit (`config.py`) | 41 | 1 | 1 |
| Deployment artefact, not a repo file | 42 | 1 | 0 |
| Non-code repo artefacts | 43–45 | 3 | 3 |
| CI gates and asset tooling | 46–47 | 2 | 2 |
| **Total** | **1–47** | **47** | **54** |

Of the 54 files, **3 are optional** (items 25 and 47) and **2 are conditional** (item 7
exists only under D7 option B; item 41 exists only if the phone-home question resolves to
"disable"). That leaves **49 files that must exist** for the design as specified.

Two entries are not repo changes and are numbered anyway so nothing is silently missing:
**item 34** is a documented non-change, and **item 42** is an `odoo.conf` line that lives in
the operator's deployment, not the tree. The register's 37 counts upstream paths that
differ after the overlay; this plan counts everything that must exist for the design to
work, including the addon tree that carries the 23 additive overrides and the gates that
keep them honest.

--------------------------------------------------------------------------------

<!-- Provenance: Indicates initial structural drafting via EGM. -->

*Drafted with EGM*
