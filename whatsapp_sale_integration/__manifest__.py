# -*- coding: utf-8 -*-
{
    'name': 'WhatsApp Sales Integration',
    'version': '12.0.1.0.3',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'license': 'OPL-1',
    'category': 'Tools',
    'summary': 'WhatsApp Odoo Sales Integration',
    'description': """
This module can be used to send Quotations/Sales Orders via WhatsApp
--------------------------------------------------------------------

Send Quotations/Sales Orders via WhatsApp
""",
    'depends': ['base', 'sale', 'whatsapp_integration'],
    'data': [
        'views/sale_order_form_wa_inherited.xml',
    ],
    'external_dependencies': {'python': ['phonenumbers', 'selenium']},
    'installable': True,
    'auto_install': False,
    'currency': 'EUR',
    'price': 50,
}
