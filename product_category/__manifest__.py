# -*- coding: utf-8 -*-

{
    'name': "Product category",
    'summary': "Assigning the categories at the product master level",
    'description': """
        Feature introduced to differentiate between product, service, assets and charges. It has been given an option to configure accordingly at product master level and also helps while selecting the right combination at purchase and sales transaction.
    """,
    'version': '12.0',
    'author': 'Prixgen Tech Solutions Pvt Ltd.',
    'company': 'Prixgen Tech Solutions Pvt Ltd.',
    'website': 'https://www.prixgen.com',
    "category": "Invoicing,Products",
    'depends': ['product','purchase','sale','stock'],
    'images': ['static/description/Banner.png'],
    'data': [
        'views/products.xml',
        'views/purchase.xml',
        'views/sale.xml',
        'views/product_menu.xml',
        'views/asset_menu.xml',
        'views/service_menu.xml',
        'views/charge_menu.xml',
        ],
    'installable': True,
    'auto_install': False,
}
