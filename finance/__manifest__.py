{
    'name': 'Finance',
    'summary': '',
    'description': """
    """,
    'category': 'Invoicing',
    'version': '16.0.0.1',
    'author': 'Softparadox',
    'website': 'https://softparadox.com',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/finance_transaction_views.xml',
        'views/finance_account_views.xml',
        'views/finance_transference_views.xml',
        'views/finance_category_views.xml',
        'views/finance_menuitem.xml',
    ],
    'application': True,
}
