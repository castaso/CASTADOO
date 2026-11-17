# Part of CASTADOO. See LICENSE file for full copyright and licensing details.
# Derived from Odoo 17.0 (https://www.odoo.com), LGPL-3.

{
    'name': "CASTADOO Branding: eLearning",
    'summary': "Rebrands the channel-invitation email footer.",
    'category': 'Hidden/Tools',
    'version': '17.0.1.0.0',
    'author': "CASTASOFT, Odoo S.A.",
    'website': "https://castasoft.yukreasi.id",
    'license': 'LGPL-3',
    'depends': ['castadoo_branding', 'website_slides'],
    'auto_install': ['website_slides'],
    'data': [
        'views/website_slides_templates.xml',
    ],
}
