{
    'name': 'Document Model',
    'version': '12.0.13',
    'category': 'Tools',
    'summary': "This module consists, the customized Templates",
    'depends': ['account_tax_python','account','l10n_in','addon_fields_for_mcl','fleet','analytical_warehouse'],
    'website': 'http://www.prixgen.com',
    'data': [
             'views/report_invoice_document_inherit.xml',
             'views/tax_amount.xml',
             'views/account_invoice_line.xml',
             ],
    'auto_install': False,
    'application': True,
}
