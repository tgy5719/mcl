{
    'name': 'Process Costing in Manufacturing Process',
    'version': '2.2.7',
    'category' : 'Manufacturing',
    'license': 'Other proprietary',
    'price': 19.0,
    'currency': 'EUR',
    'summary': """This app allow you to do process costing (Material Cost, Labour Cost, Overheads) for manufacturing orders.""",
    'depends': [
            'mrp',
            'stock',
            'sales_team',
            'hr',
            'hr_contract',
            'product',
            'split_functionality'
    ],
    'description': """

    """,
    'author': 'Prixgen Tech Solutions Pvt Ltd.',
    'company': 'Prixgen Tech Solutions Pvt Ltd.',
    'website': 'https://www.prixgen.com',
    'data':[
        'security/ir.model.access.csv',
        'views/hr_employee.xml',
        'views/mrp_bom_view.xml',
        'views/mrp_job_cost_sheet_view.xml',
        'views/mrp_production_view.xml',
        'views/work_order_view.xml',
        'report/manufacturing_report_view.xml',
        'report/bom_report_view.xml',
    ],
    'installable' : True,
    'application' : False,
}
