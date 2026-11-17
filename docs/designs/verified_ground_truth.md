# Verified Ground Truth — Odoo 17.0 @ 9c58cae5

**Purpose:** Stage 9 checks the design's `file:line` citations. Stages 5–8 could not, because the clone had no working tree. A sparse checkout now exists at:

```
C:\Users\Yongky\AppData\Local\Temp\opencode\depth17
```

Read-only. Every path below is on disk and readable. Cite this tree, not memory.

**HEAD:** `9c58cae5d6e3cf91ac1cca7df39fb21f68ca6e15` (branch `17.0`)

---

## How this file was produced

Spot-checks run by the orchestrator against the checkout above, not reviewer assertions. Each line states the command's *result*, so a reviewer can re-run it. Where the design and the tree disagree, both are recorded.

---

## CONFIRMED — design claim matches the tree

| Design claim | Verified |
|---|---|
| `webmanifest.py:48` is `web.web_app_name` with `'Odoo'` fallback | **Exact.** Line 48: `web_app_name = request.env['ir.config_parameter'].sudo().get_param('web.web_app_name', 'Odoo')` |
| `webmanifest.py` `background_color` (54) and `theme_color` (55) are both `'#714B67'` | **Exact.** Both lines read `'#714B67'` |
| `webmanifest.py` icon paths at 60 and 89 | **Exact.** Line 60 `'/web/static/img/odoo-icon-%s.png' % size`; line 89–90 `return 'web/static/img/odoo-icon-192x192.png'` |
| `config.py:50` feeds the datadir from `release.product_name` + `release.author` | **Exact.** Line 50: `return func(appname=release.product_name, appauthor=release.author)` |
| `models.py:5103` skips `noupdate` records on update | **Exact.** Line 5103: `if not (update and d_noupdate):` guarding `to_update.append(data)` |
| `ir_module.py:420` defines `must_install` | **Exact.** Line 420 `def must_install(module):`, line 421 the dependency-state set, line 434 `self.search(auto_domain).filtered(must_install)` |
| `release.py` line 19 `product_name`, 20 `description`, 33 `author`, 15 `version_info`, 32 `url`, 37 `nt_service_name` | **Exact.** All six line numbers match. File is 37 lines. |
| `setup.nsi:87` is `DEFAULT_POSTGRESQL_PASSWORD` | **Exact.** Line 87: `!define DEFAULT_POSTGRESQL_PASSWORD 'openpgpwd'`. It is the only `openpgpwd` in the entire tree. |
| `setup.nsi:136–137` share one BMP for welcome and uninstall-welcome | **Exact.** Both lines reference `${PIXMAPS_PATH}\odoo-intro.bmp` |
| `digest_data.xml:398` = `Sent by`, `:436` = `Powered by` | **Exact.** Line 398 `Sent by <a href=...>`; line 436 `Powered by <a href=...>`. Both confirmed. |
| "35 references to `logo.png`" | **Confirmed** as 35 non-`i18n` lines (53 occurrences). 596 lines match tree-wide, all but 35 inside `i18n/`. |
| "2 references to `logo2.png`" | **Exact.** 2. |
| `hr_expense` carries `#9E588B` | **Exact.** `addons/hr_expense/data/mail_templates.xml:49`: `<p style="color:#9E588B;">Powered by <a ...>Odoo</a>.</p>` |
| Item 31 `addons/point_of_sale/static/src/img/favicon.ico` exists | **Yes.** Present. |
| Item 32 `addons/website_links/static/img/default_favicon.png` exists | **Yes.** Present at that exact path. |
| Item 33 `odoo-icon.ico`, `odoo-intro.bmp`, `odoo-slogan.bmp` exist | **Yes.** All three under `setup/win32/static/pixmaps/`. |
| Item 26 icons exist at `addons/web/static/img/` | **Yes.** `favicon.ico` 1150 B, `logo.png` 2901 B, `logo2.png` 2745 B, `logo_inverse_white_206px.png` 8208 B, `odoo-icon-192x192.png`, `odoo-icon-512x512.png`, `odoo-icon-ios.png`, `odoo-icon.svg` all present. |
| `nologo.png` exists and is a distinct placeholder | **Yes.** 3261 B, separate from `logo.png`. |

---

## CONTRADICTED — design claim does not match the tree

### X1. `setup.nsi` does not hold 94 lines, nor 87 strings, by any count I can reproduce

| Measure | Value |
|---|---|
| File length | **729 lines** (design implies 600; citation at 1255 says "87 strings") |
| Lines containing `Odoo` (case-sensitive, simple match) | **89** |
| Total `Odoo` substring occurrences | **114** |
| Lines containing `odoo` (any case) | **119** |
| `LangString` lines carrying `Odoo` | subset of the 89 |
| `LANG_FRENCH` lines | **31** |

The design says "87 such lines" (60), "87 lines of `setup.nsi`" (638), "87 strings" (1255), and "87 of 94 edit lines". **89 and 114 are the nearest real numbers, and neither is 87.** Stage 6 finding 6 already flagged that 87 is used as three different units; the tree shows none of the three resolves to 87 exactly. This needs a recounted, unit-labelled figure.

### X2. `!include` is already used six times — the NSIS collapse proposal is cheaper than Stage 5 estimated

`setup.nsi` lines 9–14 already `!include` six headers (`MUI2.nsh`, `FileFunc.nsh`, `WordFunc.nsh`, `LogicLib.nsh`, `Sections.nsh`, `x64.nsh`), and there are **33 `!define` lines**, of which **10 carry `Odoo`**:

