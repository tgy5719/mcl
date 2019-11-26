{
    'name': 'Parent Category Tree view',
    'version': '12.0.0.8',
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'category': 'Tools',
    'summary': "Module for customized fields.",
    'depends': ['base','stock','stock_account','product'],
    'data': [
             'views/stock_move_line_tree.xml',
             'views/inventory_user.xml',
             'views/stock_move.xml',
             ],
    'auto_install': False,
    'application': True,
}