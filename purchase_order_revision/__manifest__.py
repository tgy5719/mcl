{
    "name": "Purchase order revisions",
    'version': '12.0',
    'author': 'Prixgen Tech Solutions Pvt Ltd.',
    'company': 'Prixgen Tech Solutions Pvt Ltd.',
    'website': 'https://www.prixgen.com',
    "category": "Purchase Management",
    "summary": "Purchase revision history",
    "license": "AGPL-3",
    "depends": [
        "purchase",
    ],
    "data": [
        "views/purchase_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
