{
    'name': 'Loan/Advance',
    'version': '12.0.1.0.0',
    'summary': 'Manage Loan Requests',
    'description': """
        Helps you to manage Loan Requests of your company's staff.
        """,
    'category': 'Human Resources',
    
    'maintainer': 'Prixgen Tech Solutions Pvt. Ltd.',
    'author': 'Prixgen Tech Solutions Pvt Ltd.',
    'company': 'Prixgen Tech Solutions Pvt Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': [
        'base', 'hr_payroll', 'hr', 'account',
    ],
    'data': [
        'data/salary_rule_loan.xml',
        'wizard/hr_loan_wizard_view.xml',
        'views/hr_contract_view.xml',
        'views/hr_loan_view.xml',
        'views/hr_payroll.xml',
        'views/hr_loan_seq.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        ],
    'demo': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
