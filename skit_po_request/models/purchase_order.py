# -*- coding: utf-8 -*-

from odoo import api, fields, models,exceptions,_
from odoo.addons import decimal_precision as dp
from datetime import datetime
import odoo.addons.decimal_precision as dp
from odoo.exceptions import Warning
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare
import time
import math

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
_STATES = [
  ('draft', 'Draft'),
  ('to_approve', 'To be approved'),
  ('approved', 'Approved'),
  ('rejected', 'Rejected')
]

class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'
	purchase_request_id = fields.Many2one('purchase.request', string='Purchase Request' , domain ="[('z_check_order','=','Open'),('state','=','approved')]")
	reference = fields.Char('Reference',store = True)
	
	@api.onchange('purchase_request_id')
	def _onchange_allowed_purchase_ids(self):
		result = {}
		purchase_line_ids = self.order_line.mapped('purchase_request_line')
		purchase_ids = self.order_line.mapped('purchase_request_id').filtered(lambda r: r.line_ids <= purchase_line_ids)

		return result

	# Load all unsold PO lines
	@api.onchange('purchase_request_id')
	def purchase_order_change(self):
		if not self.purchase_request_id:
			self.purchase_request_id = self.purchase_request_id
			return {}
		new_lines = self.env['purchase.order.line']
		for line in self.purchase_request_id.line_ids - self.order_line.mapped('purchase_request_line'):
			data = self._prepare_invoice_line_from_po_lines(line)
			new_line = new_lines.new(data)
			new_line._set_additional_po_order_fields(self)
			new_lines += new_line
		self.order_line += new_lines
		self.env.context = dict(self.env.context, from_purchase_order_change=True)
		self.purchase_request_id = False
		#changing the final_display boolean value to true once the po is used.
		return {}

	def _prepare_invoice_line_from_po_lines(self, line):
		invoice_line = self.env['purchase.order.line']

		data = {
        'purchase_request_id': line.request_id.id,
        'name': line.product_id.name,
        'product_id': line.product_id.id,
        'product_qty':line.product_qty,
        'date_planned':line.date_required,
        'product_uom':line.product_uom_id,
        'purchase_request_line':line.id,
        'categ_types':line.categ_types,
        'account_analytic_id':line.analytic_account_id.id
		}
		return data

	@api.onchange('order_line')
	def _onchange_purchase_order_origin(self):
		purchase_order_ids = self.order_line.mapped('purchase_request_id')
		if purchase_order_ids:
			self.reference = ', '.join(purchase_order_ids.mapped('name'))

	def button_confirm(self):
		for order in self:
			for l in order.order_line:
				if l.purchase_request_line:
					for line in l:
						line.purchase_request_line.z_balance_quantity_order += line.product_qty
						line.purchase_request_line.z_balance_quantity = (line.purchase_request_line.product_qty)-(line.purchase_request_line.z_balance_quantity_order)
						if line.purchase_request_line.z_balance_quantity <= 0.00:
							line.purchase_request_line.check_boolean = True
		return super(PurchaseOrder,self).button_confirm()
      
class PurchaseOrderLine(models.Model):
	_inherit = 'purchase.order.line'
	purchase_request_id = fields.Many2one('purchase.request', string='Purchase Request')
	purchase_request_line = fields.Many2one('purchase.request.line', string='Purchase Request')
	def _set_additional_po_order_fields(self, invoice):
		""" Some modules, such as Purchase, provide a feature to add automatically pre-filled
		  invoice lines. However, these modules might not be aware of extra fields which are
		  added by extensions of the accounting module.
		  This method is intended to be overridden by these extensions, so that any new field can
		  easily be auto-filled as well.
		  :param invoice : account.invoice corresponding record
		  :rtype line : account.invoice.line record
		"""
		pass  