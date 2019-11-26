{
    'name': 'GST Stock Transfer Module',
    'version': '0.14',
    'author': "Prixgen Tech Solutions Pvt. Ltd.",
    'website': 'https://www.prixgen.com',
    'company': 'Prixgen Tech Solutions Pvt. Ltd.',
    'category': 'Stock',
    'summary': "Gst Stock Transfer",
    'depends': ['stock','sale','purchase','account','product'],
    'data': [
            'views/product_category_views.xml',
            'views/product_template_views.xml',
            'views/stock_picking_views.xml',        
    	],
    'auto_install': False,
    'application': True,

}

