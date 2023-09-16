from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class FinanceTransaction(models.Model):
    _name = 'finance.transaction'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'rating.mixin']
    _description = 'Finance Transaction'

    name = fields.Char(string='Name')
    description = fields.Text(string='Description')
    date = fields.Date(string='Date',
                       default=lambda self: self.browse(self.env.context.get('active_id')).date or date.today(),
                       copy=False)
    currency_id = fields.Many2one(comodel_name='res.currency',
                                  string='Currency',
                                  default=lambda self: self.env.company.currency_id,
                                  readonly=True)
    amount = fields.Monetary(string='Amount',
                             compute='_compute_amount',
                             readonly=False,
                             store=True)
    parent_id = fields.Many2one(comodel_name='finance.transaction',
                                string='Parent transaction',
                                ondelete='cascade')
    child_ids = fields.One2many(comodel_name='finance.transaction',
                                inverse_name='parent_id',
                                string='Sub-transactions',
                                copy=True)
    has_children = fields.Boolean(compute='_compute_has_children',
                                  store=True)
    account_id = fields.Many2one(comodel_name='finance.account',
                                 string='Account',
                                 compute='_compute_account_id',
                                 readonly=False,
                                 store=True,
                                 default=lambda self: self.env['finance.transaction'].search([('parent_id', '=', False)], order='date desc, id desc', limit=1).account_id)
    budget_id = fields.Many2one(comodel_name='finance.budget',
                                string='Budget',
                                compute='_compute_budget_id',
                                readonly=False,
                                store=True)
    transference_id = fields.Many2one(comodel_name='finance.transference',
                                      string='Transference',
                                      ondelete='cascade')
    category_ids = fields.Many2many(comodel_name='finance.category', string='Categories')
    is_recurrent = fields.Boolean(string='Is Recurrent?', default=False)
    recurrence = fields.Selection(string='Recurrence',
                                  selection=[('days', 'Daily'),
                                             ('weeks', 'Weekly'),
                                             ('months', 'Monthly'),
                                             ('years', 'Yearly')])
    next_recurrence = fields.Date(string='Next Recurrence',
                                  compute='_compute_next_recurrence',
                                  store=True)
    review_period = fields.Selection(string='Tracking Period',
                                     selection=[('no', 'No track'),
                                                ('weeks', 'After 1 Week'),
                                                ('months', 'After 1 month'),
                                                ('years', 'After 1 year')],
                                     required=True,
                                     default='no')
    next_review = fields.Date(string='Next Review',
                              compute='_compute_next_review',
                              store=True)
    review_sent = fields.Boolean(string='Review Sent', default=False)

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

    @api.depends('date', 'review_period')
    def _compute_next_review(self):
        for transaction in self:
            if transaction.review_period != 'no':
                transaction.next_review = transaction.date + relativedelta(**{transaction.review_period: 1})
            else:
                transaction.next_review = False

    def _rating_get_partner(self):
        return self.message_partner_ids[0]

    def _cron_send_review_mail(self):
        for transaction in self.search([('next_review', '<', date.today()), ('review_sent', '=', False)]):
            rating_template = self.env['mail.template'].search([('name', '=', 'Finance: Transaction Rating Request')])
            transaction.write({ 'review_sent': True })
            transaction.rating_send_request(rating_template, force_send=True)

    def _cron_create_transaction(self):
        transactions = self.search([('is_recurrent', '=', True), ('parent_id', '=', False), ('next_recurrence', '<', date.today())])
        for transaction in transactions:
            new_transaction = self._new_transaction_from_transaction(transaction, transaction.next_recurrence)
            for child in transaction.child_ids:
                if 'child_ids' not in new_transaction:
                    new_transaction['child_ids'] = []
                new_child = self.create(self._new_transaction_from_transaction(child, transaction.next_recurrence))
                new_transaction['child_ids'].append(new_child.id)
            self.create(new_transaction)
            transaction.next_recurrence = transaction.next_recurrence + relativedelta(**{ transaction.recurrence: 1 })
            self.write(transaction)

            mail_values = {
                'auto_delete': True,
                'author_id': self.env.user.partner_id.id,
                'body_html': self.env['ir.qweb']._render('finance.finance_automatic_transaction', { 'transaction': transaction }),
                'email_from': (self.env.company.partner_id.email_formatted or self.env.user.email_formatted or self.env.ref('base.user_root').email_formatted),
                'email_to': [partner.email_formatted for partner in transaction.message_partner_ids],
                'subject': f'Created transaction {transaction.name}',
            }
            self.env['mail.mail'].sudo().create(mail_values).send()
        return True

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

    def copy(self, default=None):
        transaction = super(FinanceTransaction, self).copy(default)
        transaction.date = date.today()
        for child in transaction.child_ids:
            child.date = date.today()
        return transaction
