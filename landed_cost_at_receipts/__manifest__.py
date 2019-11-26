{
    'name': 'Landed Cost at Receipts',
    'version': '0.4',
    'category': 'Landed Costs',
    'author': 'Prixgen Tech Solutions Pvt Ltd.',
    'company': 'Prixgen Tech Solutions Pvt Ltd.',
    'website': 'https://www.prixgen.com',
    'depends': ['base','stock','stock_landed_costs','account','product','purchase_stock','stock_account','prix_analytic_account'],
    'data': [
        'views/landed_cost_views.xml',
        'views/stock_picking_views.xml',
        'views/res_config_settings_views.xml'
        
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
}
