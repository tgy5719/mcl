# -*- coding: utf-8 -*-
{
    'name': 'WhatsApp Invoicing Integration',
    'version': '12.0.1.0.0',
    'category': 'Tools',
    'author': 'Prixgen Tech Solutions Pvt Ltd.',
    'website': 'http://www.prixgen.com.com',
    'license': 'OPL-1',
    'summary': 'WhatsApp/Invoice Integration',
    'description': """
This module can be used to send Odoo Invoices via WhatsApp
----------------------------------------------------------

Send Customer Invoices, Vendor Bills via WhatsApp
""",
    'depends': ['base', 'account', 'whatsapp_integration'],
    'data': [
        'views/account_inovice_form_wa_inherited.xml',
    ],
    'external_dependencies': {'python': ['phonenumbers', 'selenium']},
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'currency': 'EUR',
    'price':'50',
    }
