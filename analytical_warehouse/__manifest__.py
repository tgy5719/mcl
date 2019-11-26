# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
# Copyright (c) 2016  - Osis - www.osis-dz.net

{
    'name': 'Analytical and warehouse custom fields',
    'version': '12.0.0.5',
    'category': 'Stock',
    'description': """This is the module for analytical and warehouse custom fields.""",
    'author': 'Prixgen Tech Solutions Pvt Ltd.',
    'company': 'Prixgen Tech Solutions Pvt Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': ['base','account','stock','sale','sale_stock'],
    'data': [
        'views/account_analytic_account_views.xml',
        'views/account_invoice_views.xml',
        'views/sale_order_views.xml',
        'views/stock_warehouse_views.xml'

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
