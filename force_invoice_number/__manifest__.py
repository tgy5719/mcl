# -*- encoding: utf-8 -*-
{
    'name': 'Force Invoice Number',
    'version': '12.0.0.1',
    'category': 'Others',
    'summary': """Enter Invoice Number Manually""",
    'depends': ['base','account'],
    'description': """Enter the invoice nmber manually and update to all dependent tables""",
    'data': [
        'views/account_invoice_view.xml',
    ],
    'application': False,
}
