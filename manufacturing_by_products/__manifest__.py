# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Custom Module for Manufacturing Order By Products',
    'version': '12.0.0.3',
    'category': 'Manufacturing',
    'description': """Development in progress.
    Developed by Deekshith H M
""",
    'depends': [
        'mrp',
    ],
    'data': [
    'views/mrp_production_views.xml',
    'views/product_template_views.xml'

    ],
    'installable': True,
    'auto_install': True,
    'license': 'OEEL-1',
}
