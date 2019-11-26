# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare


from odoo.addons import decimal_precision as dp

from werkzeug.urls import url_encode


class PurchaseOrder(models.Model):
	_inherit = "purchase.order"
	
	#inherited field to make readonly false
	z_account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account', states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="The analytic account related to a sales order.",compute="fetch_analytic_account_id")

	@api.multi
	@api.depends('picking_type_id')
	def fetch_analytic_account_id(self):
		for line in self:
			if line.picking_type_id:
				analytic_id = self.env['account.analytic.account'].search([('z_warehouse', '=', line.picking_type_id.warehouse_id.id)])
				if analytic_id:
					for lines in analytic_id[:1]:
						line.z_account_analytic_id = lines.id

	'''@api.multi
	def action_view_invoice(self):
		action = self.env.ref('account.action_vendor_bill_template')
		result = action.read()[0]
		create_bill = self.env.context.get('create_bill', False)
		result['context'] = {
		'type': 'in_invoice',
		'default_purchase_id': self.id,
		'default_currency_id': self.currency_id.id,
		'default_company_id': self.company_id.id,
		'default_z_analytic_account_id':self.z_account_analytic_id.id,
		'company_id': self.company_id.id}
		if len(self.invoice_ids) > 1 and not create_bill:
			result['domain'] = "[('id', 'in', " + str(self.invoice_ids.ids) + ")]"
		else:
			res = self.env.ref('account.invoice_supplier_form', False)
			result['views'] = [(res and res.id or False, 'form')]
			if not create_bill:
				result['res_id'] = self.invoice_ids.id or False
		return result'''

	@api.multi
	def button_confirm(self):
		if not self.z_account_analytic_id:
			raise UserError(_('Kindly select the Analytic Account before confirming this Purchase order'))
		return super(PurchaseOrder, self).button_confirm()


class PurchaseOrderLine(models.Model):
	_inherit = "purchase.order.line"

	#new field added.. account_analytic_id is used to display in the front end. But the value is flowing in the function create_invoices
	account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account', store=True,related="order_id.z_account_analytic_id",help="The analytic account related to a sales order.")
	analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags',compute="product_id_change_analytic_default")

	@api.multi
	@api.depends('order_id.z_account_analytic_id')
	def product_id_change_analytic_default(self):
		for line in self:
			rec = self.env['account.analytic.account'].search([('id', '=', line.order_id.z_account_analytic_id.id)])
			line.analytic_tag_ids = rec.z_analytic_tag_ids.ids
