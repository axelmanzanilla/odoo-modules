{
    'name': 'Backend Main Menu',
    'summary': 'Facilite the navigation through the installed modules.',
    'description': """
        Install a main menu where you can access all installed modules in a more visual way.
    """,
    'category': 'Extra Tools',
    'version': '16.0.0.2',
    'author': 'Softparadox',
    'website': 'https://www.softparadox.com',
    'license': 'LGPL-3',
    'depends': ['web'],
    'data': [
        'views/main_menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'backend_main_menu/static/src/webclient/navbar/*',
            'backend_main_menu/static/src/components/main_menu/*',
        ],
    },
    'application': True,
}
