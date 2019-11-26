# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    igst_intransit = fields.Boolean(string='Allow IGST Intransit Account', help="Allow IGST Intransit Account")
    igst_intransit_account = fields.Many2one('account.account', string='IGST Intransit Account')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            igst_intransit_account=int(ICPSudo.get_param('gst_stock_transfer.igst_intransit_account')),
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("gst_stock_transfer.igst_intransit_account", self.igst_intransit_account.id)
