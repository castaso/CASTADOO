# CASTADOO Change Register

**Target:** `odoo/odoo` tip `9c58cae5d6e3cf91ac1cca7df39fb21f68ca6e15` (branch 17.0)
**Measured:** 2026-11-16, verified 2026-11-17, via `git grep` against the real 17.0 tree (40,111 files)
**Purpose:** enumerate every file and line in the six named surfaces, with the replacement
mechanism, so the scope boundary can be decided on evidence instead of on a file count.
**Status:** committed ahead of the plan it describes. The design cites it, so it lands with
the design. Once `castadoo/change_manifest.toml` and `castadoo/tools/render_manifest.py`
exist, this file is regenerated from the manifest rather than edited; until then it is the
hand-written enumeration, and it is the only such file in the tree.

---

## How to read this

**Mechanism** — what has to change, and whether it touches an upstream-owned file:

| Code | Mechanism | Touches upstream? | Conflict surface |
|---|---|---|---|
| `CFG` | database setting or `ir.config_parameter` | no | **none** |
| `BIN` | replace a binary, keep the same path and filename | yes (binary) | **none** — git sees a new blob, not a hunk |
| `INH` | QWeb `<xpath>` inheritance in a new file | no | **none**, unless upstream renames the anchor |
| `JS` | additive JS registry patch, new file | no | **none** |
| `OWL` | Owl `t-inherit` asset template, new file | no | **none** |
| `DATA` | re-declare an existing data record | yes (data file) | **permanent** — your version wins forever |
| `EDIT` | edit the line in place | yes | **recurring** — every upstream touch |

**Conflict risk** is the risk at a *point-release sync*, not at first build.

**Effort** is a build-time estimate in person-hours, one person who knows Odoo. `0` means
configuration only. It is an estimate, not a measurement, and it excludes asset design.

---

## Corrections this measurement made to the brief

| Claim in the draft | Measured | Effect |
|---|---|---|
| "~4 lines in `release.py`" | `product_name` has **one** consumer: `appdirs.user_data_dir()`. It is the datadir. | Freeze it. Net release.py change is **1 line**. |
| "Email footers are `mail.template` data, so no inheritance possible" | 20 sites: **11 QWeb views, 7 `mail.template` bodies, 2 Owl asset templates**. One footer's verb is `Sent by`, so a `Powered by` grep finds 19. | ~90% of the email surface becomes additive |
| "`home.py` = 1 hit signals 17.0 db-manager HTML in `database.py`" | Both files: 1 hit each, the licence header. Manager renders `database_manager.qweb.html`. | Claim false; real surface is 4 lines in another file |
| "PWA manifest name is hardcoded" | `webmanifest.py:48` reads `ir.config_parameter['web.web_app_name']` | 0 edits needed |
| "PDF report headers need rebranding" | `external_layout_standard` renders `company.name`/`company.logo`. Zero literal `Odoo` in the rendered PDF body. | PDF = 2 metadata-title strings only |
| "`publisher_warranty_url` → `services.odoo.com`" | It is `services.openerp.com` (`odoo/tools/config.py:78`) | Cosmetic, but it was wrong |
| "`setup.nsi` has 45 Odoo strings" | 729 lines, **89** contain `Odoo` — **114 occurrences** (119 any-case) | Installer cost was understated ~2×; it is also the surface that justifies the fork |
| "Odoo purple is `#875A7B` and `#71639e`" | **Four** distinct purples: `#714B67` (brand/17.0), `#71639e` (stray meta), `#875A7B` (legacy email), `#9E588B` (`hr_expense` mail only) | Only the `mail` and `digest` layouts read the company field; 5 of 10 sites hardcode a literal |
| "290 XML/JS/SCSS files need editing" | 1,343 non-test grep hits / 591 files — but grep cannot tell `odoo_chart` from brand copy | Not a work estimate |

---

## Surface 1 — Backend shell, browser tab, offline page

