{
    'name': 'Advanced Request',
    'category': 'Accounting',
    'version': '12.0.4',
    'depends': ['account','purchase','stock','account_batch_payment','account_voucher'],
    'author': 'Prixgen Tech Solutions Pvt Ltd.',
    'company': 'Prixgen Tech Solutions Pvt Ltd.',
    'website': 'https://www.prixgen.com',
    'data': [
    	'security/ir.model.access.csv',
    	'views/advanced_payment_view.xml',
    	'data/advance_payments_data.xml',
    ],
    'installable': True,
    'auto_install': False,
}
