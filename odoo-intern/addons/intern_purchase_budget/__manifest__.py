{
    'name': 'Intern - Purchase Budget Control',
    'version': '19.0.1.0.0',
    'category': 'Inventory/Purchase',
    'summary': 'Monthly purchase budget per product category, checked when confirming a PO',
    'author': 'Intern',
    'depends': ['purchase'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/purchase_budget_views.xml',
    ],
    'demo': ['demo/demo.xml'],
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}