**File:** `addons/web/views/webclient_templates.xml` — 1 file, 8 register items, **0 in-place edits**

| ID | Line | Template id | Current | Mechanism | Effort |
|---|---|---|---|---|---|
| S1.01 | 22 | `web.layout` | `<title t-esc="title or 'Odoo'"/>` | `INH` xpath `//title` → set `@t-esc` fallback to `'CASTADOO'` | 0.25 |
| S1.02 | 23 | `web.layout` | `t-att-href="x_icon or '/web/static/img/favicon.ico'"` | none — replace the blob at that path | 0 |
| S1.03 | 94–95 | `brand_promotion_message` | `<img alt="Odoo" src="/web/static/img/odoo_logo_tiny.png">` | `INH` xpath `//img` → `@alt`, `@src` | 0.25 |
| S1.04 | 130 | `web.login_layout` | `Powered by <span>Odoo</span>` + `href="https://www.odoo.com?…auth"` | `INH` xpath on the anchor → href, text | 0.25 |
| S1.05 | 251 | `web.webclient_bootstrap` | `<meta name="theme-color" content="#71639e"/>` | `INH` → `@content` = `#303188` | 0.1 |
| S1.06 | 253 | `web.webclient_bootstrap` | `apple-touch-icon` → `odoo-icon-ios.png` | `BIN` same filename | 0 |
| S1.07 | 330 | `webclient_offline` | `<img … alt="Odoo logo">` | `INH` → `@alt` | 0.1 |
| S1.08 | 332 | `webclient_offline` | `…Odoo will load as soon as…` | `INH` → `@t-out` / text node | 0.25 |
| S1.09 | 317, 319 | `webclient_offline` | inline CSS `background-color: #714B67` / `border: 1px solid #714B67` | `INH` → `@t-out` of the `<style>` block | 0.5 |

Note S1.09: the offline page carries an inline `<style>` block with the brand purple. Text-node
rewrites inside a `<style>` are more fragile than the rest of this surface — this is the one
item in S1 that deserves a smoke test after every sync.

**Not in this surface, but adjacent:** `addons/web/static/src/public/database_manager.qweb.html`
renders *before* login and shows 4 brand strings. It is loaded by file path, not as a view, so
nothing inheritable reaches it.

| ID | Line | Current | Mechanism | Effort |
|---|---|---|---|---|
| S1.10 | 4 | `<title>Odoo</title>` | `EDIT` | 0.1 |
| S1.11 | 33 | `Warning, your Odoo database manager is not protected.` | `EDIT` | 0.1 |
| S1.12 | 102 | `…sent to Odoo online services…` + Privacy Policy link | `EDIT` | 0.1 |
| S1.13 | 144 | `…Odoo needs to know if this database was moved or copied.` | `EDIT` | 0.1 |

---

## Surface 2 — Login page

| ID | Element | Mechanism | Effort |
|---|---|---|---|
| S2.01 | Logo (`/web/binary/company_logo`) | `CFG` — set `res.company.logo` | 0 |
| S2.02 | `Powered by Odoo` footer link | already covered by S1.04 | 0 |
| S2.03 | Database selector / manager pages | covered by S1.10–S1.13 | 0 |

**Surface total: 0 additional files.** The login screen is the cheapest surface in the plan —
its only code-branded element is the footer link, and that is inherited for free with the
backend shell.

---

## Surface 3 — PDF reports

**File:** `addons/web/views/report_templates.xml`

| ID | Line | Template | Current | Mechanism | Effort |
|---|---|---|---|---|---|
| S3.01 | 16 | `web.report_layout` | `<title><t t-esc="title or 'Odoo Report'"/></title>` | `INH` | 0.2 |
| S3.02 | 50 | `web.report_preview_layout` | same string, separate template | `INH` (second record) | 0.2 |
| S3.03 | — | visible header + footer | `company.name`, `company.logo`, address | `CFG` — `res.company` | 0 |

