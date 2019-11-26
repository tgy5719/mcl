from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from datetime import timedelta
from collections import namedtuple
import json
import time

from itertools import groupby
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_round
from odoo.exceptions import UserError
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
from operator import itemgetter



class Stock_Inherit(models.Model):
	_inherit = "stock.picking"


	part_id = fields.Many2one('res.partner',related="sale_id.partner_invoice_id")
	z_customer_id = fields.Many2one('res.partner',related="sale_id.partner_shipping_id")
	z_deliver_to = fields.Char('Deliver To',related='sale_id.z_delivered_to')
	z_date = fields.Date('Backorder Date',compute='_date_state')
	date_delivery = fields.Datetime('Deliver Date')
	# z_total_amt = fields.Monitary(compute='_calculate_total',store=True)


	# @api.depends('move_ids_without_package')
	# def _calculate_total(self):
	# 	for line in self:
	# 		total = 0
	# 		for move_id in line.move_ids_without_package:
	# 			total += move_id.z_price_total
	# 		line.z_total_amt = total


	@api.multi
	def button_validate(self):
		self.action_date()
		self.ensure_one()
		if not self.move_lines and not self.move_line_ids:
			raise UserError(_('Please add some lines to move'))

		picking_type = self.picking_type_id
		no_quantities_done = all(line.qty_done == 0.0 for line in self.move_line_ids)
		no_initial_demand = all(move.product_uom_qty == 0.0 for move in self.move_lines)
		if no_initial_demand and no_quantities_done:
			raise UserError(_('You cannot validate a transfer if you have not processed any quantity.'))

		if picking_type.use_create_lots or picking_type.use_existing_lots:
			lines_to_check = self.move_line_ids
			if not no_quantities_done:
				lines_to_check = lines_to_check.filtered(
					lambda line: float_compare(line.qty_done, 0,
						precision_rounding=line.product_uom_id.rounding)
					)

			for line in lines_to_check:
				product = line.product_id
				if product and product.tracking != 'none':
					if not line.lot_name and not line.lot_id:
						raise UserError(_('You need to supply a lot/serial number for %s.') % product.display_name)
					elif line.qty_done == 0:
						raise UserError(_('You cannot validate a transfer if you have not processed any quantity for %s.') % product.display_name)
		if no_quantities_done:
			view = self.env.ref('stock.view_immediate_transfer')
			wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, self.id)]})
			return {
				'name': _('Immediate Transfer?'),
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'stock.immediate.transfer',
				'views': [(view.id, 'form')],
				'view_id': view.id,
				'target': 'new',
				'res_id': wiz.id,
				'context': self.env.context,
			}

		if self._get_overprocessed_stock_moves() and not self._context.get('skip_overprocessed_check'):
			view = self.env.ref('stock.view_overprocessed_transfer')
			wiz = self.env['stock.overprocessed.transfer'].create({'picking_id': self.id})
			return {
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'stock.overprocessed.transfer',
				'views': [(view.id, 'form')],
				'view_id': view.id,
				'target': 'new',
				'res_id': wiz.id,
				'context': self.env.context,
			}
		if self._check_backorder():
			return self.action_generate_backorder_wizard()
		self.action_done()
		return

	@api.multi
	def action_date(self):
		for rec in self:
			rec.date_delivery = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


	@api.multi
	def _date_state(self):
		for line in self:
			if line.backorder_id:
				if line.state == 'done':
					line.z_date = datetime.today()

