{
    "name": "Sale order revisions",
    "version": "12.0.1.0.0",
    "category": "Sale Management",
    'author': 'Prixgen Tech Solutions Pvt Ltd.',
    'company': 'Prixgen Tech Solutions Pvt Ltd.',
    'website': 'https://www.prixgen.com',
    "license": "AGPL-3",
    "depends": [
        "sale_management",
    ],
    "data": [
        "view/sale_order.xml",
    ],
    "installable": True,
    "post_init_hook": "populate_unrevisioned_name",
}
