# Part of CASTADOO. See LICENSE file for full copyright and licensing details.
# Derived from Odoo 17.0 (https://www.odoo.com), LGPL-3.

{
    'name': "CASTADOO Branding",
    'summary': "Rebrands the web client, login, offline page, PDF metadata and "
               "notification footers for CASTADOO.",
    'description': """
CASTADOO Branding
=================

Base tier of the CASTADOO rebrand. This addon depends on ``web`` and nothing
else, deliberately: a base addon that depends on every module it touches drags
the whole dependency graph into every database.

What it does
------------
* replaces the browser tab title fallback and the ``theme-color`` meta value
* repoints the login footer at the CASTASOFT site
* rebrands the ``Powered by`` badge used on public pages
* rebrands the offline page and its call-to-action colour
* replaces the PDF ``<title>`` fallback in both report layouts
* seeds ``web.web_app_name`` so the PWA manifest is named CASTADOO on a fresh
  database

Per-module surfaces (email footers, portal sidebar, POS receipt) live in the
``castadoo_branding_<module>`` overlays, which auto-install with their target.

Colour: ``#303188`` (navy) and ``#FAA61A`` (orange), from the CASTASOFT mark.
The backend itself stays on the upstream palette; retheming it is out of scope.
    """,
    'category': 'Hidden/Tools',
    'version': '17.0.1.0.0',
    'author': "CASTASOFT, Odoo S.A.",
    'website': "https://castasoft.yukreasi.id",
    'license': 'LGPL-3',
    'depends': ['web'],
    'auto_install': False,
    'application': False,
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
}
