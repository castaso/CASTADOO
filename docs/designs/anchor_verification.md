# Anchor & Citation Verification — Orchestrator Run

**Why this file exists:** Stage 9 reviewers are sandboxed to the bundle directory and cannot read `C:\Users\Yongky\AppData\Local\Temp\opencode\depth17` (`permission.rejected: external_directory`). The implementation-readiness reviewer reported vector 5 (anchor correctness) as `[tree-blocked]`. The orchestrator ran those checks instead. Findings below are **measured**, not inferred.

**Tree:** Odoo 17.0 @ `9c58cae5d6e3cf91ac1cca7df39fb21f68ca6e15`. Sparse checkout, now widened to include `addons/web/static/src/core/` and `addons/web/static/src/webclient/`.

Supersedes and extends `verified_ground_truth.md` § CONTRADICTED.

---

## A1 — `inherit_id` naming: design adds a module prefix the tree does not have

**BLOCKER.** The design names parents `web.web_layout` and `web.webclient_offline`. The tree declares:

```
addons/web/views/webclient_templates.xml:17    <template id="web.layout" name="Web layout">
addons/web/views/webclient_templates.xml:285   <template id="webclient_offline">
addons/web/views/webclient_templates.xml:5     <template id="conditional_assets_tests">
addons/web/views/webclient_templates.xml:89    <template id="brand_promotion_message">
addons/web/views/webclient_templates.xml:103   <template id="brand_promotion">
addons/web/views/webclient_templates.xml:112   <template id="web.login_layout">
addons/web/views/webclient_templates.xml:247   <template id="web.webclient_bootstrap">
```

The declared `id` is a **local** id. Odoo qualifies it with the module name at load, so the fully-qualified external id is `web.layout` (module `web` + id `layout`) — **not** `web.web_layout`.

- Item 3 line 911 says `web.web_layout` → **wrong**, should be `web.layout`.
- Item 4 line 926 says `web.webclient_offline` → **wrong**, should be `web.webclient_offline`… which *is* right, because the local id is `webclient_offline` and the module is `web`. So the design is inconsistent, not uniformly wrong: it prefixes some and doubles the prefix on others.

Correct externally-qualified ids for every parent the design cites:

| Design says | Tree local id | Correct external id |
|---|---|---|
| `web.web_layout` (911) | `layout` at :17 | **`web.layout`** |
| `web.brand_promotion_message` (913) | `brand_promotion_message` at :89 | `web.brand_promotion_message` ✓ |
| `web.login_layout` (916) | `login_layout` at :112 | `web.login_layout` ✓ |
| `web.webclient_bootstrap` (918) | `webclient_bootstrap` at :247 | `web.webclient_bootstrap` ✓ |
| `web.webclient_offline` (926) | `webclient_offline` at :285 | `web.webclient_offline` ✓ |
| `web.report_layout` (944) | `report_layout` at :6 | `web.report_layout` ✓ |
| `web.report_preview_layout` (945) | `report_preview_layout` at :39 | `web.report_preview_layout` ✓ |
| `mail.mail_notification_layout` (997) | `mail_notification_layout` at :4 | `mail.mail_notification_layout` ✓ |
| `mail.mail_notification_light` (1004) | `mail_notification_light` at :114 | `mail.mail_notification_light` ✓ |
| `point_of_sale.OrderReceipt` (item 23) | `OrderReceipt` at :3 | `point_of_sale.OrderReceipt` ✓ |

**One wrong id out of ten.** It is still a Blocker because a wrong `inherit_id` is a hard install failure (`External ID not found`), and because the register (`change_register.md` S1.01) already says `web.layout` — so the design and the register disagree, and Gate 1's allowlist is the register.

---

## A2 — The `<title>` fallback does not control the browser tab on a branded deployment

**MAJOR.** `webclient_templates.xml:22`:

```xml
<title t-esc="title or 'Odoo'"/>
```

