# -*- coding: utf-8 -*-

{
    'name': 'Purchase Request',
    'version': '0.2',
    'summary': 'Purchase Request',
    'author': 'Prixgen Tech Solutions Pvt Ltd.',
    'company': 'Prixgen Tech Solutions Pvt Ltd.',
    'website': 'https://www.prixgen.com',
    'license': "AGPL-3",
    'description': """
        This module helps to create Pruchase Request.
    """,
    'category': "Purchase Management",
    'depends': ['purchase','advance_request','product_category'],

    "data": [
        "security/purchase_request.xml",
        "security/ir.model.access.csv",
        "data/purchase_request_seq.xml",
        "data/purchase_request_demo_data.xml",
        "views/purchase_request_view.xml",
        "reports/report_purchaserequests.xml",
        "views/purchase_request_report.xml",
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