`addons/account/static/src/img/Odoo_logo_O.svg` is not a report header. It is the letterhead
marker stencilled into the QR code on invoice reports; swapping it changes the QR, so leave it
unless the QR is being re-branded deliberately.

---

## Surface 4 — Outgoing email

19 "Powered by Odoo" sites in 16 files, plus one more that a `Powered by` grep misses: the
digest carries a second footer whose verb is `Sent by` (`digest_data.xml:398`), inside the
same template as its `Powered by` footer at line 436. So the real total is **20 sites in 16
files**. Four of the sites put the verb and `Odoo` on separate lines (the two
`mail_notification_*` templates, the digest footer, the POS customer display), so a
single-line grep undercounts those too. The split into three classes matters, because they
cost very different amounts.

### 4a — QWeb views (`INH`, no upstream edit) — 11 sites, 8 files

| ID | Path | Line | Template id |
|---|---|---|---|
| S4.01 | `addons/mail/data/mail_templates_email_layouts.xml` | 104 | `mail_notification_layout` |
| S4.02 | same | 178 | `mail_notification_light` |
| S4.03 | `addons/auth_signup/views/auth_signup_templates_email.xml` | 81 | `reset_password_email` |
| S4.04 | same | 143 | `alert_login_new_device` |
| S4.05 | `addons/portal/views/portal_templates.xml` | 288 | `portal_record_sidebar` |
| S4.06 | `addons/hr_expense/data/mail_templates.xml` | 49 | `hr_expense_template_register_no_user` |
| S4.06b | same | 31 | `hr_expense_template_register` — button `#9E588B`, a **different template** from S4.06 |
| S4.07 | `addons/im_livechat/data/mail_templates.xml` | 91 | `livechat_email_template` |
| S4.08 | `addons/im_livechat/views/im_livechat_channel_templates.xml` | 79 | `support_page` |
| S4.09 | `addons/website_slides/data/mail_templates.xml` | 69 | `mail_notification_channel_invite` |
| S4.10 | `addons/digest/data/digest_data.xml` | 436 | `digest_mail_main` |
| S4.20 | `addons/digest/data/digest_data.xml` | 398 | `digest_mail_main` (second footer, verb is `Sent by`) |

S4.01 and S4.02 carry most of the traffic — the notification layout is the footer under every
internal notification. Fix those two and the default footer is CASTADOO everywhere.

### 4b — `mail.template` data bodies — **OUT OF SCOPE (decision D1-C)**

Seven sites in 6 files. **Not rebranded.** Recorded here so the exclusion is a documented
decision rather than an oversight, and so the brand lint can allowlist them by id.

| ID | Path | Line | Record id | Consequence of leaving it |
|---|---|---|---|---|
| S4.11 | `addons/auth_signup/data/mail_template_data.xml` | 91 | `set_password_email` | portal invitation footer says Odoo |
| S4.12 | same | 237 | `mail_template_user_signup_account_created` | account-created mail footer says Odoo |
| S4.13 | `addons/portal/data/mail_template_data.xml` | 81 | `mail_template_data_portal_welcome` | portal welcome footer says Odoo |
| S4.14 | `addons/gamification/data/mail_template_data.xml` | 94 | `email_template_badge_received` | internal gamification footer |
| S4.15 | `addons/lunch/data/mail_template_data.xml` | 134 | `lunch_order_mail_supplier` | supplier-facing footer |
| S4.16 | `addons/website_crm_partner_assign/data/mail_template_data.xml` | 92 | `email_template_lead_forward_mail` | staff-facing footer |
| S4.17 | `addons/website_profile/data/mail_template_data.xml` | 95 | `validation_email` | staff-facing footer |

Why this is the right call: these records are `noupdate="1"`. Re-declaring `body_html` applies
at module install and then stops. But the mechanism is not the poisoned-upgrade path claimed in
an earlier draft — `odoo/models.py:5103` reads

```python
if not (update and d_noupdate):
    to_update.append(data)
```

