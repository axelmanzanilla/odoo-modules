from odoo import fields, models


class FinanceAccount(models.Model):
    _name = 'finance.asset'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Finance Assets'

    name = fields.Char(string='Name')
    description = fields.Text(string='Description')
    image = fields.Image(string="Image")
    currency_id = fields.Many2one(comodel_name='res.currency',
                                  string='Currency',
                                  default=lambda self: self.env.company.currency_id,
                                  readonly=True)
    purchase_price = fields.Monetary(string='Cost')
    resale_price = fields.Monetary(string='Expected Resale Price')
    estimated_sell_time = fields.Integer(string='Estimated Sell Time') #TODO: This is in days, adds it in the help
    transaction_id = fields.Many2one(comodel_name='finance.transaction', string='Transaction')
    purchase_date = fields.Date(string='Purchase Date')
    annual_deprecation = fields.Monetary()
    accumulated_depreciation = fields.Monetary()
    residual_value = fields.Monetary()
    useful_life = fields.Integer()
    depreciation_method = fields.Selection(selection=[('', 'Straight-line'),
                                                      ('', 'Double declining balance'),
                                                      ('', 'Units of production'),
                                                      ('', 'Sum of years digits')])

    def action_sell_asset(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'finance.asset.transaction',
            'target': 'new',
            'context': {
                'active_id': self.id
            }
        }
