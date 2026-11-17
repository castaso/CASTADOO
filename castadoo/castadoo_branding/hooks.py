# Part of CASTADOO. See LICENSE file for full copyright and licensing details.
#
# D7-B: a post_init_hook that marks the per-module overlays for install.
#
# Why a hook rather than relying on auto_install alone: auto_install fires when
# the target module is being installed in the same transaction. A database that
# already had `mail` before `castadoo_branding` existed never re-evaluates that,
# so without this the mail footer stays unbranded on every migrated database.

import logging

_logger = logging.getLogger(__name__)

# Target module -> overlay that brands it. Kept here rather than duplicated
# across nine manifests, because this table is what covers the migration case:
# a target already installed before castadoo_branding was added.
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
    """Mark an overlay for install wherever its target is already installed.

    Runs once, on first install of this addon. Not on ``-u``: the loader gates
    the call on ``new_install`` (odoo/modules/loading.py:178, and the guarded
    call at :243-247). Adding an overlay for an already-installed target in a
    later release therefore needs one explicit
    ``-i castadoo_branding_<new>`` in that release's deployment step.
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
            # The overlay is absent from addons_path. Report and continue:
            # raising here would make this addon uninstallable on a deployment
            # that ships the base tier without that particular overlay, and a
            # missing overlay is a deployment defect the rollout check surfaces.
            _logger.warning(
                "castadoo_branding: %s is installed but %s was not found on "
                "addons_path; that surface will stay unbranded.",
                target, overlay)
            continue
        to_install |= overlay_module
        _logger.info(
            "castadoo_branding: marking %s for install (%s present)",
            overlay, target)

    if to_install:
        # button_install(), not button_immediate_install(): the immediate
        # variant raises UserError while the registry is initialising
        # (odoo/addons/base/models/ir_module.py:590) and RuntimeError outright
        # inside tests (:594). button_install only marks the modules
        # 'to install'; the loader's STEP 3 loop re-queries that state and
        # loads them (odoo/modules/loading.py:479-487).
        to_install.button_install()
