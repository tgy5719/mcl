# -*- coding: utf-8 -*-


{
    'name': 'Sales Summary Report',
    'version': '12.0.0',
    'category': 'Sales',
    'summary': 'Sales Summary Report',
    'description': """
		This module get the sales summary between the given dates .
    				""",
    'author': "Prixgen tech Solutions",
    'depends': ['hr', 'sale','account'],
    'data': [
        'security/ir.model.access.csv',
        # 'views/project_assigned_emp_view.xml',
        'wizard/emp_report_view.xml',
    ],

    'installable': True,
    'auto_install': False
}
