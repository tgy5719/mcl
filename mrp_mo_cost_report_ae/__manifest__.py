# -*- coding: utf-8 -*-
{
    'name': 'MRP BoM Cost Report',
    'version': '12.0.1.0.0',
    'author': 'Ascents Entrepreneurs',
    'license': 'OPL-1',
    'category': 'Manufacturing',
    'summary': 'MRP BoM Cost Report',
    'description': """
MRP BoM Cost Report
-------------------
MRP BoM Cost Report MO wise
""",
    'depends': ['mrp', 'report_xlsx'],
    'data': [
        'views/mo_bom_report_views.xml',
        'views/templates.xml',
        'report/mrp_report_mo_structure.xml',

    ],
    'qweb': ['static/src/xml/mrp.xml'],
    'installable': True,
    'auto_install': False,
    'currency': 'EUR',
    'price': 20,
}
