
from odoo import api,fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    cost_center_id = fields.Many2one(
        'account.cost.center',
        index=True,
        string='Dimension'
    )

    z_cost_center_bool = fields.Boolean(string="Dimension",default=False,store=True,track_visibility='always',compute="func_dimension_check_account_move")

    @api.multi
    @api.depends('account_id')
    def func_dimension_check_account_move(self):
        for line in self:
            if line.account_id.z_cost_center_bool == True:
                line.z_cost_center_bool = True
            else:
                line.z_cost_center_bool = False
