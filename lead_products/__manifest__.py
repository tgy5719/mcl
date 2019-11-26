
{
    'name': "Products In Lead And Opportunity",
    'version': '0.2',
    'author': 'Prixgen Tech Solutions Pvt Ltd.',
    'company': 'Prixgen Tech Solutions Pvt Ltd.',
    'website': 'https://www.prixgen.com',
    'category': 'Sales',
    'depends': ['base', 'crm', 'product', 'sale', 'sale_crm'],
    'data': [
             'views/lead_product_view.xml',
             'views/opportunity_pdt_views.xml',
             ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
