{
    'name': 'Stock Picking Invoice Link',
    'version': '11.0.1.0.0',
    'author': 'Prixgen Tech Solutions Pvt Ltd.',
    'company': 'Prixgen Tech Solutions Pvt Ltd.',
    'website': 'https://www.prixgen.com',
    'category': 'Warehouse Management',
    'summary': 'Adds link between pickings and invoices',

    'license': 'AGPL-3',
    'depends': [
        'sale_stock','sale'
    ],
    'data': [
        'views/stock_view.xml',
        'views/account_invoice_view.xml',
    ],
    'installable': True,
}



