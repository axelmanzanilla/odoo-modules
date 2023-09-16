from odoo import api, fields, models


class FinanceAccount(models.Model):
    _name = 'finance.account'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Finance Account'

    name = fields.Char(string='Name')
    description = fields.Text(string='Description')
    icon = fields.Image(string="Custom Icon")
    currency_id = fields.Many2one(comodel_name='res.currency',
                                  string='Currency',
                                  default=lambda self: self.env.company.currency_id,
                                  readonly=True)
    amount = fields.Monetary(string='Amount', compute='_compute_amount')
    transaction_ids = fields.One2many(comodel_name='finance.transaction',
                                      inverse_name='account_id',
                                      string='Transactions')

    @api.depends('transaction_ids')
    def _compute_amount(self):
        for account in self:
            account.amount = sum(transaction.amount if not transaction.has_children else 0 for transaction in account.transaction_ids)
