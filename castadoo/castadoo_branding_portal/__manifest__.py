# Part of CASTADOO. See LICENSE file for full copyright and licensing details.
# Derived from Odoo 17.0 (https://www.odoo.com), LGPL-3.

{
    'name': "CASTADOO Branding: Portal",
    'summary': "Rebrands the portal sidebar badge.",
    'category': 'Hidden/Tools',
    'version': '17.0.1.0.0',
    'author': "CASTASOFT, Odoo S.A.",
    'website': "https://castasoft.yukreasi.id",
    'license': 'LGPL-3',
    'depends': ['castadoo_branding', 'portal'],
    'auto_install': ['portal'],
    'data': [
        'views/portal_templates.xml',
    ],
}
