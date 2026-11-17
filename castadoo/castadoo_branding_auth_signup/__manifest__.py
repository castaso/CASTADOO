# Part of CASTADOO. See LICENSE file for full copyright and licensing details.
# Derived from Odoo 17.0 (https://www.odoo.com), LGPL-3.

{
    'name': "CASTADOO Branding: Signup",
    'summary': "Rebrands the password-reset and new-device alert emails.",
    'category': 'Hidden/Tools',
    'version': '17.0.1.0.0',
    'author': "CASTASOFT, Odoo S.A.",
    'website': "https://castasoft.yukreasi.id",
    'license': 'LGPL-3',
    'depends': ['castadoo_branding', 'auth_signup'],
    'auto_install': ['auth_signup'],
    'data': [
        'views/auth_signup_templates_email.xml',
    ],
}
