# -*- coding: utf-8 -*-
{
    'name': "Database auto-backup",
    'summary': 'Automated backups',
    'description': """The Database Auto-Backup""",
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': "http:/www.prixgen.com",
    'category': 'Administration',
    'version': '12.0.0.1',
    'installable': True,
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'views/backup_view.xml',
        'data/backup_data.xml',
    ],
}
