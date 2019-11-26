from odoo.addons import decimal_precision as dp
from collections import namedtuple
import json
import time
from odoo.exceptions import UserError, ValidationError,Warning
from itertools import groupby
from odoo import api, fields, models,_,exceptions
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
from operator import itemgetter

# class StockQuant(models.Model):
# 	_inherit = "stock.quant"
# 	_rec_name = "lot_id"

class StockProductionLot(models.Model):
	_inherit = "stock.production.lot"

	z_qunatity_on_hand = fields.Float(string = 'Quantity on Hand',store = True,compute = "quantity_line")
	# z_location_ids = fields.Many2many(comodel_name='stock.location',string='locations', compute='_compute_location_ids',store=True)

	@api.multi
	@api.depends('name')
	def quantity_line(self):
		for line in self:
			invoice_ids = self.env['stock.quant'].search([('product_id','=',line.product_id.id),('lot_id','=',line.name)])
			for run in invoice_ids:
				line.z_qunatity_on_hand = run.quantity

	# @api.depends('quant_ids', 'quant_ids.location_id')
	# def _compute_location_ids(self):
	# 	for lot in self:
	# 		lot.location_ids = lot.mapped('quant_ids.location_id')

class Stockmoveline(models.Model):
	_inherit = "stock.move.line"
	qunatity_on_hand = fields.Char(string = 'Quantity on Hand',compute = "quantity_line")
	#heloo  = fields.Char('hello')
	z_qunatity_on_hand = fields.Char(string = 'Quantity on Hand',store = True,compute = "quantity_line")

	z_lot_id = fields.Many2one('stock.production.lot',string='Lot/Serial number',compute='get_lot',inverse="set_lot")

	@api.multi
	@api.depends('product_id','lot_id','location_id')
	def quantity_line(self):
		for line in self:
			invoice_ids = self.env['stock.quant'].search([('product_id','=',line.product_id.id),('location_id','=',line.location_id.id),('lot_id','=',line.lot_id.id)])
			for run in invoice_ids:
				line.qunatity_on_hand = run.quantity
				line.z_qunatity_on_hand = run.quantity

	@api.onchange('z_lot_id')
	def set_lot(self):
		for line in self:
			line.lot_id = line.z_lot_id

	@api.depends('lot_id')
	def get_lot(self):
		for line in self:
			line.z_lot_id = line.lot_id

	# @api.onchange('product_id')
	# def _get_lot_filter(self):
	# 	res = {}
		
	# 	if self.picking_id.picking_type_id.code in ['outgoing','mrp_operation']:
	# 		res['domain'] = {'z_lot_id': [('product_id', '=', self.product_id),('z_qunatity_on_hand','>',0),('quant_ids.location_id','=',self.location_id)]}
	# 	elif self.picking_id.picking_type_id.code in ['incoming','internal']:
	# 		res['domain'] = {'z_lot_id': [('product_id', '=', self.product_id),('quant_ids.location_id','=',self.location_id)]}

	# 	return res