`t-esc` fallback fires only when `title` is falsy. Most `/web` routes set `title` from data. So:
- Replacing `'Odoo'` with `'CASTADOO'` (item 3, line 911) is **correct and worth doing** — it fixes the empty-title case.
- The assertion at line 1386 ("tab reads CASTADOO") is **wrong as written**: on a deployment whose company is named anything else, the tab reads the company name and the assertion fails.

Verified: `webclient_offline` at :288 sets `<t t-set="title">Offline</t>`, and the test templates at :218/:233 set their own titles — confirming `title` is normally data-driven, not fallback-driven.

---

## A3 — The digest colour machinery is in a different template from the one cited

**MAJOR.** `digest_data.xml` declares four templates:

```
:5    digest_mail_layout
:270  digest_mail_main
:452  digest_section_mobile
:498  digest_tool_kpi
```

`color_company` is set at **line 14**, which is inside `digest_mail_layout` (5–269), and applied at **line 147** (`.odoo_link_text`) and lines 58/87 (button backgrounds) — **all four inside `digest_mail_layout`**, not inside `digest_mail_main` (270–452).

Item 19 (line 1081) says `digest.digest_mail_main` "spans lines 270–447" and then cites lines 14 and 147. **The cited template range and the cited lines are in different templates.** Also 270–447 is wrong: `digest_mail_main` runs to 451 (next template starts at 452).

Consequence for the design's argument: item 19's claim that the digest needs "zero edits" because the colour is data-driven is **correct in substance** — `<t t-set="color_company" t-value="company.email_secondary_color or '#714B67'"/>` genuinely makes `email_secondary_color` drive it. But the anchors are misattributed, and an implementer following the citation would inherit the wrong template.

Note line 14 has a **third** hardcoded purple `#714B67` as the fallback — consistent with the design's four-purple finding.

---

## A4 — `Sent by` / `Powered by` in digest: confirmed exactly, and they are in the same template

**NIT (confirming design).** Both are inside `digest_mail_main`:
- `:398` — `Sent by <a href="https://www.odoo.com" target="_blank">`
- `:436` — `Powered by <a href="https://www.odoo.com" target="_blank" class="odoo_link">`

Both cited line numbers are **exact**. Stage 6's C1 reconciliation (two footers, two colours) is confirmed against source.

Because both are in one template with two distinct structures, the design's "two records, two anchors" claim is correct in principle — but the design supplies **neither anchor expression** (item 19, lines 1081–1098). An implementer must invent both.

---

## A5 — Item 9's parent ids and footer lines: exact

**Confirmed.** `mail_templates_email_layouts.xml`:
- `:4` `mail_notification_layout`, footer at `:103–109` (`Powered by` at 104, `Odoo` at 105, `t-att-style` reading `company.email_secondary_color or '#875A7B'` at 105).
- `:114` `mail_notification_light`, footer at `:177–183`.

Design's cites at 997–1005 are **accurate**. The `t-att-style` expression is confirmed present, so the design's instruction to leave it intact and set the field instead is sound.

---

## A6 — Item 11 spans two templates: design's "single inheritance edit" is impossible

**MAJOR.** `auth_signup_templates_email.xml`:
- `:3` `reset_password_email` — `#875A7B` button at **:36**, `Powered by` at **:81**.
- `:88` `alert_login_new_device` — `#875A7B` button at **:122**, `Powered by` at **:143**.

Design (1016–1026) says "two templates at lines 36, 81 and 122, 143; those are inside the same template region, so replacing all four occurrences is a single inheritance edit rather than two."

**Four occurrences across two separate templates.** A single `<xpath>` cannot cover both. It needs at minimum two records (two `inherit_id`), and realistically four (button + footer in each). The design also supplies no anchor expressions.

Also note `auth_signup/data/mail_template_data.xml` is `<data noupdate="1">` at line 3, containing `set_password_email` (:5), `mail_template_data_unregistered_users` (:101), `mail_template_user_signup_account_created` (:153) — confirming the `noupdate` premise that D1-C rests on.

---

## A7 — Item 17's two nodes in one template: confirmed

