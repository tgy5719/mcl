{
    'name': 'Letter Of Credit',
    'summary': "Letter of Credit",
    'version': '0.3',
    'author': 'Prixgen Tech Solutions Pvt Ltd.',
    'company': 'Prixgen Tech Solutions Pvt Ltd.',
    'website': 'https://www.prixgen.com',
    'category': 'Accounting & Finance',
    'depends': ['base','account','account_accountant','purchase','sale'],
    'data': [
        'views/account_journal.xml',
        'views/account_letter_credit.xml',
        'views/account_invoice.xml',
        'data/ir_data_sequence.xml',
        'security/ir.model.access.csv',
        'report/lc_template.xml',
        'report/lc_report.xml',
        'report/lc_template_self.xml',
        ],
    'auto_install': True,
    'application': True,
    
}
