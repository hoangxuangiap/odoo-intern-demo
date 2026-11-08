{
    'name': 'Intern - Supplier Rating',
    'version': '19.0.1.0.0',
    'category': 'Inventory/Purchase',
    'summary': 'Rate vendors (quality, delivery, price) and show the average on the partner form',
    'description': 'Bài 1.1 (model supplier.rating) và Bài 1.2 (kế thừa res.partner, smart button).',
    'author': 'Intern',
    'depends': ['purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/supplier_rating_views.xml',
        'views/res_partner_views.xml',
    ],
    'demo': ['demo/demo.xml'],
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}
