# -*- coding: utf-8 -*-

import json
import re
import uuid
from functools import partial

from lxml import etree
from dateutil.relativedelta import relativedelta
from werkzeug.urls import url_encode

from odoo import api, exceptions, fields, models, _
from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, \
    pycompat, date_utils
from odoo.tools.misc import formatLang

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from odoo.addons import decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

# mapping invoice type to journal type
TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale',
    'in_refund': 'purchase',
}

# mapping invoice type to refund type
TYPE2REFUND = {
    'out_invoice': 'out_refund',        # Customer Invoice
    'in_invoice': 'in_refund',          # Vendor Bill
    'out_refund': 'out_invoice',        # Customer Credit Note
    'in_refund': 'in_invoice',          # Vendor Credit Note
}

MAGIC_COLUMNS = ('id', 'create_uid', 'create_date', 'write_uid', 'write_date')


class AccountInvoice(models.Model):
	_inherit = "account.invoice"


	z_analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', help="The analytic account related to a Invoice.")

	'''@api.model
	def _get_refund_modify_read_fields(self):
		read_fields = ['type','z_analytic_account_id', 'number', 'invoice_line_ids', 'tax_line_ids',
                       'date']
		return self._get_refund_common_fields() + self._get_refund_prepare_fields() + read_fields'''

	@api.multi
	def action_invoice_open(self):
		# lots of duplicate calls to action_invoice_open, so we remove those already open
		to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
		if to_open_invoices.filtered(lambda inv: not inv.z_analytic_account_id):
			raise UserError(_('Kindly select the Analytic Account before Validating this Invoice'))
		'''if to_open_invoices.filtered(lambda inv: not inv.partner_id):
									raise UserError(_("The field Vendor is required, please complete it to validate the Vendor Bill."))
								if to_open_invoices.filtered(lambda inv: inv.state != 'draft'):
									raise UserError(_("Invoice must be in draft state in order to validate it."))
								if to_open_invoices.filtered(lambda inv: float_compare(inv.amount_total, 0.0, precision_rounding=inv.currency_id.rounding) == -1):
									raise UserError(_("You cannot validate an invoice with a negative total amount. You should create a credit note instead."))
								if to_open_invoices.filtered(lambda inv: not inv.account_id):
									raise UserError(_('No account was found to create the invoice, be sure you have installed a chart of account.'))
								to_open_invoices.action_date_assign()
								to_open_invoices.action_move_create()
								return to_open_invoices.invoice_validate()'''
		return super(AccountInvoice, self).action_invoice_open()

	@api.multi
	@api.onchange('z_analytic_account_id')
	def onchange_product_id_analytic_tags(self):
		for lines in self:
			if lines.type != "out_invoice":
				for line in lines.invoice_line_ids:
					rec = self.env['account.analytic.account'].search([('id', '=', lines.z_analytic_account_id.id)])
					line.analytic_tag_ids = False
					line.analytic_tag_ids = rec.z_analytic_tag_ids.ids

	# @api.onchange('vendor_bill_purchase_id')
	# def fetch_analytic_account_for_vendor_bills(self):
	# 	for line in self:
	# 		line.z_analytic_account_id = line.vendor_bill_purchase_id.purchase_order_id.z_account_analytic_id.id

class AccountInvoiceLine(models.Model):
	_inherit = "account.invoice.line"


	account_analytic_id = fields.Many2one('account.analytic.account',store=True,related="invoice_id.z_analytic_account_id",string='Analytic Account')
	analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')