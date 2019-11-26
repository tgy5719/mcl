{
    'name': 'Document Model',
    'version': '12.0.1.2',
    'category': 'Tools',
    'summary': "This module consists, the customized Templates",
    'depends': ['base','account_tax_python','account','l10n_in','hr','addon_fields_for_mcl'],
    'website': 'http://www.prixgen.com',
    'data': [
             'views/report_payslip_document_inherit.xml',
             'views/amt_words.xml',
             ],
    'auto_install': False,
    'application': True,
}
