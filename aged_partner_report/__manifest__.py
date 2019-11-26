# -*- coding: utf-8 -*-


{
    'name': 'Aged Partner Report',
    'version': '12.0.0',
    'category': 'Project',
    'summary': 'Aged Partner Report caliculate depends on the Due dates',
    'description': """
		This module caliculate Aged Partner Report.
    				""",
    'author': "Prixgen tech Solutions",
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/aged_partner_report_view.xml',
        'wizard/aged_partner_wizard_view.xml',
    ],

    'installable': True,
    'auto_install': False
}
