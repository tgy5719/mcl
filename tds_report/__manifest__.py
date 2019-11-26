{
    'name': 'TDS Report',
    'summary': 'TDS Report',
    'category': 'account',
    'version': '0.6',
    'description': """Print and Send your Sales Order by Post""",
    'depends': ['base', 'tds_calculation','account'],
    'author': 'Prixgen Tech Solutions Pvt Ltd.',
    'company': 'Prixgen Tech Solutions Pvt Ltd.',
    'website': 'https://www.prixgen.com',
    'data': ['report/report_template.xml', 'wizard/tds_date.xml', 'views/addcin.xml'],
    'auto_install': False,
    'application': True,
}