**MAJOR (as flagged).** `hr_expense/data/mail_templates.xml`:
- `:11` `hr_expense_template_register`, `#9E588B` button at `:31`
- `:35` `hr_expense_template_register_no_user`, `<p style="color:#9E588B;">Powered by ...Odoo</p>` at `:49`

Item 17 claims **one** inherited record on `hr_expense_template_register_no_user` but then requires the button at line 31 replaced too — and line 31 is in a **different template**. Same defect shape as A6.

`#9E588B` at :49 confirmed exactly, including the trailing period after the link.

---

## A8 — POS parents: both exist, and item 24's parent is identifiable

**Confirmed, with a gap.** `order_receipt.xml:3` → `t-name="point_of_sale.OrderReceipt"`, `Powered by Odoo` at `:140`. Item 23's parent and line are exact.

`customer_display_template.xml` has six `t-name` declarations. Line 84 (`<span>Powered by </span>`) sits inside the template declared at `:43`:

```
:4    point_of_sale.CustomerFacingDisplayHead
:30   point_of_sale.CustomerFacingDisplayNoOrder
:43   point_of_sale.CustomerFacingDisplayOrder   <-- line 84 is inside this one
:91   point_of_sale.CustomerFacingDisplayMainContainer
:106  point_of_sale.CustomerFacingDisplayOrderLines
:170  point_of_sale.CustomerFacingDisplayPaymentLines
```

Item 24 names the file and line 84 but **never states the parent `t-name`**. Since line 84 is inside `CustomerFacingDisplayOrder`, the correct parent is `point_of_sale.CustomerFacingDisplayOrder`. A wrong `t-inherit` is silent — the design says so itself at 1129–1131.

---

## A9 — `Registry.remove` exists; the design's `?` is unnecessary

**Blocker resolved — write the real call.** `addons/web/static/src/core/registry.js`:

```
:50   add(key, value, { force, sequence } = {}) {
:118  * Remove an item from the registry
:122  remove(key) {
:124      delete this.content[key];
```

`remove(key)` **exists in 17.0**. The design's `registry.category("user_menuitems").remove?` (line 965) can be replaced with the concrete call.

`user_menu_items.js` (129 lines) confirmed:
- `:12` `documentationURL = "https://www.odoo.com/documentation/17.0"` — exact.
- `:91` `id: "account"`, `:92` `description: _t("My Odoo.com account")` — **the id is `account`, not `odoo_account`**; `odoo_account` is the *registry key* used at `:128` `.add("odoo_account", odooAccountItem)`.
- `:100` `browser.open("https://accounts.odoo.com/account", "_blank")` — exact.

So the item must distinguish the **registry key** (`odoo_account`) from the **item id** (`account`). The design (954 vs 958) conflates them: `.remove("odoo_account")` removes by registry key, which is correct — but the design's prose calls `odoo_account` "the item's id". Write it as: `registry.category("user_menuitems").remove("odoo_account")`.

---

## A10 — `database_manager.qweb.html`: all four strings exact

**Confirmed.** 296 lines total.
- `:4` `<title>Odoo</title>`
- `:33` `Warning, your Odoo database manager is not protected.<br/>`
- `:102` `To enhance your experience, some data may be sent to Odoo online services. See our <a href="https://www.odoo.com/privacy" ...>Privacy Policy</a>.`
- `:144` `In order to avoid conflicts between databases, Odoo needs to know if this database was moved or copied.<br/>`

All four line numbers in item 36 (1234–1236) are **exact**. The design's privacy-link dilemma at 1238–1241 is real: the string genuinely describes data sent to Odoo's servers.

---

## A11 — `package.py`: 9 case-sensitive `Odoo` lines, not 8

**MAJOR.** Item 39 claims "8 occurrences, of which two must not change". Measured (`-CaseSensitive 'Odoo'`): **9 lines**.

