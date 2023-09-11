from odoo import api, fields, models


class FinanceAccount(models.Model):
    _name = 'finance.account'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Finance Account'

    name = fields.Char(string='Name')
    description = fields.Text(string='Description')
    type = fields.Selection(string='Type',
                            selection=[('account', 'Account'),
                                       ('budget', 'Budget')])
    currency_id = fields.Many2one(comodel_name='res.currency',
                                  string='Currency',
                                  default=lambda self: self.env.company.currency_id,
                                  readonly=True)
    amount = fields.Monetary(string='Amount', compute='_compute_amount')
    transaction_account_ids = fields.One2many(comodel_name='finance.transaction',
                                      inverse_name='account_id',
                                      string='Account transactions')
    transaction_budget_ids = fields.One2many(comodel_name='finance.transaction',
                                      inverse_name='budget_id',
                                      string='Budget transactions')
    goal = fields.Boolean(string='Goal')
    goal_amount = fields.Monetary(string='Goal Amount')
    goal_percentage = fields.Integer(string='Percentage', compute='_compute_goal_percentage')
    budget_end_date = fields.Date(string='Period End Date',
                                  help='Hello',
                                  default=False)
    budget_review = fields.Selection(string='Recurrence',
                                     help='Bye',
                                     selection=[('days', 'Daily'),
                                                ('weeks', 'Weekly'),
                                                ('months', 'Monthly'),
                                                ('years', 'Yearly')])
    send_email_review = fields.Boolean(string='Review email', default=False)
    # TODO: Cron and function to send a email to accounts with budget type and send_email_review True
    # TODO: In-app message with the same info that the email

    @api.depends('transaction_account_ids', 'transaction_budget_ids')
    def _compute_amount(self):
        for account in self:
            if account.type == 'account':
                account.amount = sum(transaction.amount if not transaction.has_children else 0 for transaction in account.transaction_account_ids)
            else:
                account.amount = sum(transaction.amount if not transaction.has_children else 0 for transaction in account.transaction_budget_ids)

    @api.depends('amount', 'goal_amount')
    def _compute_goal_percentage(self):
        for account in self:
            if account.goal_amount:
                account.goal_percentage = 100 * account.amount / account.goal_amount
            else:
                account.goal_percentage = 0