so a `noupdate="1"` record is skipped on *every* module update, including upstream's own. Odoo
never pushes a post-install change to these bodies either. The accurate cost is narrower and
worth stating precisely:

- **Existing databases:** neither stock nor branding ever rewrites these bodies after install.
  Overriding them costs nothing you did not already have.
- **Fresh installs:** upstream's current body and your body are both candidates, and load order
  decides. If `castadoo_branding` is installed, yours wins — so a *new* deployment ships your
  footer, and any later upstream body improvements reach new installs only if you drop the
  override.

So the real trade is: 7 re-declared records that must be re-checked when upstream changes them,
in exchange for a footer line. The maintenance burden is a review obligation, not a silent
data-loss trap. That is a smaller cost than the earlier draft implied, and D1-C remains a
defensible call on the narrower grounds that seven records need watching for a line of
boilerplate.

**Mitigation available without forking the records:** the footer a customer actually sees on
these mails is only Odoo because the body carries its own "POWERED BY" table. A `post_init`
hook that rewrites the existing `body_html` in place — a database migration, not a data
re-declaration — changes the rendered footer while leaving upstream's record intact for future
syncs. It is a 20-line migration with a rollback hazard of its own, so it is recorded as an
option, not chosen here.

Brand lint implication: `auth_signup`, `portal`, `gamification`, `lunch`,
`website_crm_partner_assign` and `website_profile` data files must be on the lint allowlist with
the reason "D1-C", or the first sync will fail on them.

### 4c — Owl asset templates (`OWL` via `t-inherit`) — 2 sites

| ID | Path | Line | Context |
|---|---|---|---|
| S4.18 | `addons/point_of_sale/static/src/app/screens/receipt_screen/receipt/order_receipt.xml` | 140 | printed POS receipt |
| S4.19 | `addons/point_of_sale/static/src/app/customer_display/customer_display_template.xml` | 84 | customer-facing display |

Owl templates support `t-inherit` in a new asset file, so these are additive too — but Owl
inheritance fails at *asset bundle* load, silently, if the parent name is wrong. Verify in
POS, not in the browser.

### 4d — Brand colour, per site (the uniform claim was wrong)

An earlier version of this section said `#875A7B` is the fallback for
`company.email_secondary_color` "in every S4.01–S4.10 fragment", so setting the company
field covers all of them. **Measured, that is false for five of the ten in-scope sites.**

| Sites | Colour mechanism as written upstream | Cost |
|---|---|---|
| S4.01, S4.02 (`mail` layout) | `t-att-style="'color: ' + (company.email_secondary_color or '#875A7B') + ';'"` | `CFG` — 0 edits |
| S4.10, S4.20 (`digest`) | `color_company = company.email_secondary_color or '#714B67'`, applied to `.odoo_link_text` at line 147 | `CFG` — 0 edits |
| S4.03, S4.04 (`auth_signup`) | inline `style="color: #875A7B;"` | markup replacement |
| S4.07 (`im_livechat` data) | inline `style="color: #875A7B;"` | markup replacement |
| S4.09 (`website_slides` data) | inline `style="color: #875A7B;"` | markup replacement |
| S4.06 (`hr_expense`) | inline `style="color:#9E588B;"` | markup replacement |

Two consequences that were previously missed:

1. **A fourth purple.** `#9E588B` appears only in `hr_expense` (footer line 49, button
   line 31). It is not the fallback of anything and no company setting reaches it. A global
   `#875A7B` find-and-replace silently leaves this file purple.
2. **The digest fallback is `#714B67`, not `#875A7B`.** So the digest is data-covered, and
   the residue under D1-C is narrower than previously stated: only the excluded
   `mail.template` bodies (S4.11–S4.17) keep Odoo purple.

Setting `res.company.email_secondary_color = #303188` therefore covers 4 of 10 sites, and
the other 5 need their literal replaced in the inherited markup. Both facts matter for the
effort estimate, because "set one field" and "edit five templates" are different work.

