# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.addons.stock_landed_costs.models import product
from odoo.exceptions import UserError


class LandedCost(models.Model):
	_inherit = 'stock.landed.cost'

	z_account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account', states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="The analytic account related to a sales order.")



	#commented coz of installation of 3rd party purchased app ' dev_landed_cost_average_price'
	'''@api.multi
				def button_validate(self):
					if any(cost.state != 'draft' for cost in self):
						raise UserError(_('Only draft landed costs can be validated'))
					if any(not cost.valuation_adjustment_lines for cost in self):
						raise UserError(_('No valuation adjustments lines. You should maybe recompute the landed costs.'))
					if not self._check_sum():
						raise UserError(_('Cost and adjustments lines do not match. You should maybe recompute the landed costs.'))
			
					for cost in self:
						move = self.env['account.move']
						move_vals = {
						'journal_id': cost.account_journal_id.id,
						'date': cost.date,
						'ref': cost.name,
						'z_analytic_account_id':cost.z_account_analytic_id.id,
						'line_ids': [],
						}
						for line in cost.valuation_adjustment_lines.filtered(lambda line: line.move_id):
							# Prorate the value at what's still in stock
							cost_to_add = (line.move_id.remaining_qty / line.move_id.product_qty) * line.additional_landed_cost
			
							new_landed_cost_value = line.move_id.landed_cost_value + line.additional_landed_cost
							line.move_id.write({
								'landed_cost_value': new_landed_cost_value,
								'value': line.move_id.value + line.additional_landed_cost,
								'remaining_value': line.move_id.remaining_value + cost_to_add,
								'price_unit': (line.move_id.value + line.additional_landed_cost) / line.move_id.product_qty,
								})
							# `remaining_qty` is negative if the move is out and delivered proudcts that were not
							# in stock.
							qty_out = 0
							if line.move_id._is_in():
								qty_out = line.move_id.product_qty - line.move_id.remaining_qty
							elif line.move_id._is_out():
								qty_out = line.move_id.product_qty
							move_vals['line_ids'] += line._create_accounting_entries(move, qty_out)
			
						move = move.create(move_vals)
						cost.write({'state': 'done', 'account_move_id': move.id})
						move.post()
					return True'''
