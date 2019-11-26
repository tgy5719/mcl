# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'purchase template',
    'version': '1.2',
    'description': """ Purchase Report""",
    'category': 'Localization',
    'depends': ['purchase','l10n_in_purchase'],
    'data': [
        'views/report_purchase_order.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
