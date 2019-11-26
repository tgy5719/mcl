# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare

from itertools import groupby


MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}
# Since invoice amounts are unsigned, this is how we know if money comes in or goes out
MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund': -1,
    'in_invoice': -1,
    'out_refund': 1,
}

#on selection of the record in invoice
class account_register_payments(models.TransientModel):
	_inherit = "account.register.payments"
	z_analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', required=True,help="The analytic account related to a Invoice.")
	z_analytic_tag_ids = fields.Many2many('account.analytic.tag',string='Analytic Tags',copy=True,related="z_analytic_account_id.z_analytic_tag_ids")