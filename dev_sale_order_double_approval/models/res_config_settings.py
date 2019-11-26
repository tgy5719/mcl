# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    so_double_verify = fields.Boolean(string="Double Approval")
    so_double_validation_amount = fields.Float(string="Minimum Amount")

    @api.model
    def set_values(self):
        ir_param = self.env['ir.config_parameter'].sudo()
        ir_param.set_param(
            'dev_sale_order_double_approval.so_double_verify',
            self.so_double_verify)
        ir_param.set_param(
            'dev_sale_order_double_approval.so_double_validation_amount',
            self.so_double_validation_amount)
        super(ResConfigSettings, self).set_values()


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_param = self.env['ir.config_parameter'].sudo()
        so_double_verify = \
            ir_param.get_param(
                'dev_sale_order_double_approval.so_double_verify')
        so_double_validation_amount = \
            ir_param.get_param('dev_sale_order_double_approval'
                               '.so_double_validation_amount')
        res.update(
            so_double_verify=bool(so_double_verify),
            so_double_validation_amount=float(so_double_validation_amount),
        )
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: