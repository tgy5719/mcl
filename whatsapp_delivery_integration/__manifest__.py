# -*- coding: utf-8 -*-
{
    'name': 'WhatsApp Delivery Integration',
    'version': '12.0.2.0.0',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'https://www.prixgen.com',
    'license': 'OPL-1',
    'category': 'Tools',
    'summary': 'WhatsApp/Delivery Integration',
    'description': """
This module can be used to send Odoo Delivery Orders via WhatsApp
----------------------------------------------------------

Send Delivery Orders via WhatsApp
""",
    'depends': ['base', 'delivery', 'whatsapp_integration'],
    'data': [
        'views/stock_picking_form_wa_inherited.xml',
    ],
    'external_dependencies': {'python': ['phonenumbers', 'selenium']},
    'installable': True,
    'auto_install': False,
    'currency': 'EUR',
    'price': 50,
}
