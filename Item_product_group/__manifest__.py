# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Products categories & groups',
    'version': '1.2',
    'category': 'Products',
    'author': 'Prixgen Tech Solutions Pvt Ltd.',
    'company': 'Prixgen Tech Solutions Pvt Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': ['base', 'purchase','product'],
    'description': """ Item category and product group code"""
,
    'data': [
        'views/item_category_view.xml',
        'views/product_category_secondary_view.xml',
        'views/product_group_primary_view.xml',
        'views/item_view.xml',
        
    ],
    
    'installable': True,
    'auto_install': False,
}
