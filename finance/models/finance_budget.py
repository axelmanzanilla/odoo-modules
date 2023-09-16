from odoo import api, fields, models


class FinanceBudget(models.Model):
    _name = 'finance.budget'
    _inherit = 'finance.account'
    _description = 'Finance Budget'

    transaction_ids = fields.One2many(comodel_name='finance.transaction',
                                      inverse_name='budget_id',
                                      string='Transactions')
    goal_amount = fields.Monetary(string='Goal Amount')
    goal_percentage = fields.Integer(string='Percentage',
                                     compute='_compute_goal_percentage',
                                     store=True)
    budget_end_date = fields.Date(string='Period End Date',
                                  help='Hello',
                                  default=False)
    budget_review = fields.Selection(string='Review recurrence',
                                     help='Bye',
                                     selection=[('no_review', 'No review'),
                                                ('days', 'Daily'),
                                                ('weeks', 'Weekly'),
                                                ('months', 'Monthly'),
                                                ('years', 'Yearly')],
                                     required=True,
                                     default='no_review')
    # TODO: Cron and function to send a email to accounts with budget type and send_email_review True
    # TODO: In-app message with the same info that the email
    # TODO: Change help='Hello' message

    @api.depends('amount', 'goal_amount')
    def _compute_goal_percentage(self):
        for account in self:
            if account.goal_amount:
                account.goal_percentage = 100 * account.amount / account.goal_amount
            else:
                account.goal_percentage = 0
