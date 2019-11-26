{
    'name': 'Payslip Batch Confirm',
    'version': '0.5',
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'category': 'Human Resources',
    'summary': " Payslip Batch Confirm",
    'description': """
        Payslip Batch Confirm.
        Developed by Deekshith H M
    """,
    'depends': ['account','hr_payroll','prix_analytic_account','loan_accounting'],
    'data': [
        'views/hr_payroll_payslips_by_employee_views.xml',
        'views/hr_payroll_views.xml',
    	],
    'auto_install': False,
    'application': True,

}

