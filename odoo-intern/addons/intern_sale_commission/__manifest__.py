{
    'name': 'Intern - Sales Commission',
    'version': '19.0.1.0.0',
    'category': 'Sales',
    'summary': 'Commission rules per salesperson, generated when the invoice is fully paid',
    'author': 'Intern',
    'depends': ['sale', 'account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/commission_views.xml',
    ],
    'demo': ['demo/demo.xml'],
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}
