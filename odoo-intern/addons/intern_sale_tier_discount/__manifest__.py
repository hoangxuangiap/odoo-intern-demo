{
    'name': 'Intern - Sale Quantity Tier Discount',
    'version': '19.0.1.0.0',
    'category': 'Sales',
    'summary': 'Automatic discount on sale order lines based on quantity tiers defined on the product',
    'author': 'Intern',
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_views.xml',
    ],
    'demo': ['demo/demo.xml'],
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}
