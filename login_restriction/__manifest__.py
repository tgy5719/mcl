{
    'name': 'Login Restriction',
    'version': '0.20',
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'category': 'Security',
    'summary': " Login Restriction",
    'description': """
        Login Restriction
    """,
    'depends': ['base','crm','sale','sale_crm','sale_management','stock','account','collection_summary','stock_summary','sales_team','addon_fields_for_mcl'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv'
        'views/crm_lead_views.xml',
        'views/crm_lead_login_restriction_views.xml',
        'views/res_users_views.xml',
        'views/sale_order_views.xml',
    	],
    'auto_install': False,
    'application': True,

}