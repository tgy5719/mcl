{
    'name': 'Journal Entry Report',
    'version': '12.0.2',
    'author': 'Prixgen Tech Solutions Pvt Ltd',
    'summary': 'Print a particular Journal Entry',
    'description': """  """,
    'category': 'Accounting',
    'website': 'https://www.prixgen.com/',


    'depends': ['base', 'account',
                ],

    'data': [
        'views/report_journal_entry.xml'
    ],

    'qweb': [],


    'installable': True,
    'application': True,
    'auto_install': False,
}
