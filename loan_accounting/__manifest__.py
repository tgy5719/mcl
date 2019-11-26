{
    'name': 'Loan/Advance Accounting',
    'version': '12.0.1.0.0',
    'summary': 'Loan Accounting',
    'description': """
        Create accounting entries for loan requests.
        """,
    'category': 'Human Resources',
    'author': 'Prixgen Tech Solutions Pvt Ltd.',
    'company': 'Prixgen Tech Solutions Pvt Ltd.',
    'website': 'https://www.prixgen.com',
    'maintainer': 'Prixgen Tech Solutions Pvt. Ltd.',
    
    'depends': [
        'base', 'hr_payroll', 'hr', 'account','loan',
    ],
    'data': [
        'views/hr_loan_config.xml',
        'views/hr_loan_acc.xml',
        ],
    'demo': [],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
