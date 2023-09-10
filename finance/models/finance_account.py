from odoo import api, fields, models


class FinanceAccount(models.Model):
    _name = 'finance.account'
    _description = 'The accounts'

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
                                      string='Transactions')
    transaction_budget_ids = fields.One2many(comodel_name='finance.transaction',
                                      inverse_name='budget_id',
                                      string='Transactions')

    @api.depends('transaction_account_ids', 'transaction_budget_ids')
    def _compute_amount(self):
        for account in self:
            if account.type == 'account':
                account.amount = sum(transaction.amount if not transaction.has_children else 0 for transaction in account.transaction_account_ids)
            else:
                account.amount = sum(transaction.amount if not transaction.has_children else 0 for transaction in account.transaction_budget_ids)
