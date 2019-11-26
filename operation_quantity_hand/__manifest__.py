{
    'name': 'Operational Quantity Hand',
    'version': '12.0.0.3',
    'category': 'Stock',
    'description': """This is the module for quantity on hand flow for stock move line""",
    'author': 'Prixgen Tech Solutions Pvt Ltd.',
    'company': 'Prixgen Tech Solutions Pvt Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': ['base','stock','product'],
    'data': [
        'views/quantity_hand.xml',

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
