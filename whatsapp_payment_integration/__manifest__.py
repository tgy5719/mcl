# -*- coding: utf-8 -*-
{
    'name': 'WhatsApp Payments Integration',
    'version': '12.0.1.0.0',
    'category': 'Tools',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'license': 'OPL-1',
    'summary': 'WhatsApp/Payments Integration',
    'description': """
This module can be used to send Payment Receipts via WhatsApp
----------------------------------------------------------

Send Payment Receipts via WhatsApp
""",
    'depends': ['base', 'account', 'whatsapp_integration'],
    'data': [
        'views/account_payment_form_wa_inherited.xml',
    ],
    'external_dependencies': {'python': ['phonenumbers', 'selenium']},
    'installable': True,
    'auto_install': False,
    'currency': 'EUR',
    'price': 50,
}
