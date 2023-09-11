{
    'name': 'Finance',
    'summary': 'Manage your personal finances with ease.',
    'description': """
        With this module you can track your income and expenses inside Odoo.

        Features:
        - Transaction Management: Easily record and categorize your financial transactions, including income, expenses, and transfers.
        - Account Management: Create and manage multiple financial accounts for a comprehensive view of your financial situation.
        - Budgeting: Set up and track budgets to control spending and achieve your financial goals.
        - Asset Management: Keep track of your assets and valuable possessions, and monitor their value over time.
        - Categorized Transactions: Categorize transactions into customizable categories for better expense analysis.
        - Integration: Seamlessly integrate with email for notifications and reminders.
        - Automatic Scheduling: Set up recurring transactions and let the module handle them automatically.
        - Financial Reporting: Generate detailed reports to gain insights into your financial status and trends.
    """,
    'category': 'Invoicing',
    'version': '16.0.0.5',
    'author': 'Softparadox',
    'website': 'https://softparadox.com',
    'license': 'LGPL-3',
    'depends': ['mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/finance_transaction_views.xml',
        'views/finance_account_views.xml',
        'views/finance_transference_views.xml',
        'views/finance_category_views.xml',
        'views/finance_asset_views.xml',
        'views/finance_menuitem.xml',
        'wizard/finance_asset_transaction_views.xml',
    ],
    'application': True,
}
