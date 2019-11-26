# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round

class MrpProduction(models.Model):
	_inherit = 'mrp.production'

	z_planned_qty = fields.Float(string="Planned Qty",readonly=True)

	@api.multi
	def button_plan(self):
		for line in self:
			if line.z_ref_doc:
				line.z_planned_qty = 0.00
			if not line.z_ref_doc:
				line.z_planned_qty = line.product_qty

		return super(MrpProduction,self).button_plan()

	def short_close(self):
		qty = 0
		for line in self:
			for lines in line.finished_move_line_ids:
				if lines.z_by_product == False:
					qty = qty + lines.qty_done
			workorder = self.env['mrp.workorder'].search([('production_id','=',line.id)])
			for work_ids in workorder:
				work_ids.state='done'
			line.product_qty = qty


	@api.multi
	def update_by_product(self):
		for line in self:
			total_qty = 0
			for finished_lines in line.finished_move_line_ids:
				if finished_lines.state != 'done':
					if finished_lines.z_by_product == True:
						if finished_lines.z_qty_sq_mtr:
							total_qty = total_qty + finished_lines.z_qty_sq_mtr
						else:
							total_qty = total_qty + finished_lines.qty_done
					if finished_lines.z_by_product == False:
						total_qty = total_qty + finished_lines.qty_done

			for lines in line.move_raw_ids:
				if lines.state != 'done':
					#individual consumed line have multiple move lines.
					#first line consists the remaining qty to be consumed
					for move_lines in lines.active_move_line_ids:
						if move_lines.qty_done > 0:
							move_lines.update({'qty_done':total_qty * lines.unit_factor}) 
