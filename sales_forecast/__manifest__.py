{
    'name': 'Sales forecast',
    'depends': ['crm','stock','sale'],
    'category': 'crm',
    'version':'0.1',
    'summary': "sales Forecast",
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'data': [
        'views/sale_allocation.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'active':False,
}
