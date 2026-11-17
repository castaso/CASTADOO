# Part of CASTADOO. See LICENSE file for full copyright and licensing details.
# Derived from Odoo 17.0 (https://www.odoo.com), LGPL-3.

{
    'name': "CASTADOO Branding: Point of Sale",
    'summary': "Rebrands the printed receipt footer.",
    'category': 'Hidden/Tools',
    'version': '17.0.1.0.0',
    'author': "CASTASOFT, Odoo S.A.",
    'website': "https://castasoft.yukreasi.id",
    'license': 'LGPL-3',
    'depends': ['castadoo_branding', 'point_of_sale'],
    'auto_install': ['point_of_sale'],
    # point_of_sale declares assets_prod and assets_qunit_tests. There is NO
    # point_of_sale.assets key in 17.0 - naming one would produce a silent
    # no-op, which is the whole reason this is stated rather than assumed.
    #
    # Only the receipt is listed. The customer display was measured and needs no
    # template override: its footer is <span>Powered by </span> followed by the
    # wordmark of CSS class .pos-odoo_logo_container .logo, which is a
    # background-image of /web/static/img/logo_inverse_white_206px.png - a blob
    # replaced in place by item 29. There is no Odoo string in that template to
    # inherit. The OdooLogo component (generic_components/odoo_logo) is declared
    # in 17.0 but rendered by no template at all, so overriding it would change
    # nothing on screen.
    'assets': {
        'point_of_sale.assets_prod': [
            'castadoo_branding_pos/static/src/overrides/receipt.xml',
        ],
    },
}
