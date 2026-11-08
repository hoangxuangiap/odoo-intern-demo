{
    'name': 'Intern - OWL Widgets & Dashboard',
    'version': '19.0.1.0.0',
    'category': 'Technical',
    'summary': 'Star-rating field widget for supplier ratings + simple OWL dashboard client action',
    'author': 'Intern',
    'depends': ['intern_supplier_rating', 'sale', 'purchase', 'stock'],
    'data': ['views/supplier_rating_views.xml', 'views/dashboard_views.xml'],
    'assets': {
        'web.assets_backend': [
            'intern_owl_widgets/static/src/scss/intern_owl.scss',
            'intern_owl_widgets/static/src/js/star_rating_field.js',
            'intern_owl_widgets/static/src/xml/star_rating_field.xml',
            'intern_owl_widgets/static/src/js/dashboard.js',
            'intern_owl_widgets/static/src/xml/dashboard.xml',
        ],
    },
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}
