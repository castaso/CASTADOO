# Part of CASTADOO. See LICENSE file for full copyright and licensing details.
# Derived from Odoo 17.0 (https://www.odoo.com), LGPL-3.

{
    'name': "CASTADOO Branding: Live Chat",
    'summary': "Rebrands the live-chat support page and its invitation email.",
    'category': 'Hidden/Tools',
    'version': '17.0.1.0.0',
    'author': "CASTASOFT, Odoo S.A.",
    'website': "https://castasoft.yukreasi.id",
    'license': 'LGPL-3',
    'depends': ['castadoo_branding', 'im_livechat'],
    'auto_install': ['im_livechat'],
    'data': [
        'views/im_livechat_templates.xml',
    ],
}
