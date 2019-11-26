
{
    'name': 'Dimension',
    'version': "0.1",
    'author': 'Prixgen Tech Solutions Pvt Ltd.',
    'company': 'Prixgen Tech Solutions Pvt Ltd.',
    'website': 'https://www.prixgen.com',
    'summary': 'Dimension information for invoice lines',
    'license': 'AGPL-3',
    'depends': ['account','account_reports'],
    'data': [
        'security/ir.model.access.csv',
        'security/account_cost_center_security.xml',
        'data/account_financial_report_data.xml',
        'views/account_account.xml',
        'views/account_cost_center.xml',
        'views/account_move.xml',
        'views/account_move_line.xml',
        'views/account_invoice.xml',
        'views/account_invoice_report.xml',
        'views/report_financial.xml',
    ],
    'installable': True,
}