```
  2  # Part of Odoo. See LICENSE file...
 50  class OdooTestTimeoutError(Exception):
 54  class OdooTestError(Exception):
 78  raise OdooTestError("Installation of package failed")
 83  raise OdooTestError("Package test: FAILED. Not able to install base.")
257  logging.info('Starting to test Odoo install test')
269  raise OdooTestTimeoutError('Odoo pid file never appeared after %s sec' % INSTALL_TIMEOUT)
270  raise OdooTestError('Error while installing/starting Odoo after %s sec.\nSee testlogs.txt in build dir' % ...)
323  changelog = fr"odoo ({VERSION}.{TSTAMP}) stable; urgency=low\n\n  * {VERSION}\n\n -- Odoo Bot <info@odoo.com>  {TFULL}\n"
```

Not to change: :2 (licence header), :50, :54, :78, :83, :269, :270 (exception class names and messages — internal identifiers, not user-visible), :257 is a log line. Only **:323** (`Odoo Bot <info@odoo.com>` in the Debian changelog) is genuinely user-visible.

The design's `8 occurrences, two must not change` is wrong on both numbers. Real split: **9 lines, 1 genuinely user-visible**, the rest internal identifiers. Also `ruff.toml` **does** exist at repo root (confirmed) — so the design's ruff claim is right.

---

## A12 — `odoo_logo.svg` and `odoo_logo_dark.svg` are different files

**NIT resolved.** Register cited "1,571 B each" for a light/dark pair, which looked suspicious. Measured: both are 1,581 bytes but **SHA256 differs** — genuinely distinct files, identical size by coincidence. Item 30's two files exist and are distinct. `odoo_logo_tiny.png` exists at 627 B.

---

## A13 — `README.md` exists, `odoo.conf` does not (at root)

**MAJOR for item 42.** Root listing confirms `README.md`, `CONTRIBUTING.md`, `LICENSE`, `COPYRIGHT`, `SECURITY.md`, `ruff.toml`, `setup.cfg`. **No `odoo.conf` at root** — the only ones are `debian/odoo.conf` and `addons/point_of_sale/tools/posbox/configuration/odoo.conf`.

Item 42 (1313–1322) and placement decision (881–887) speak of "one `addons_path` entry in `odoo.conf`" as if editing an existing file. There is no such file to edit — it must be **created** (or the deployment config documented). That changes item 42 from a `Modify` of an upstream file to a `Create`, which also changes the 37/38 upstream-path arithmetic.

---

## Summary of anchor defects, by severity

| # | Severity | Defect |
|---|---|---|
| A1 | Blocker | `web.web_layout` → must be `web.layout` (item 3) |
| A9 | Blocker → **resolved** | `Registry.remove` exists; write the concrete call; distinguish registry key from item id |
| A3 | Major | Item 19 cites `digest_mail_main` (270–447) but the lines are in `digest_mail_layout`; range is also 270–451 |
| A6 | Major | Item 11: four sites across **two** templates, called "a single inheritance edit" |
| A7 | Major | Item 17: two nodes in two templates, declared as one record |
| A8 | Major | Item 24: parent `t-name` never stated; it is `point_of_sale.CustomerFacingDisplayOrder` |
| A11 | Major | Item 39: 9 lines not 8; 1 user-visible not "two must not change" |
| A13 | Major | Item 42: no root `odoo.conf` exists — it is a Create, not a Modify |
| A2 | Major | `<title>` fallback does not drive the tab; the assertion at 1386 is wrong |
| A4 | Nit | Two digest footers confirmed, but neither anchor expression supplied |
| A5 | Clear | Item 9 exact — parents, footer lines, `t-att-style` all confirmed |
| A10 | Clear | Item 36 all four strings exact |
| A12 | Clear | Item 30's two SVGs distinct; `odoo_logo_tiny.png` present |

**Items whose anchors are fully correct:** 5 (both report templates), 9 (both mail layouts), 23 (POS receipt), 36 (all four db-manager strings), 3 (three of four records), 4 (both parents; the `<style>` dilemma is real).

**Items whose anchors are wrong or missing:** 3 (one parent), 11, 17, 19, 24, 30 (fine), 39, 42.
