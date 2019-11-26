# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import namedtuple
import json
import time

from itertools import groupby
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
from operator import itemgetter

class PickingType(models.Model):
	_inherit = "stock.picking.type"
	z_interstate_bool = fields.Boolean(string="Interstate",default=False)
	z_stock_transfer = fields.Boolean(string="Stock Transfer",default=False)

class StockLocation(models.Model):
	_inherit = "stock.location"
	z_internal_transfer_bool = fields.Boolean(string="Check if the location is used for intenal transfer",default=False)	

class Picking(models.Model):
	_inherit = "stock.picking"

	z_interstate_bool = fields.Boolean(string="Interstate",default=False,related="picking_type_id.z_interstate_bool")
	currency_id = fields.Many2one("res.currency", related='company_id.currency_id', string="Currency", readonly=True, required=True)
	z_amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
	z_stock_transfer = fields.Boolean(string="Stock Transfer",default=False,related="picking_type_id.z_stock_transfer")


	@api.depends('move_lines.z_price_tax')
	def _amount_all(self):
		for order in self:
			amount_untaxed = amount_tax = 0.0
			for line in order.move_lines:
				amount_untaxed += line.z_price_subtotal
				amount_tax += line.z_price_tax
			order.update({
				'z_amount_tax': order.currency_id.round(amount_tax),
				})