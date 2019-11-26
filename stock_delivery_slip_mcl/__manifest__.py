{
    'name': 'Stock Transfer Delivery Slip customized',
    'summary': 'quotation',
    'category': 'product',
    'version': '12.0.0.6(Delivery Date)',
    'description': """Print and Send your Sales Order by Post""",
    'depends': ['base', 'stock','sale_management','gst_stock_transfer'],
    'website': 'http://www.prixgen.com',
    'data': ['report/delivery.xml','report/delivery_copy.xml',
    'views/stock_amount.xml',
    ],
    'auto_install': False,
    'application': True,
}
