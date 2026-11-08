{
    'name': 'Intern - Block Negative Stock',
    'version': '19.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Block validating outgoing transfers without enough stock, unless the warehouse allows negative stock',
    'author': 'Intern',
    'depends': ['stock'],
    'data': ['views/stock_warehouse_views.xml'],
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}
