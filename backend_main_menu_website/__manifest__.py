{
    'name': 'Backend Main Menu Website',
    'summary': 'Facilite the navigation through the installed modules and website.',
    'description': """
        Install a main menu where you can access all installed modules in a more visual way.
        This version adds the menu in the website.
    """,
    'category': 'Extra Tools',
    'version': '16.0.1.0',
    'author': 'Softparadox',
    'website': 'https://softparadox.com',
    'license': 'LGPL-3',
    'depends': ['website'],
    'data': [
        'views/main_menu_views.xml',
        'views/website_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'backend_main_menu_website/static/src/webclient/navbar/*',
            'backend_main_menu_website/static/src/components/main_menu/*',
        ],
    },
    'application': True,
}