---

## Surface 5 — Windows installer

| ID | Path | Hits | Mechanism | Effort |
|---|---|---|---|---|
| S5.01 | `setup/win32/setup.nsi` | **89 lines / 114 occurrences** of `Odoo` (729 lines total) | `EDIT` | 3–4 |
| S5.02 | `setup/win32/static/pixmaps/odoo-icon.ico` | 1 binary | `BIN` | 0 |
| S5.03 | `setup/win32/static/pixmaps/odoo-intro.bmp` | 1 binary | `BIN` | 0 |
| S5.04 | `setup/win32/static/pixmaps/odoo-slogan.bmp` | 1 binary | `BIN` | 0 |
| S5.05 | `setup/package.py` | 9 lines (1 user-visible) | `EDIT` (build script console output) | 0.25 |
| S5.06 | `setup/win32/static/doc/License.rtf` | 1 | `EDIT` (licence text, must keep LGPL) | 0.5 |

`setup.nsi` is the single largest line item in the plan and cannot be delegated to an addon:
`PRODUCT_NAME`, `PUBLISHER`, `BrandingText`, every dialog caption, the whole French translation
block, and the service install/uninstall registry keys.

Two decisions sit inside S5.01 and should not be made twice:

- **`PUBLISHER 'Odoo S.A.'` (line 44).** In an NSIS manifest this is the publisher of *this
  binary*, not a copyright notice. Left as-is, your installer reports Odoo S.A. as its
  publisher and gets an unknown-publisher warning when signing is attempted with your
  certificate. Set it to `CASTASOFT` and keep the LGPL notice in `COPYRIGHT`/`NOTICE`.
- **`nt_service_name` / service registry keys.** Every prior `odoo-server-17.0` service
  becomes uninterruptible by the new uninstaller. Invisible to almost all users, and not a
  branding element. Leave the service identity alone; rebrand only the display strings.

---

## Surface 6 — PWA, offline page, icons

**File:** `addons/web/controllers/webmanifest.py`

| ID | Line | Current | Mechanism | Effort |
|---|---|---|---|---|
| S6.01 | 48 | `get_param('web.web_app_name', 'Odoo')` | `CFG` — set the parameter | 0 |
| S6.02 | 54 | `'background_color': '#714B67'` | `EDIT` → `#303188` | 0.1 |
| S6.03 | 55 | `'theme_color': '#714B67'` | `EDIT` → `#303188` | 0.1 |
| S6.04 | 60 | `'src': '/web/static/img/odoo-icon-%s.png' % size` | `BIN` — keep filenames, 0 edits | 0 |
| S6.05 | 89 | `_icon_path()` → `web/static/img/odoo-icon-192x192.png` | `BIN` — same file as S1.07 | 0 |
| S6.06 | 22–31 | service worker content | none | 0 |

Keeping the existing `odoo-icon-*` filenames is deliberate: it converts 3 code edits into 0,
and the filenames are never visible to a user.

---

## Binary asset inventory

**16 replacements**, listed below with 3 further entries recorded as deliberate non-changes so
their absence is not read as an oversight. All replacements sit at the same path, so **zero
reference edits** are needed if filenames are kept. Of the 16, **13 are true binaries** and
**3 are SVG/XML** — the SVGs diff line by line and conflict inside the file.

