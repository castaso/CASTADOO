/* Part of CASTADOO. See LICENSE file for full copyright and licensing details.
 *
 * Patches the backend user-menu registry so no entry leads to Odoo's account
 * service. Loaded through web.assets_backend by castadoo_branding's manifest.
 *
 * Two distinct problems, two different answers:
 *
 *   odoo_account — removed. The entry's description is "My Odoo.com account"
 *   and its callback calls /web/session/account, falling back to
 *   https://accounts.odoo.com/account. Both routes lead to Odoo's own account
 *   service, which a CASTASOFT customer has no account on. Renaming it while
 *   leaving the URL would be worse than removing it.
 *
 *   documentation — kept, pointing where it points. This is the one place
 *   where the Odoo name is accurate rather than a leak: that URL documents the
 *   software this fork actually is, so a customer following it gets correct
 *   answers. Repointing at a CASTASOFT copy that does not exist would ship a
 *   broken menu. It carries a Gate 3b allowlist reason of "upstream
 *   documentation". If a CASTASOFT-hosted mirror ever exists, this is the line
 *   to change (user_menu_items.js:12 in upstream).
 */

import { registry } from "@web/core/registry";

const userMenuRegistry = registry.category("user_menuitems");

// remove() throws nothing and no-ops if the key is absent, so this is safe on a
// tree where upstream has already dropped the entry.
if (userMenuRegistry.contains("odoo_account")) {
    userMenuRegistry.remove("odoo_account");
}
