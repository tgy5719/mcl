{
    'name': 'Business Type',
    'version': '0.1',
    'author': 'Prixgen Tech Solutions Pvt Ltd.',
    'company': 'Prixgen Tech Solutions Pvt Ltd.',
    'website': 'https://www.prixgen.com',
    'category': 'Contacts',
    'summary': "Customer Vendor Business Types",
    'depends': ['base','sale','contacts','purchase','sales_team','account','addon_fields_for_mcl'],
    'data': [
        'views/account_invoice_views.xml',
    	'views/business_type_views.xml',
        'views/purchase_order.xml',
        'views/sale_order_views.xml',
    	],
    'auto_install': False,
    'application': True,

}

