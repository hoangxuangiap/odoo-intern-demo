{
    'name': 'Intern - Sale Customer Credit Limit',
    'version': '19.0.1.0.0',
    'category': 'Sales',
    'summary': 'Block sale orders that exceed the customer credit limit and send them to approval',
    'author': 'Intern',
    'depends': ['sale', 'account'],
    'data': [
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
    ],
    'demo': ['demo/demo.xml'],
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}
