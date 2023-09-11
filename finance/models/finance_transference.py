from odoo import api, fields, models


class FinanceTransference(models.Model):
    _name = 'finance.transference'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Finance Transference'

    name = fields.Char(string='Name', readonly=True)
    description = fields.Text(string='Description')
    date = fields.Date(string='Date', default=fields.Date.today)
    type = fields.Selection(string='Type',
                            selection=[('account', 'Account'),
                                       ('budget', 'Budget'),
                                       ('both', 'Account & Budget')],
                            default='account',
                            required=True)
    account_from = fields.Many2one(comodel_name='finance.account',
                                   string='Account from',
                                   domain=[('type', '=', 'account')],
                                   default=False)
    account_to = fields.Many2one(comodel_name='finance.account',
                                 string='Account to',
                                 domain=[('type', '=', 'account')],
                                 default=False)
    budget_from = fields.Many2one(comodel_name='finance.account',
                                   string='Budget from',
                                   domain=[('type', '=', 'budget')])
    budget_to = fields.Many2one(comodel_name='finance.account',
                                 string='Budget to',
                                 domain=[('type', '=', 'budget')])
    currency_id = fields.Many2one(comodel_name='res.currency',
                                  string='Currency',
                                  default=lambda self: self.env.company.currency_id,
                                  readonly=True)
    amount = fields.Monetary(string='Amount', compute='_compute_amount', readonly=False, store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            name_from = self.env['finance.account'].browse(vals['account_from']).name or self.env['finance.account'].browse(vals['budget_from']).name
            name_to = self.env['finance.account'].browse(vals['account_to']).name or self.env['finance.account'].browse(vals['budget_to']).name
            vals['name'] = 'Transference ' + name_from + ' -> ' + name_to
        res_ids = super(FinanceTransference, self).create(vals_list)
        for transference in res_ids:
            self.env['finance.transaction'].create({
                'name': f'Sent to {transference.account_to.name or transference.budget_to.name}',
                'description': transference.description,
                'date': transference.date,
                'amount': -1 * transference.amount,
                'account_id': transference.account_from.id,
                'budget_id': transference.budget_from.id,
                'transference_id': transference.id
            })
            self.env['finance.transaction'].create({
                'name': f'Received from {transference.account_from.name or transference.budget_from.name}',
                'description': transference.description,
                'date': transference.date,
                'amount': transference.amount,
                'account_id': transference.account_to.id,
                'budget_id': transference.budget_to.id,
                'transference_id': transference.id
            })
        return res_ids
