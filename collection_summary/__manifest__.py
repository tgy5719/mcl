{
    'name': 'Collection Summary',
    'summary': "Collection Details",
    'version': '12.0.0.6',
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'depends': ['sale','addon_fields_for_mcl','account','account_payment','invoice_multi_payment'],
    'data': [
    'views/sale_calcu.xml',
    'views/sale_cal_detail.xml',
    'views/account_payment.xml',
    'data/calculate_details_sequence.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
