{
    'name': 'Intern - Import Purchase Orders from Excel',
    'version': '19.0.1.0.0',
    'category': 'Inventory/Purchase',
    'summary': 'Wizard: upload an Excel file (vendor code, product code, qty, price) to create POs in bulk',
    'author': 'Intern',
    'depends': ['purchase'],
    'external_dependencies': {'python': ['openpyxl']},
    'data': [
        'security/ir.model.access.csv',
        'wizard/purchase_import_wizard_views.xml',
    ],
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}
