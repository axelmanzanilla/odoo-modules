from odoo import fields, models


class FinanceAssetTransaction(models.TransientModel):
    _name = 'finance.asset.transaction'
    _description = 'Finance Asset Transaction'

    asset_id = fields.Many2one(comodel_name='finance.asset',
                               default=lambda self: self.env.context.get('active_id'))
    name = fields.Char()

    def action_confirm_sell(self):
        # TODO: create new transaction and set state to sold
        print("Confirm")
