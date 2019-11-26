{
    'name': 'sale Delivery Slip customized',
    'summary': 'quotation',
    'category': 'product',
    'version': '12.0.0.7(Delivery Date)',
    'description': """Print and Send your Sales Order by Post""",
    'depends': ['base', 'stock','sale_management'],
    'website': 'http://www.prixgen.com',
    'data': ['report/delivery.xml','views/stock_view.xml'],
    'auto_install': False,
    'application': True,
}