| Path | Size | Role | Needs |
|---|---|---|---|
| `addons/web/static/img/favicon.ico` | 1,150 B | backend favicon | 16/32/48 multi-size `.ico`, mark |
| `addons/web/static/img/odoo-icon-192x192.png` | 6,016 B | PWA 192 | 192 square, maskable safe area |
| `addons/web/static/img/odoo-icon-512x512.png` | 17,285 B | PWA 512 + offline page | 512 square |
| `addons/web/static/img/odoo-icon-ios.png` | 27,552 B | iOS home screen | 180 square, opaque bg |
| `addons/web/static/img/odoo-icon.svg` | 4,585 B | scalable icon | mark, vector |
| `addons/web/static/img/odoo_logo.svg` | 1,571 B | website configurator (light) | wordmark, outlined |
| `addons/web/static/img/odoo_logo_dark.svg` | 1,571 B | configurator (dark) | wordmark, inverse |
| `addons/web/static/img/odoo_logo_tiny.png` | 627 B | "Powered by" badge, 62×20 | wordmark, 62×20 |
| `addons/web/static/img/logo.png` | 2,901 B | portal footer, public pages (35 refs) | horizontal lockup |
| `addons/web/static/img/logo2.png` | 2,745 B | POS display, misc (2 refs) | horizontal lockup |
| `addons/web/static/img/logo_inverse_white_206px.png` | 8,208 B | inverse, 206 px | white wordmark |
| `addons/web/static/img/nologo.png` | — | **exclude** — intentional placeholder | — |
| `addons/point_of_sale/static/src/img/favicon.ico` | — | POS favicon | mark |
| `addons/point_of_sale/static/src/app/generic_components/odoo_logo/*` | — | POS component (js+xml), not a binary | `JS` rename optional |
| `addons/website_links/static/img/default_favicon.png` | — | generic link-preview icon | mark |
| `addons/account/static/src/img/Odoo_logo_O.svg` | — | QR letterhead stencil — **leave** | — |
| `setup/win32/static/pixmaps/odoo-icon.ico` | — | installer icon | `.ico` multi-size |
| `setup/win32/static/pixmaps/odoo-intro.bmp` | — | installer intro | BMP, 24-bit |
| `setup/win32/static/pixmaps/odoo-slogan.bmp` | — | installer header | BMP, 24-bit |

`addons/website/…/favicon` is **not** here and does not need to be: `website.favicon` is a
configurable `Binary` field with a Settings UI (`res_config_settings.py:93`,
`website_templates.xml:111` sets `x_icon`). Website and portal pages pick up the uploaded
favicon with no code change. Only the backend falls back to the static file.

Rasterisation is a build dependency that does not exist on this machine yet (`inkscape`,
`rsvg-convert`, `magick` all absent; `convert.exe` is the Windows filesystem utility). Node 22
is installed, so `sharp` covers all PNG/ICO output in one `npm i`. The wordmark's live Garamond
`<text>` nodes — plus one empty `<text>` node and Inkscape/Sodipodi metadata — must be outlined
first; `opentype.js` reads the glyph paths directly. None of that needs a rasteriser.

---

## Register totals

| Surface | Files touched | In-place edits (`EDIT`/`DATA`) | Additive items | Est. hours |
|---|---|---|---|---|
| 1 Backend shell + dbase manager | 1 view + 1 qweb html | 4 lines (qweb html) | 7 inheritances | 3 |
| 2 Login | 0 | 0 | 0 | 0 |
| 3 PDF reports | 1 view | 0 | 2 inheritances | 1 |
| 4 Email | 10 | 0 data records | 11 inheritances + 2 Owl | 4 |
| 5 Windows installer | 1 `.nsi` + 3 binaries | **89 lines / 114 occurrences** | 0 | 5 |
| 6 PWA / offline / icons | 1 `.py` + 16 binaries (13 true, 3 SVG) | 2 lines | 0 | 3 |
| `release.py` | 1 | 1 line (`description`) | 0 | 0.1 |
| User menu (JS) | 1 | 0 | 1 registry patch | 1 |
| **Total** | **37 deduplicated** (table below; the per-surface counts above overlap — `odoo-icon-192x192.png` is counted in both S1 and S6) | **94 lines** in scope here (+9 in `package.py`/`License.rtf` = **103**) | **23 additive overrides** (not the whole addon tree — see below) | **≈17 h for the register items only** |

