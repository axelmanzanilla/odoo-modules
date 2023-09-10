from odoo import fields, models


class FinanceCategory(models.Model):
    _name = 'finance.category'
    _description = 'Finance Category'

    name = fields.Char(string='Name')
