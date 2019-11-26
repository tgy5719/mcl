{
    'name': 'Walkin Sales',
    'version': '0.1',
    'category': 'Sales',
    'summary': 'Add details of walkin sales customers',
    'author': 'Prixgen Tech Solutions Pvt Ltd.',
    'company': 'Prixgen Tech Solutions Pvt Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': ['sale_management','base','sale','account'],
    'data': [
        'views/account_invoice_views.xml',
        'views/sale_order_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
