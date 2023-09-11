from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class FinanceTransaction(models.Model):
    _name = 'finance.transaction'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'The transactions'

    name = fields.Char(string='Name')
    description = fields.Text(string='Description')
    date = fields.Date(string='Date',
                       default= lambda self: self.browse(self.env.context.get('active_id')).date or date.today())
    currency_id = fields.Many2one(comodel_name='res.currency',
                                  string='Currency',
                                  default=lambda self: self.env.company.currency_id,
                                  readonly=True)
    amount = fields.Monetary(string='Amount', compute='_compute_amount', readonly=False, store=True)
    parent_id = fields.Many2one(comodel_name='finance.transaction',
                                string='Parent transaction',
                                ondelete='cascade')
    child_ids = fields.One2many(comodel_name='finance.transaction',
                                inverse_name='parent_id',
                                string='Sub-transactions')
    has_children = fields.Boolean(compute='_compute_has_children')
    account_id = fields.Many2one(comodel_name='finance.account',
                                 string='Account',
                                 domain=[('type', '=', 'account')],
                                 compute='_compute_account_id',
                                 readonly=False,
                                 store=True,
                                 default=lambda self: self.env['finance.transaction'].search([('parent_id', '=', False)], order='date desc, id desc', limit=1).account_id)
    budget_id = fields.Many2one(comodel_name='finance.account',
                                string='Budget',
                                domain=[('type', '=', 'budget')],
                                compute='_compute_budget_id',
                                readonly=False,
                                store=True)
    transference_id = fields.Many2one(comodel_name='finance.transference', string='Transference', ondelete='cascade')
    category_ids = fields.Many2many(comodel_name='finance.category',
                                    string='Category',
                                    compute='_compute_category_ids',
                                    readonly=False,
                                    store=True)
    is_recurrent = fields.Boolean(string='Is Recurrent?', default=False)
    recurrence = fields.Selection(string='Recurrence',
                                  selection=[('days', 'Daily'),
                                             ('weeks', 'Weekly'),
                                             ('months', 'Monthly'),
                                             ('years', 'Yearly')])
    next_recurrence = fields.Date(string='Next Recurrence',
                                  compute='_compute_next_recurrence',
                                  store=True)
    recurrence_email = fields.Boolean(string='Email Notification')
    tracking_period = fields.Selection(string='Tracking Period',
                                       selection=[('no', 'No track'),
                                                  ('weeks', 'After 1 Week'),
                                                  ('months', 'After 1 month'),
                                                  ('years', 'After 1 year')])
    # TODO: Add an field to add the calification

    @api.depends('child_ids')
    def _compute_amount(self):
        for transaction in self:
            transaction.amount = sum(child.amount for child in transaction.child_ids) if transaction.child_ids else transaction.amount
    
    @api.depends('child_ids')
    def _compute_has_children(self):
        for transaction in self:
            transaction.has_children = len(transaction.child_ids) > 0

    @api.depends('child_ids')
    def _compute_account_id(self):
        for transaction in self:
            account_ids = [child.account_id for child in transaction.child_ids]
            unique_account_ids = set(account_ids)
            transaction.account_id = unique_account_ids.pop() if len(unique_account_ids) == 1 else False

    @api.depends('child_ids')
    def _compute_budget_id(self):
        for transaction in self:
            budget_ids = [child.budget_id for child in transaction.child_ids]
            unique_budget_ids = set(budget_ids)
            transaction.budget_id = unique_budget_ids.pop() if len(unique_budget_ids) == 1 else False

    @api.depends('child_ids')
    def _compute_category_ids(self):
        for transaction in self:
            category_ids = [child.category_ids for child in transaction.child_ids]
            unique_category_ids = set(category_ids)
            transaction.category_ids = unique_category_ids if len(unique_category_ids) > 1 else transaction.category_ids

    @api.depends('date', 'recurrence')
    def _compute_next_recurrence(self):
        for transaction in self:
            if transaction.recurrence:
                transaction.next_recurrence = transaction.date + relativedelta(**{transaction.recurrence: 1})
            else:
                transaction.next_recurrence = False

    def action_open_transaction(self):
        return {
            'name': 'Transaction',
            'type': 'ir.actions.act_window',
            'res_model': 'finance.transaction',
            'view_mode': 'form',
            'target': 'current',
            'res_id': self.id
        }

    def _cron_create_transaction(self):
        print("\n\nCron")
        transactions = self.search([('is_recurrent', '=', True), ('parent_id', '=', False), ('next_recurrence', '<', date.today())])
        print(transactions)
        for transaction in transactions:
            new_transaction = self._new_transaction_from_transaction(transaction, transaction.next_recurrence)
            for child in transaction.child_ids:
                if 'child_ids' not in new_transaction:
                    new_transaction['child_ids'] = []
                new_child = self.create(self._new_transaction_from_transaction(child, transaction.next_recurrence))
                new_transaction['child_ids'].append(new_child.id)
            self.create(new_transaction)
            transaction.next_recurrence = transaction.next_recurrence + relativedelta(**{transaction.recurrence: 1})
            self.write(transaction)

    @api.model
    def _new_transaction_from_transaction(self, transaction, date):
        return {
            'name': transaction.name,
            'description': transaction.description,
            'date': date,
            'currency_id': transaction.currency_id.id,
            'amount': transaction.amount,
            'account_id': transaction.account_id.id,
            'budget_id': transaction.budget_id.id,
            'category_ids': transaction.category_ids
        }
