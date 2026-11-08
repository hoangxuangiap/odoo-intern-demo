{
    'name': 'Intern - Inventory Adjustment Reason',
    'version': '19.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Require a reason when applying an inventory adjustment; store it on the stock move; report by reason',
    'author': 'Intern',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'data/reason_data.xml',
        'views/stock_views.xml',
    ],
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}