```
44:  !define PUBLISHER 'Odoo S.A.'
74:  !define PRODUCT_NAME "Odoo"
80:  !define UNINSTALL_REGISTRY_KEY_SERVER "${UNINSTALL_BASE_REGISTRY_KEY}\Odoo Server ${VERSION}"
89:  !define DEFAULT_ODOO_DB_USERNAME 'odoo'
90:  !define DEFAULT_ODOO_DB_PASSWORD 'odoopwd'
134: !define MUI_ICON "${PIXMAPS_PATH}\odoo-icon.ico"
136: !define MUI_WELCOMEFINISHPAGE_BITMAP "${PIXMAPS_PATH}\odoo-intro.bmp"
137: !define MUI_UNWELCOMEFINISHPAGE_BITMAP "${PIXMAPS_PATH}\odoo-intro.bmp"
139: !define MUI_HEADERIMAGE_BITMAP "${PIXMAPS_PATH}\odoo-slogan.bmp"
160: !define MUI_FINISHPAGE_LINK_LOCATION "https://www.odoo.com/page/contactus"
```

Stage 5's M11 (`!include` / `!define /redef` could collapse the conflict lines) is **confirmed and understated**: the file already demonstrates the idiom at lines 9–14, and only inline `LangString`/`Name`/`Caption` literals would remain in-place. Note lines 134–139 are pixmap *paths*, not strings — they resolve to files, so they need no edit at all if item 33 preserves filenames.

### X3. Item 32's "Default link-preview icon" framing is unsupported by the module

`addons/website_links/static/img/default_favicon.png` exists, but **no file in `website_links` references it**. `git grep -i "favicon"` across the module returns only `i18n/*.po` `msgid "Icon"` hits. `website_links_template.xml` contains no favicon or logo reference. The file may well be used by a controller outside the module or by `website`'s link-preview path — but the design's justification ("Link Tracker preview icon") is not established by the module it names, and Stage 6 already noted `website_links` is not one of the six named surfaces.

**Action for reviewer:** determine whether the file is dead, or referenced from outside `website_links`. Do not accept the design's stated scope without an actual reference.

### X4. `author` is `'OpenERP S.A.'`, not `'Odoo S.A.'`

`release.py:33` reads `author = 'OpenERP S.A.'`.

The requirement (user-confirmed) is that the Module author field `Odoo S.A.` stays unchanged for LGPL attribution. **The field does not currently say `Odoo S.A.`** — it says `OpenERP S.A.`, the corporate predecessor. Item 35 freezes `author` at line 33, which is correct behaviour, but the design's rationale ("`author` is LGPL attribution") describes a value the tree does not contain. Any reviewer checking the claim against source will report a mismatch. The design should say `OpenERP S.A.`, or explain why the legacy value is the attribution it wants to preserve.

### X5. `License.rtf` carries 2 `Odoo` occurrences, and 0 `OpenERP`

The design lists item 40 (`License.rtf`, 1 line). The file is at `setup/win32/static/doc/License.rtf` (design's path omits `static/doc/`) and contains **2** occurrences of `Odoo`. A 1-line edit is plausible if both are on one line, but the count and the path both need correction.

### X6. The `Powered by Odoo` corpus is far larger than the design's ten-to-thirteen site table

`git grep -l "Powered by Odoo" HEAD` returns **52 files**. The design's scope is `~10` sites in the table at 430–440 (which itself lists 13 IDs). The 52 includes `demo/` files, `crm/data/mail_template_demo.xml`, `mass_mailing*/demo/`, and `im_livechat`. Some are demo data and arguably out of scope — but **the design never states the exclusion rule**, and its own D1-C rationale ("seven records watched") reads very differently against 52 files than against 7.

Also: `addons/web/views/webclient_templates.xml:130` renders `Powered by <span>Odoo</span>` on the **login page** — a named surface — and `:100` defines `final_message` as `Powered by %s%s`. That is runtime-assembled, which the design concedes Gate 2 cannot see.

### X7. `Sent by` appears in 180 files, not the 398/436 line pair the design implies

`digest_data.xml` line 398 and 436 match exactly. But `git grep -l "Sent by"` returns **180 files**, overwhelmingly `i18n/*.po` `msgid "Sent by"` entries. The design's decision to treat `Sent by` as a single site inside `digest` is defensible for the data file, but the document should say the 180 is `.po` and therefore covered by the D1-`.po` deferral — otherwise a fresh reader cannot reconcile 1 site with 180 files.

---

## What Stage 9 should do with this file

- **Treat CONFIRMED rows as settled.** Do not spend findings re-deriving them.
- **Treat X1–X7 as the citation-defect set** and verify each independently, adding anything I missed. X1 and X6 are the two that change the design's argument, not just its numbers.
- **Every other `file:line` in the design that is not in either table is unverified** — check it in the tree and report it. That is the core of this stage.
- The sparse checkout contains only the paths cited. If you need a path that is missing, report the missing path as a finding rather than guessing — I can widen the checkout.

---

## Checkout coverage

On disk and readable:

```
setup/                     (win32/setup.nsi, win32/static/doc/License.rtf, win32/static/pixmaps/, package.py, odoo.conf samples)
odoo/release.py
odoo/tools/config.py
odoo/models.py
odoo/addons/base/models/ir_module.py
addons/web/controllers/
addons/web/static/src/public/
addons/web/views/
addons/web/static/img/
addons/mail/data/
addons/portal/
addons/auth_signup/
addons/gamification/data/
addons/lunch/data/
addons/hr_expense/
addons/website_crm_partner_assign/
addons/website_profile/
addons/website_links/
addons/website_slides/data/
addons/digest/
addons/point_of_sale/static/src/
addons/website/views/
addons/im_livechat/
```

Not on disk (widening the sparse checkout is possible if a finding needs one): `i18n/` trees for most modules, `addons/website/static/`, unrelated business modules.
