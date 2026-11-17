# CASTADOO: Rebranded Fork of Odoo 17.0

* **Author:** acer (castasoft@gmail.com)
* **Date:** 2026-11-17

## Overview

Create a fork of `github.com/odoo/odoo` named `castaso/CASTADOO` that shows CASTADOO
branding to users instead of Odoo, while staying cheap to keep in sync with upstream at
point releases. The operator is CASTASOFT (https://castasoft.yukreasi.id). Target series is
17.0 only.

The value the fork provides is not ownership — LGPL-3 denies that — but a shipped product
that carries the CASTASOFT name on every surface a customer sees: login page, web client,
PDF reports, outgoing email, Windows installer, and the PWA/offline page.

The central technical problem is that "rebrand everything visible" and "keep the diff
small so syncs never conflict" pull in opposite directions. Every string changed inside a
file that upstream owns becomes a future merge conflict. Every string left alone becomes a
place where the customer still sees Odoo. The design below draws that line deliberately,
and — this is the part that changed — draws it on the basis of what Odoo 17.0 actually does,
not on what Odoo 18.0 appears to do.

## Analysis

### The numbers that drove the first draft were wrong, and so was one load-bearing finding

The first pass measured an 18.0 working tree and asserted "17.0 is structurally similar."
Re-measuring against the real 17.0 tip (`9c58cae5d6e3cf91ac1cca7df39fb21f68ca6e15`, 40,111
files in tree) changes both the volume and the shape of the work.

| Measurement | Value on 17.0 |
|---|---|
| Files containing `Odoo` at all (incl. `.po`) | 26,560 |
| Lines containing `Odoo` (incl. `.po`) | 111,365 |
| `.po`/`.pot` files containing `Odoo` | 18,920 |
| Non-translation lines containing `Odoo` | 8,985 |
| …of which the mandated notice `# Part of Odoo. See LICENSE…` | 5,496 |
| **Remaining hits after notice, translation, comment and test/demo exclusion** | **1,343 across 591 files** |

The 111,365 figure is an artefact of translation files. The 8,985 figure is mostly a
licence header that must not be touched. The 1,343 figure is still mostly internal
identifiers — `odoo_chart`, `zoomodoo`, `OdooBarChart`, class names, docstrings.

**A case-sensitive grep cannot separate a brand string from an identifier.** That is the
single most important methodological correction in this document. The work budget must be
derived from surfaces that render, not from occurrences of a substring. The inventory below
is built that way.

Two specific reviewer claims were tested and failed:

- *"`home.py` reports 1 hit on 18.0, which signals a refactor that moved the database-manager
  markup into QWeb; on 17.0 it lives in `controllers/database.py` as Python-side HTML
  strings."* — False on both counts. `addons/web/controllers/home.py` and
  `addons/web/controllers/database.py` each contain exactly **one** capital-`O` hit, and it
  is the licence header. The database manager renders
  `addons/web/static/src/public/database_manager.qweb.html` (288 lines, 4 brand strings)
  through a file-path loader. The direction of the reviewer's warning was right — that
  surface is not inheritable — but the mechanism and the count were invented.
- *"The PWA manifest returns a hardcoded name and is therefore not overridable."* — False.
  `addons/web/controllers/webmanifest.py:48` reads
  `ir.config_parameter` `web.web_app_name` with `'Odoo'` only as a fallback default. The
  name needs **zero** source edits.

### What the four replacement mechanisms actually reach

The plan is not "one addon overrides everything". It is four mechanisms with an explicit
disposition for each string. The classification below is verified file by file.

| Mechanism | Cost | What it genuinely covers |
|---|---|---|
| **Database configuration** | zero code | PWA name (`web.web_app_name`), company name/logo/address on login, PDF headers and email bodies, website favicon (`website.favicon`), email brand colours (`res.company.email_secondary_color`) |
| **QWeb inheritance** (new files) | zero conflict surface | backend `<title>`, login footer, offline page, report `<title>`, notification-email layout |
| **Asset replacement** (same filename) | zero path edits | backend favicon, PWA icons, iOS icon, logo PNGs — 10 binaries |
| **In-place edit** | real conflict surface, must be enumerated | `setup/win32/setup.nsi`, `database_manager.qweb.html`, `webmanifest.py` icon path, `odoo/release.py` description, `mail.template` data records |

### `release.py` is not a branding file, and changing `product_name` moves your data

The first draft proposed "~4 lines in `release.py`" as the safe core of the plan. That is
wrong in a way that would have caused a production incident on the first upgrade.

`release.product_name` has **exactly one consumer** in the entire 17.0 tree:

```python
# odoo/tools/config.py:50
return func(appname=release.product_name, appauthor=release.author)
```

That is `appdirs.user_data_dir()`, which computes the **default datadir**. On Linux it is
`~/.local/share/Odoo`; on Windows it is `%LOCALAPPDATA%\OpenERP S.A.\Odoo`. Renaming
`product_name` to `CASTADOO` silently relocates the datadir — every existing filestore,
session directory and attachment becomes invisible, and Odoo creates an empty new one
next to it without an error. `release.author` is the other half of that path on Windows,
which is a second reason the attribution field must stay as it is.

`product_name` is not a display string. It is a directory name.

Field by field:

| Field | Real consumers | Verdict |
|---|---|---|
| `product_name` | `config.py:50` → datadir only | **Freeze at `'Odoo'`.** Not branding. |
| `author` | `config.py:50` → datadir (Windows) + LGPL attribution | **Freeze.** Attribution and path. |
| `version_info` / `version` / `series` | manifest validation, upgrade paths, filestore, addons-data-dir | **Freeze.** Never a branding surface. |
| `url` | one test (`test_res_config_doc_links.py`) | Effectively dead. Changing it achieves nothing. |
| `nt_service_name` | `service/server.py`, `tools/osutil.py` → Windows service identity | **Freeze.** Orphans installed services the uninstaller then cannot find. |
| `description` | log prefix, `--version`, NT event log, PO `Project-Id-Version` | **Change.** The only display-facing field. |

So the honest `release.py` change is **one line**, not four, and the correct one-line change
is `description`. Branding does not live in `release.py`; it lives in templates, data
records and binaries.

### The six named surfaces, enumerated

Scope is the user's list, not "every occurrence of the word". Within that scope the work is
finite and countable.

**1. Backend shell / browser tab** — `addons/web/views/webclient_templates.xml`, 5 hits.
`<title>` fallback, `<meta name="theme-color">`, the login footer link, and two strings on
the offline page. All five are inside `ir.ui.view` templates, all inheritable by xpath.

**2. Login page** — the logo is `/web/binary/company_logo`, i.e. `res.company`. Zero edits;
set the company logo. The only code-branded element is the `Powered by Odoo` anchor at line
130, inherited from `web.login_layout`.

**3. PDF reports** — two hits, both `<title>…'Odoo Report'</title>` in
`addons/web/views/report_templates.xml` (lines 16, 50). This is PDF metadata, not the
visible header. The visible header and footer come from `web.external_layout_standard`,
which renders `company.name`, `company.logo`, `company.street` and so on. **There is no Odoo
text in the rendered PDF body at all.** Two title strings are the entire surface; everything
else is `res.company` data.

**4. Outgoing email** — 20 brand-footer sites in 16 files (19 use `Powered by`, one uses
`Sent by`), plus the brand colour threaded through the same markup.
colour threaded through the same markup. These split into **three** classes, and the split is
the most consequential result of re-measuring, because a reviewer asserted that email footers
are `mail.template` data and therefore unreachable:

- *Inheritable QWeb views* — **11 sites** in `mail/data/mail_templates_email_layouts.xml`
  (the global notification footer, lines 104 and 178), `auth_signup/views/auth_signup_templates_email.xml`,
  `portal/views/portal_templates.xml`, `im_livechat/views/im_livechat_channel_templates.xml`,
  `im_livechat/data/mail_templates.xml`, `hr_expense/data/mail_templates.xml`,
  `website_slides/data/mail_templates.xml`, `digest/data/digest_data.xml` (**two** sites,
  lines 398 and 436 — the first uses `Sent by`, so a `Powered by` grep misses it). The
  filename is misleading: a `<template>` element in `data/` is still an inheritable QWeb
  view. Override by `inherit_id`, no upstream edit.
- *`mail.template` data bodies* — **7 sites in 6 files**: `set_password_email` and
  `mail_template_user_signup_account_created` (`auth_signup`), `mail_template_data_portal_welcome`
  (`portal`), `email_template_badge_received` (`gamification`), `lunch_order_mail_supplier`,
  `email_template_lead_forward_mail` (partner assign), `validation_email` (`website_profile`).
  These are `body_html` fields with `noupdate="1"`. **Decision D1-C: out of scope.** The
  consequence, stated honestly: the portal-invitation and account-created mails will carry a
  `Powered by Odoo` footer, along with four staff- or supplier-facing mails. The reasoning is
  in `change_register.md` §4b, including the fact that `odoo/models.py:5103` means Odoo itself
  never pushes post-install changes to these bodies either — so the cost is a review obligation
  on seven records, not a data-loss trap.
- *Owl asset templates* — **2 sites**, the printed POS receipt and the customer display. These are
  asset-bundled, not `ir.ui.view`, but Owl supports `t-inherit`, so they too can be overridden from
  a new file. The failure mode is silent (a wrong parent name just does not apply), so they need a
  POS-specific verification step.

So 13 of the 20 sites are additive and in scope, and 7 are excluded by decision — the
enumeration below corrected a `Powered by`-only grep that misses the digest's `Sent by`
footer. The first draft
of this brief had the ratio backwards in one direction and the mechanism wrong in another; the
per-line enumeration, including the seven exclusions, is in `change_register.md` §Surface 4.

**5. Windows installer** — `setup/win32/setup.nsi`, **87 hits in one file** including
`PRODUCT_NAME`, `PUBLISHER`, `BrandingText`, every dialog caption, the French translation
block, and the service install/uninstall registry keys. One file, one edit, no inheritance
path. It cannot be reached by an addon at all — an installer addon is a contradiction.

**6. PWA / offline** — `webmanifest.py` name is config (0 edits); `background_color` and
`theme_color` are hardcoded `#714B67`; icon URLs hardcode `/web/static/img/odoo-icon-%s.png`;
`_icon_path()` hardcodes the offline icon. The offline page itself is a QWeb template.

### Brand colour: there are four purples, not two

The first draft named `#875A7B` and `#71639e`. 17.0 actually carries four:

- `#714B67` — the 17.0 brand purple. Manifest `theme_color`/`background_color` (2 hits),
  `primary_variables.scss`, `digest_data.xml`, `hw_posbox_homepage/override.css` (5 hits).
- `#71639e` — the `theme-color` meta in `webclient_templates.xml:251`. A third value,
  inconsistent with both, almost certainly a leftover.
- `#875A7B` — the legacy e-mail button and link colour, also `res.company
  .email_secondary_color`'s fallback. Appears in `README.md` (3), and in the mail templates
  as a *default* rather than a literal.
- `#9E588B` — a **fourth** purple, used only by `hr_expense`
  (`data/mail_templates.xml` lines 31 and 49, button and footer). It is not
  `email_secondary_color`-driven, so no company setting reaches it, and a global
  `#875A7B` find-and-replace would pass over it.

The distinction matters because only the `mail` notification layout and the `digest`
template read the company field. Setting `res.company.email_secondary_color` fixes those
four sites with no file edit; `auth_signup` (2), `im_livechat` (1), `website_slides` (1)
and `hr_expense` (1) hardcode their literal and must be edited in markup.

The SCSS case is worse than it looks. `primary_variables.scss:73` reads
`$o-brand-odoo: $o-community-color !default;` — so the real variable of interest is
`$o-community-color`, and `!default` means appending a later file in the bundle cannot win.
Retheming the backend means editing the compiled-variable file, which is a permanent
conflict site in a file that changes between releases. Recommendation: do not retheme the
backend.

### The asset problem is a licence problem, not a rasteriser problem

`logo.svg` is a mark, 89.94 × 110.97 (portrait, 0.81:1). `CASTADOO.svg` is a wordmark,
683.22 × 107.6 (6.35:1). They are not interchangeable in any slot:

- PWA icons are square, 192 and 512, and maskable with a safe-area inset. A 6.35:1 wordmark
  is illegible there.
- A 32 px favicon needs the mark, and needs to survive being 32 px.
- The login lockup and the PDF header want horizontal.

So the deliverable is an asset *set*, not an asset swap: square icon (mark, with safe-area
padding), horizontal lockup (mark + wordmark), monochrome favicon, and a 206 px inverse mark
to replace `logo_inverse_white_206px.png`.

The wordmark renders live `<text>` in Garamond plus one empty `<text>` node. Garamond happens
to be installed on this machine (`GARA.TTF`), which is exactly why the defect is invisible
here — everywhere else the fallback serif renders and the logo changes shape. Text must be
converted to outlines. That is a vector operation and does not need a rasteriser;
`opentype.js` on the installed Node 22 or `fontTools` on Python 3.14 emits path data from the
font file. PNG rasterisation is only needed for the icon set, and does need one dependency
installed (`sharp` via npm, or `cairosvg` via pip).

The font itself is the open question. Garamond as shipped is not freely redistributable, and
outlining a wordmark fixes rendering but not the licence to embed those glyph shapes. EB
Garamond (OFL) removes both problems.

### Silent drift is the failure mode that survives a clean merge

An xpath override whose anchor upstream renames fails loudly at install. That is fine.

The dangerous case is an override that still applies cleanly when upstream **adds** new
brand copy in the same region. Nothing conflicts, nothing errors, the new upstream string
ships, and it is discovered by a customer. Git cannot catch this and neither can a human
reading a merge diff of 40,000 files.

So the plan needs two gates that run on every sync, not one:

1. **An allowlisted change register** — every touched upstream path, its mechanism class,
   and why no cleaner mechanism reaches it. The diff either matches the register or the sync
   fails.
2. **A brand lint** — grep the post-sync tree for the enumerated patterns and fail on any hit
   that is not in a reviewed, justified allowlist. The allowlist must be able to say
   "internal identifier, not user-visible" explicitly, or the lint becomes noise and gets
   disabled.

The first draft treated the register as a nice-to-have. It is the artefact that makes "small
diff" falsifiable instead of aspirational.

### Sync mechanics: settled on merge, and why that mattered

Rebasing a *published* branch rewrites every commit SHA on every point release. Any fork,
pinned CI ref or submodule breaks. For an LGPL-3 work it also discards the modification
provenance the licence asks you to keep, because `git log` no longer shows what was changed
when. Three shapes were weighed:

- **Merge** upstream point releases into a long-lived overlay branch with `--no-ff`.
  **Chosen (D2).** Monotonic history, never force-pushes, conflicts resolved once per
  release. Costs a non-linear graph.
- **Rebase**, publishing immutable annotated tags `castadoo-17.0.<upstream>-r<n>` as the
  only supportable artefacts and forbidding consumers from tracking the branch head.
  Rejected: makes the branch itself unsupportable, which is a worse default than a noisier
  graph.
- **Patch series** replayed onto a clean upstream tag at build time. Rejected: provable
  ancestry to a signed upstream tag is the strongest auditability position, but it requires a
  build step before anything can be run, and this plan produces a source tree, not a build
  pipeline.

The practical consequence of choosing merge: the overlay branch **can** be published, its
SHAs are stable, and the LGPL "mark modifications with dates" obligation is discharged by the
merge commit message. That last point is why merge wins on more than aesthetics — it turns a
compliance chore into a by-product of syncing.

The fork itself also has a default-branch trap: GitHub forks at the upstream default, which
is `20.0`. Anyone who clicks "Download" or clones without `-b` gets unbranded Odoo 20.0. The
sequence must be fork → set default branch to `17.0` → verify with `git ls-remote`. This is
cheap to fix and expensive to discover late.

## Goals vs. Non-Goals

**In-Scope Goals**

- `castaso/CASTADOO` carries a real GitHub fork relationship to `odoo/odoo`, so objects are
  shared and local storage stays small.
- Local working copy is a blobless clone of *the fork* (444 MB measured, full history, real
  merge bases), not of upstream.
- Branch `17.0` is byte-identical to `upstream/17.0` and provably so.
- One long-lived overlay branch carries every CASTADOO change.
- CASTADOO branding on the six named surfaces: backend shell and login, PDF report
  documents, outgoing email, Windows installer, PWA manifest and offline page, favicon and
  app icons.
- LGPL-3 respected: notices kept, modifications dated, no relicensing, no relicensing claim.
- A written sync procedure with a trigger, an owner, and a conflict fallback.
- A committed change register plus the two CI gates that make drift visible.

**Out-of-Scope Non-Goals**

- Relicensing. LGPL-3 cannot become MIT or proprietary and the notices cannot be stripped.
- Renaming internal identifiers: the `odoo` Python package, `odoo-bin`, `ODOO_RC`,
  `odoo.conf`, the datadir, `version_info`/`series`. These break addons, upgrades and sync.
- Changing `release.product_name`, `release.author` or `release.nt_service_name`
  (datadir relocation, attribution, service orphaning — see Analysis).
- Editing the 18,920 `.po`/`.pot` files in place.
- Rewriting help text, tooltips, error messages, tour copy and demo content to remove every
  occurrence of the word. Out of scope by decision, recorded as accepted leakage.
- Forking more than one series. 17.0 only.
- Building, signing, updating or supporting a distributable product. This produces a source
  tree.

## Alternatives Weighed

- **`--depth 75` shallow clone.** Rejected on measurement. Depth counts commits: 75 commits
  on 17.0 spans 34.5 days, while 16.0 is four years back — the premise that 75 reached 16.0
  was false. Independently, `git push` refuses a shallow history
  (`! [remote rejected] (shallow update not allowed)`, tested against a local bare remote),
  and a shallow base destroys merge-base so every point-release merge conflicts on every
  file. Rejected by author.
- **Manual mirror pushed into `castaso/CASTADOO`.** Rejected: a single-branch 17.0 clone is
  ~4.76 GB against a GitHub-enforced 2 GB push limit. Progressive ref advancement could work
  but is a multi-hour fragile procedure. Rejected by author in favour of the fork.
- **Blobless clone of `odoo/odoo`, then push to the empty repo.** Rejected: the blobs live
  only on the promisor remote; materialising the full history against a different, empty
  repository is the same 17.7 GB transfer. Also, the earlier local test of this idea was
  invalid — the test remote printed `filtering not recognized by server, ignoring`, so it
  never exercised bloblessness. The surviving constraint is ordering: **fork first, then
  clone blobless from the fork**.
- **Delete `castaso/CASTADOO` first, then fork into the name.** Rejected by review on safety
  grounds: destructive-first, no fallback if fork creation fails (org policy, fork-network
  restriction, name validation), and the freed name is unreserved during the gap. Replaced
  by rename-then-fork, with deletion as deferred cleanup. Rejected by author.
- **Edit all 290 user-visible files in place.** Rejected: guarantees divergence on exactly
  the lines upstream touches, making "pristine" and "conflict-free" mutually exclusive. Also
  the 290 figure was never a count of brand strings.
- **Single `castadoo_branding` addon depending on every module whose email template it
  overrides.** Rejected: Odoo auto-installs manifest dependencies, so one addon covering
  `sale`, `account`, `crm`, `hr_expense` and `mail` forces ~15–25 business modules onto every
  database including minimal and test ones. Replaced by a base addon depending only on
  `web`, plus per-module overlays with `auto_install: True`.
- **Change `release.product_name` to `CASTADOO`.** Rejected on evidence: single consumer,
  `appdirs.user_data_dir`, i.e. the datadir. It relocates filestores and orphans existing
  databases. Rejected by author.
- **Retheme the backend to `#303188`.** Not chosen. Requires editing compiled SCSS
  variables (`!default` resolves before any later file in the bundle), which is a permanent
  conflict site for no user-visible brand gain. Author accepted leaving the backend purple.
- **Re-target to 18.0 or 19.0.** Not chosen; author confirmed 17.0. Raised as a risk because
  17.0 Community may now be at or past end of upstream maintenance, which would hollow out
  the "sync at point releases" premise over time.
- **Edit the 3,410 `.po` files that contain `Odoo` in a `msgid`.** Not chosen, provisionally:
  the operator is Indonesian, so `id_ID` is plausibly a primary locale, and the cost of
  leaving it is that Indonesian users read "Odoo". Note the second-order effect either way —
  renaming an English source string changes its `msgid` and drops *every* locale back to the
  new English text until retranslated. The cheap mitigation is a small branding-module
  `.po` that overrides `msgstr` only, never `msgid`.
- **Re-declare the 7 `mail.template` bodies to remove their footers.** Rejected by author
  under decision D1-C. Rationale recorded in `change_register.md` §4b, including the correction
  that `odoo/models.py:5103` (`if not (update and d_noupdate)`) means upstream never pushes
  post-install changes to these bodies either — so the cost is a standing review obligation on
  seven records, not the permanent data-loss trap an earlier draft claimed. A `post_init`
  migration that rewrites `body_html` in place was considered as a middle path and rejected as
  having its own rollback hazard.
- **Edit all readable text — help strings, tooltips, error messages, tours, doc links.** Rejected
  by author. ~1,150 additional strings, each needing a human judgement on whether `Odoo` there
  means *this product* or *the software it derives from*. Getting that wrong is a trademark
  statement, not a typo, and it cannot be automated.

## Key Decisions & Staging for Next Steps

**Settled, with the evidence that settled it**

1. Fork server-side into `castaso/CASTADOO`; clone **blobless from the fork**, not upstream.
   Ordering is load-bearing: fork first.
2. Rename the existing empty repo, fork into the freed name, delete the old one only after
   the fork is verified. Deletion is never the first step.
3. Set the fork's default branch to `17.0` and verify with `ls-remote`. Upstream default is
   `20.0` and would otherwise be what an unqualified clone receives.
4. Branch model: `17.0` is a fast-forward-only mirror; all changes live on the overlay branch.
   "Pristine" is defined operationally as `git rev-parse 17.0 == git rev-parse upstream/17.0`.
5. `release.product_name`, `author`, `version_info`, `version`, `series`, `nt_service_name`
   are frozen. Only `description` changes. Datadir, `odoo.conf`, `ODOO_RC` and the Windows
   service name stay as Odoo, permanently, with that rationale written down.
6. Mechanism is per-class, not "one addon does everything": database config, QWeb inheritance,
   same-filename asset replacement, enumerated in-place edits.
7. The backend stays Odoo purple. Colour changes are limited to the manifest, the
   `theme-color` meta, and the email colour *default* — all of which are single values, not
   compiled-variable graphs.
8. Branding is two tiers: `castadoo_branding` depending only on `web`, plus thin per-module
   overlays with `auto_install: True`.
9. The change register and the two CI gates (diff budget, brand lint) are in scope, not
   optional. Without them the plan cannot distinguish "still clean" from "quietly drifted".
10. The `.po` corpus is not edited in place. Indonesian coverage, if wanted, is a
    `msgstr`-only overlay in the branding module.
11. Assets: mark-derived square icon, horizontal lockup, monochrome favicon, 206 px inverse
    mark. Text converted to outlines. EB Garamond (OFL) rather than system Garamond.
12. **Scope boundary (D1-C).** Six named surfaces, excluding the 7 `mail.template` body
    re-declarations. 37 files, 94 edit lines, 23 additive overrides, ~17 hours. Full
    enumeration in `change_register.md`. Accepted consequence: portal-invitation and
    account-created mails keep a `Powered by Odoo` footer and Odoo purple.
13. **Sync model (D2).** Merge upstream point releases into the overlay branch with
    `--no-ff`. Consequences that follow from it:
    - The overlay branch is **safe to publish**. Every commit SHA is stable across releases,
      so customer forks, pinned CI refs and submodules do not break — which is what makes
      publishing it possible at all.
    - The branch is **never force-pushed**. `17.0` fast-forwards from `upstream/17.0`; the
      overlay merges from it. No history is rewritten anywhere.
    - Each point release adds **one merge commit** to the overlay. That commit is the natural
      place to record the LGPL modification date and the upstream tag it consumed, which turns
      licence provenance from a manual chore into a side effect of the process.
    - Conflicts are resolved **once per merge**, not replayed per commit, so a conflict in
      `setup.nsi` is resolved in one place even though 87 lines of it were edited.
    - Cost: a non-linear graph, and `git log --first-parent` becomes the way to read the
      overlay's own history. Record that convention in the repo's CONTRIBUTING notes or it
      will confuse the next maintainer.

**Open, and needed before implementation starts**

1. **17.0 upstream support window.** Confirm 17.0 Community still receives point releases
   before committing to "sync at point releases" as the maintenance model.
2. **Phone-home.** `odoo/tools/config.py:78` defaults `publisher_warranty_url` to
   `http://services.openerp.com/publisher-warranty/` — note it is `openerp.com`, not
   `odoo.com`, and it is a daily outbound call carrying instance metadata. Disable by default
   with a commented line, or leave stock?
3. **Deployment shape.** One tenant per install, or a shared multi-database host? Changes
   per-release asset recompilation from a constant to O(databases) and changes how much the
   CI gates matter.
4. **Bandwidth figure.** Two measurements disagree by ~34×: 188 MB in 746 s (≈0.25 MB/s)
   versus a 4.7 GB clone in 544 s (≈8.6 MB/s). Every cost estimate above depends on which is
   real. Re-measure once with the exact intended command before quoting any duration.
5. **Installer publisher.** `PUBLISHER 'Odoo S.A.'` in an NSIS manifest declares the publisher
   of *this binary*, not a copyright notice. Left alone, the installer reports Odoo S.A. as
   publisher and throws unknown-publisher warnings once signed with the CASTASOFT certificate.
   Recommendation: `CASTASOFT` in `PUBLISHER`, LGPL notice preserved in `COPYRIGHT`/`NOTICE`.
6. **Wordmark font.** Convert with the installed Garamond (`GARA.TTF`) to match the current
   design exactly, or rebuild on EB Garamond (OFL) and accept a small shape change in exchange
   for no font-embedding question.
