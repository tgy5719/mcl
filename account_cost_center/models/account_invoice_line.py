
from odoo import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def _default_cost_center(self):
        return self.env['account.cost.center'].browse(
            self._context.get('cost_center_id'))

    cost_center_id = fields.Many2one(
        'account.cost.center',
        string='Dimension',
        index=True,
        default=lambda self: self._default_cost_center(),
    )
    z_cost_center_bool = fields.Boolean(string="Dimension",default=False,store=True,track_visibility='always',compute="func_dimension_check")



    @api.multi
    @api.depends('account_id')
    def func_dimension_check(self):
        for line in self:
            if line.account_id.z_cost_center_bool == True:
                line.z_cost_center_bool = True
            else:
                line.z_cost_center_bool = False