Three different totals appear in this document and they measure three different things. **37**
is this register's *coverage* count — every path the rebrand reasons about, additive and
inherited included. **25** is the *diff budget* — the paths git actually reports as modified
(16 replaced artefacts + 8 edited upstream paths + 1 conditional). **103** is edited lines,
not diff lines. None of the three is a count of the other two, and none is to be hand-maintained:
they are rendered from `castadoo/change_manifest.toml`.

The **23 additive overrides** in the table above are the ones that *carry a brand string* —
QWeb inheritances, Owl template overrides, one JS registry patch. The full additive surface of
the plan is **38 files**, because the addon tree also needs manifests, `__init__.py` files, the
seeded config parameter, the CI workflow and the asset tooling, none of which touches a brand
string and none of which this register enumerates.

The **≈17 h** figure prices the register's own 47 items and nothing else. It excludes asset
design, this register, the CI gates, the deployment checklist, the `docs/` deliverables, and
all deployment work. Surface 5 adds the `setup.nsi` work plus a build-and-test capability;
D7-B adds `hooks.py`, the explicit `-i` for a new overlay, and the rollout verification step.
Read it as a floor, not an estimate of the project.

Under D1-C the 7 `mail.template` bodies are excluded, so the email row drops to the 10 files
that carry inheritable views and Owl templates (8 view files, 2 POS Owl files), and the
in-place edit count falls by 7 records. Deduplicated file count:

| Group | Files |
|---|---|
| web views / HTML (S1, S3) | 3 |
| email (S4a + S4c) | 10 |
| installer (`setup.nsi`, `package.py`, `License.rtf`, 3 pixmaps) | 6 |
| PWA + release + user menu | 3 |
| `addons/web/static/img` replacements (8 binary + 3 SVG) | 11 |
| `point_of_sale` favicon + `website_links` favicon | 2 |
| optional POS component (js + xml) | 2 |
| **Total** | **37** (35 required + 2 optional) |

`nologo.png` (a deliberate placeholder), `account/…/Odoo_logo_O.svg` (a QR stencil) and the 7
excluded data bodies are explicitly out.

The estimate excludes asset design, the change register itself, the CI gates, and any
deployment work. It assumes the filenames above are kept.

**Conflict surface, ranked.** `setup.nsi`'s 89 `Odoo` lines are ~86% of the in-place edit
volume by count, but it is a leaf file that upstream touches once or twice a year.
`webmanifest.py` is 2 lines
and upstream touches it most years — that is a higher conflict *rate* per line. `report_templates.xml`
and `webclient_templates.xml` are touched at nearly every point release, but are reached by
inheritance, so their churn costs nothing. Ranking by count would put the effort in the wrong
place; ranking by churn-per-edit says the two `webmanifest.py` lines are the most expensive
lines in the register.

---

## What this register does not include

The 1,343 grep hits resolve to these surfaces once the register is applied:

| Excluded class | Hits | Why excluded |
|---|---|---|
| Python help text, `UserError` messages, docstrings | 543 | not in the six named surfaces; needs a per-message reading to separate brand from identifier |
| Owl component strings, tours, error dialogs | 330 | same |
| XML views: `help=`, field labels, digest tips, website snippets, `mass_mailing` themes | ~280 | same |
| Module summaries/authors in `ir_module_module.xml` | 23 | author field is attribution and stays; summaries are store copy |
| `.po` / `.pot` | 19,459 files | out of scope by decision; `Odoo` persists in all non-English locales |
| Docs (`.md`/`.rst`) | 1,091 | not rendered in product |
| Demo and test fixtures | 627 | never shipped to a customer database |

Pricing those is what makes the second scope option ("everything a user can read") expensive:
roughly 1,150 additional strings, each of which needs a judgement call on whether `Odoo` there
means *this product* or *the software this is based on*. That judgement cannot be automated, and
getting it wrong is a trademark statement, not a typo.

The register deliberately encodes the conservative reading: a string is in scope only if the
customer sees it on one of the six surfaces *and* it is unambiguously the product's own name.

