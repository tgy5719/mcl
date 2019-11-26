# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _

class StockProductionLot(models.Model):
	_inherit = "stock.production.lot"

	z_analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')