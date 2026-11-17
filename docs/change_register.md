# CASTADOO change register

> Generated from `castadoo/change_manifest.toml` by
> `castadoo/tools/render_manifest.py --render`. **Do not edit by hand.**

Mirror branch `17.0`, overlay `castadoo/17.0`, upstream series `17.0`.

## Upstream paths this fork modifies

| Path | Kind | Surface | Conflict | +/- |
|---|---|---|---|---|
| `.gitignore` | modify-text | meta | none | 13/0 |
| `README.md` | modify-text | docs | recurring | 50/27 |
| `CONTRIBUTING.md` | modify-text | docs | recurring | 41/0 |
| `odoo/release.py` | modify-text | S1 | anchor | 1/1 |
| `addons/web/controllers/webmanifest.py` | modify-text | S6 | recurring | 7/2 |
| `addons/web/static/src/public/database_manager.qweb.html` | modify-text | S1 | anchor | 10/3 |
| `setup/package.py` | modify-text | S5 | anchor | 1/1 |
| `setup/win32/setup.nsi` | modify-text | S5 | recurring | 92/49 |
| `setup/win32/static/doc/License.rtf` | modify-text | S5 | whole-file | 2/0 |
| `addons/web/static/img/odoo-icon.svg` | modify-asset | S1,S6 | whole-file | 46/156 (not budgeted) |
| `addons/web/static/img/odoo_logo.svg` | modify-asset | S1 | whole-file | 78/10 (not budgeted) |
| `addons/web/static/img/odoo_logo_dark.svg` | modify-asset | S1 | whole-file | 78/10 (not budgeted) |

## Configuration values (invisible to Gates 2 and 3)

| Key | Model | Supplied by | Overlay | Assertion |
|---|---|---|---|---|
| `web.web_app_name` | `ir.config_parameter` | module-data | castadoo_branding | manifest name == 'CASTADOO' |
| `email_secondary_color` | `res.company` | module-data | castadoo_branding_mail | == '#303188' on base.main_company |
| `res.company.name` | `res.company` | deployment | - | tab title reads the company name; unset falls back to 'CASTADOO' |
| `res.company.logo` | `res.company` | deployment | - | login card renders the uploaded logo |
| `website.favicon` | `website` | deployment | - | soft assertion only: the replaced /web/static/img/favicon.ico is the real fallback |

## Allowlist

| Path | Lines | Reason |
|---|---|---|
| `CONTRIBUTING.md` | 1,52,54 | upstream documentation |
| `README.md` | 3,12,33,37,44,46,56 | accurate product reference |
| `addons/web/controllers/webmanifest.py` | 2,48,56 | internal identifier |
| `addons/web/static/src/public/database_manager.qweb.html` | 102,109 | accurate recipient |
| `odoo/release.py` | 2,19,21 | internal identifier |
| `setup/package.py` | 2,50,54,78,83,257,269,270 | internal identifier |
| `setup/win32/setup.nsi` | 1,5,85,90,99,139,140,142,143,169,193,207,208,209,210,211,212,213,217,226,240,241,242,243,244,245,246,250,263,296,297,321,351,357,359,434,445,467,530,531,567,568,655,657,658,661,671,674,676,677,679,681,682,685,688,689,690,692,694,698,699,700,704,707,711,713,740,758 | internal identifier |
| `setup/win32/static/doc/License.rtf` | 22,32 | licence notice |
| `addons/auth_signup/data/mail_template_data.xml` | all | D1-C |
| `addons/portal/data/mail_template_data.xml` | all | D1-C |
| `addons/gamification/data/mail_template_data.xml` | all | D1-C |
| `addons/lunch/data/mail_template_data.xml` | all | D1-C |
| `addons/website_crm_partner_assign/data/mail_template_data.xml` | all | D1-C |
| `addons/website_profile/data/mail_template_data.xml` | all | D1-C |
| `docs/` | all | upstream-owned, not user-visible |

## Assertions

*   **Tier A** — `GET /web/manifest.webmanifest`: name == 'CASTADOO' and background_color == theme_color == '#303188' and every icons[].src returns 200
*   **Tier A** — `GET /web/login`: body contains CASTADOO and does not contain '>Odoo<'
*   **Tier A** — `GET /web/offline, .card button computed style`: background-color == rgb(48, 49, 136)
*   **Tier A** — `registry.category('user_menuitems')`: no 'odoo_account' key
*   **Tier A** — `MailCase render of mail_notification_layout, reset_password_email, digest_mail_main`: contains CASTADOO; contains no 'Powered by Odoo' and no 'Sent by Odoo'
*   **Tier A** — `ir.module.module where state='installed'`: castadoo_branding plus one overlay per installed target module (D7-B)
*   **Tier B** — `printed POS receipt`: reads 'Powered by CASTADOO'
*   **Tier B** — `Windows installer on a clean VM`: publisher reads CASTASOFT; Add/Remove key is 'CASTADOO 17.0'; service name is still odoo-server-17.0; uninstall removes the key
*   **Tier B** — `invoice PDF text and metadata`: no 'Odoo'; title metadata reads 'CASTADOO Report'
