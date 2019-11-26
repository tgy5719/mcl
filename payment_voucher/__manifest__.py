# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Payment Voucher',
    'version': '0.2',
    'description': """This module consists Payment Voucher template""",
    'category': 'Localization',
    'author': 'Prixgen Tech Solutions Pvt Ltd.',
    'company': 'Prixgen Tech Solutions Pvt Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': ['account','account_accountant','invoice_multi_payment'],
    'data': [
        'views/payment_voucher_rep.xml',
        'views/payment_amount.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}