{
    'name': 'Intern - Simple Lot Expiry',
    'version': '19.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Expiry date on lots, daily cron alerts, warning when delivering expired lots',
    'author': 'Intern',
    'depends': ['stock', 'mail'],
    'data': [
        'data/ir_cron.xml',
        'views/stock_lot_views.xml',
    ],
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}
