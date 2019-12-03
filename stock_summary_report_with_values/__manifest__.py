# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Devintelle Solutions (<http://devintellecs.com/>).
#
##############################################################################
{
    'name': 'Detailed Stock Summary Report -With Value',
    'version': '12.0.2',
    'category': 'Stock',
    'summary': 'Print Stock Summary Report -Beginning,  Beginning Value , Purchased,Purchased Value, Sold, Sold value, Manufactured, manufactured Value, Ending and Ending Value',
    'author': 'Prixgen Tech Solutions Pvt. Ltd.',
    'website': 'http://www.prixgen.com/',
    'depends': ['sale_stock','purchase','mrp','sale_management','product'],
    'data': [
        'wizard/stock_summary_report_with_values_views.xml',
        
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}


