# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round, float_is_zero, pycompat
from odoo.addons import decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)

SPLIT_METHOD = [
    ('equal', 'Equal'),
    ('by_quantity', 'By Quantity'),
    ('by_current_cost_price', 'By Current Cost'),
    ('by_weight', 'By Weight'),
    ('by_volume', 'By Volume'),
]

class StockPicking(models.Model):
	_inherit = 'stock.picking'

	landed_cost_receipt_ids = fields.One2many('landed.cost.receipt','landed_cost_id')
	z_posted_btn = fields.Boolean(string="Posted",track_visibility='always',compute="func_to_check_landed_cost_lines")


	@api.multi
	@api.depends('landed_cost_receipt_ids','landed_cost_receipt_ids.z_posted')
	def func_to_check_landed_cost_lines(self):
		i = 0
		for line in self:
			for lines in line.landed_cost_receipt_ids:
				if i == 0:
					if lines.z_posted == False:
						i = 1
						line.z_posted_btn = True
					else:
						line.z_posted_btn = False
					

	def create_landed_cost(self):
		post = 0
		journal_id = self.env['ir.config_parameter'].sudo().get_param('landed_cost_at_receipts.landed_journal')
		if not journal_id:
			raise UserError(_('Please configure Landed Cost Journal in Inventory Setting.'))
		for line in self:
			for lines in line.landed_cost_receipt_ids:
				if lines.z_posted == False:
					post = 1
					picking_ids = [(4, picking_ids.id, None) for picking_ids in lines.picking_ids]
			if post == 1:
				vals = {
					'date':line.scheduled_date,
					'picking_ids':picking_ids,
					'account_journal_id':int(journal_id),
					'z_stock_picking':line.id,
					'z_account_analytic_id':line.analytic_account_id.id
				}
				landed_obj = self.env['stock.landed.cost'].create(vals)
				landed_cost_lines = self.env['stock.landed.cost.lines']
			for cost_lines in line.landed_cost_receipt_ids:
				if cost_lines.z_posted==False:
					move_line = {
					'price_unit':cost_lines.price_unit,
					'product_id':cost_lines.product_id.id,
					'split_method':cost_lines.split_method,
					'cost_id':landed_obj.id,
					'name':cost_lines.name,
					'account_id':cost_lines.account_id.id

					}
					landed_cost_lines.create(move_line)
					cost_lines.z_posted = True
			if post == 1:
				landed_obj.compute_landed_cost()
				landed_obj.button_validate()
				post = 2

	@api.multi
	def view_landed_cost_tree(self):
		for line in self:
			for lines in line.landed_cost_receipt_ids:
				picking_ids = [(4, picking_ids.id, None) for picking_ids in lines.picking_ids]
			tree_view = self.env.ref('stock_landed_costs.view_stock_landed_cost_tree')
			view_id = self.env.ref('stock_landed_costs.view_stock_landed_cost_form')
			return {
				'name': _('Landed Cost'),
				'view_type': 'form',
				'view_mode': 'tree, form',
				'res_model': 'stock.landed.cost',
				'domain': [('z_stock_picking', '=', line.id)],
				'res_id': self.id,
				'view_id': view_id.id,
				'views': [
						(tree_view.id, 'tree'),(view_id.id, 'form')
						],
				'type': 'ir.actions.act_window',
				}

class LandedCostReceipts(models.Model):
	_name = "landed.cost.receipt"
	_description = "Landed Cost at Receipt"


	landed_cost_id = fields.Many2one('stock.picking','Picking Ref for Landed cost')

	name = fields.Char(string="Name")
	
	product_id = fields.Many2one('product.product', 'Product', required=True)
	price_unit = fields.Float('Cost', digits=dp.get_precision('Product Price'), required=True)
	split_method = fields.Selection(SPLIT_METHOD, string='Split Method', required=True)
	account_id = fields.Many2one('account.account', 'Account', domain=[('deprecated', '=', False)])
	cost_id = fields.Float('Cost')
	picking_ids = fields.Many2many('stock.picking', 'landed_pick_ids',string='Transfers',copy=False,compute="get_picking_ids")
	z_posted = fields.Boolean(string="Posted")

	@api.multi
	@api.depends('landed_cost_id')
	def get_picking_ids(self):
		picking_ids = 0
		for line in self:
			if line.landed_cost_id:
				#picking_ids = self.env['stock.picking'].search([('id', '=', line.landed_cost_id.id)]).ids
				picking_ids = [(4, picking_ids.id, None) for picking_ids in line.landed_cost_id]
			line.picking_ids = picking_ids


	@api.onchange('product_id')
	def onchange_product_id(self):
		if not self.product_id:
			self.quantity = 0.0
		self.name = self.product_id.name or ''
		self.split_method = self.product_id.split_method or 'equal'
		self.price_unit = self.product_id.standard_price or 0.0
		self.cost_id = self.product_id.standard_price or 0.0
		self.account_id = self.product_id.property_account_expense_id.id or self.product_id.categ_id.property_account_expense_categ_id.id