### One item outside the six surfaces: `.gitattributes`

The register's binary inventory flags 13 replacement blobs as conflict-prone, and the design
mandates a `merge=ours` rule over them. Upstream 17.0 has **no `.gitattributes` file at all**
(measured: `git cat-file -p e57daa52:.gitattributes` → "path does not exist"), so creating one
is an addition, not an edit, and it carries no `Odoo` string — which is why it appears in no
surface table. It is still a file the plan must create, or the mitigation the design describes
three times never exists:

| Path | Content | Mechanism |
|---|---|---|
| `.gitattributes` (repo root) | `merge=ours` for `addons/web/static/img/*.png`, `*.ico`, `*.jpg` and `setup/win32/static/pixmaps/*.ico`, `*.bmp` | `CREATE` |

It is item **1b** in the design's plan. The three SVGs are excluded by design — they are text,
git merges them line by line, and `merge=ours` there would silently discard upstream edits
inside the file.

---

## Decision sheet

Tick one per row; rows 1 and 2 are the ones that gate the rest.

**D1 — Scope**
- [x] **C. Six surfaces minus the 7 `mail.template` bodies — 37 files, 103 edited lines, ~17 h. CHOSEN.**
- [ ] A. Six surfaces including the 7 `mail.template` bodies (43 files, 101 lines, ~19 h)
- [ ] B. C + help/error text (≈+1,150 strings, unbounded)
- [ ] D. Installer surface only (Surface 5); ship the web rebrand later

**D2 — Sync model**
- [x] **Merge `--no-ff` into the overlay branch. CHOSEN.** Stable SHAs, never force-pushes,
      conflicts resolved once per merge, one merge commit per point release to carry the
      LGPL modification date.
- [ ] Rebase + immutable tags `castadoo-17.0.<upstream>-r<n>` (cleaner graph, all SHAs rewrite)
- [ ] Patch series replayed onto a signed upstream tag at build time

**D3 — Phone-home**
- [ ] Disable `publisher_warranty_url` by default, commented (1 line)
- [ ] Leave stock

**D4 — Backend colour**
- [x] **Leave Odoo purple. CHOSEN — rejected on scope, not mechanism.** `!default` at
      `primary_variables.scss:73` does not block a plain assignment in a later-loaded file,
      so a new SCSS file in a branding module's asset bundle would work; the backend palette
      is not one of the six surfaces and the dependency cost exceeds the gain.
- [ ] Retheme to `#303188` via a new asset-bundle file (mechanism 2, no upstream edit)

**D4b — Surface 5 (Windows installer)**
- [x] **In scope — keep the fork. CHOSEN.** `setup.nsi` cannot be reached from `addons_path`;
      it is the only justification for a fork at all.
- [ ] Out of scope — the correct artefact becomes a separate addon repository plus a patch
      file, and the branch model, sync procedure and Alternatives A–F no longer apply

**D5 — Wordmark font**
- [ ] Convert with installed Garamond (`GARA.TTF`), matching the current design exactly
- [ ] Rebuild on EB Garamond (OFL), small shape change, no embedding question

**D6 — Installer publisher**
- [ ] `CASTASOFT` in `PUBLISHER`, LGPL notice in `COPYRIGHT`/`NOTICE`
- [ ] Leave `Odoo S.A.`

**D7 — Overlay activation**
- [ ] A. Explicit install list in the runbook (no code; a human omission fails silently)
- [x] **B. `post_init_hook` on `castadoo_branding`. CHOSEN.** Runs on first install only —
      `loading.py:178` sets `new_install = package.state == 'to install'`, and the call at
      `:243–247` is gated on it, so **`-u` does not re-run the hook**. Covers the migration
      case (target already installed) via `button_install()`; an overlay *added* later needs
      one explicit `-i castadoo_branding_<new>` in that release.
- [ ] C. Base addon declares all overlays as `depends` (guaranteed, but drags every business
      module onto every database)
