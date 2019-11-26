# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    landed_cost = fields.Boolean(string='Allow Landed cost to create in GRN screen', help="Allow Landed cost to create in GRN screen")
    landed_journal = fields.Many2one('account.journal', string='Landed Cost Journal')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            landed_journal=int(ICPSudo.get_param('landed_cost_at_receipts.landed_journal')),
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("landed_cost_at_receipts.landed_journal", self.landed_journal.id)
