
{
    'name': 'Currency Inverse Rate',
    'version': '12.0.0.0.0',
    'category': 'Accounting',
    'sequence': 14,
    'author': 'Prixgen Tech Solutions Pvt Ltd.',
    'company': 'Prixgen Tech Solutions Pvt Ltd.',
    'website': 'https://www.prixgen.com',
    'license': 'AGPL-3',
    'summary': '',
    'description': '''
Currency Inverse Rate
==========================
In some countries where currency rate is big enough compared to USD or EUR, 
we are used to see exchange rate in the inverse way as Odoo shows it. 

The module shows rate FROM base currency and not TO base currency. For eg.

* Base Currency IDR: 1.0
* USD rate: 12,000 (in Odoo way: 1 / 12,000 = 0.000083333333333)

Using this module, we enter the 12,000 and not the 0.000083333333333.

This module also add number of decimal precision on the currency rate
to avoid rounding for those currencies.

    ''',
    'depends': [
        'base',
    ],
    'external_dependencies': {
    },
    'data': [
        'views/res_currency_view.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
