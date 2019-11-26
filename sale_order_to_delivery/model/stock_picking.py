from odoo import models, fields, api

class StockPicking(models.Model):
	_inherit = 'stock.move'
	z_initial_demand_in_boxes = fields.Float(string='Initial Demand in Boxes',compute='_stockmove')
	z_done_qty_in_boxes = fields.Float(string='Done Quantity in Boxes',compute='compute_qty_done')
	z_qty = fields.Float(string='Qty',related='product_id.packaging_ids.qty',store=True)
	@api.multi
	def _stockmove(self):
		for l in self:
			line_env = self.env['sale.order.line'].search([('id','=',l.sale_line_id.id)])
			for line in line_env:
				if l.sale_line_id:
					l.z_initial_demand_in_boxes = line.z_no_of_package
	@api.multi
	@api.depends('quantity_done')
	def compute_qty_done(self):
		qty = 0.0
		for line in self:
			if line.quantity_done != 0 and line.z_qty != 0:
				line.z_done_qty_in_boxes = line.quantity_done / line.z_qty

class StockMoveLine(models.Model):
	_inherit = "stock.move.line"

	z_quantity_on_hand_in_boxes = fields.Float(string='Quantity on hand in Boxes',compute='compute_qty_done')
	z_reserved_qty_in_boxes = fields.Float(string='Reserved Qty. in Boxes',compute='compute_qty_done')
	z_done_qty_in_boxes = fields.Float(string='Done Qty. in Boxes')
	z_qty = fields.Float(string='Qty',related='product_id.packaging_ids.qty',store=True)

	@api.multi
	@api.depends('z_qunatity_on_hand','product_uom_qty')
	def compute_qty_done(self):
		qty = 0.0
		for i in self:
			if i.picking_id.sale_id:
				if i.z_qunatity_on_hand and i.z_qty >= 1:
					qty =float(i.z_qunatity_on_hand)
					i.z_quantity_on_hand_in_boxes = qty / i.z_qty
				if i.product_uom_qty and i.z_qty >= 1:
					i.z_reserved_qty_in_boxes = i.product_uom_qty / i.z_qty

	@api.multi
	@api.onchange('qty_done')
	def compute_done_qty_boxes(self):
		for line in self:
			if line.qty_done >= 1 and line.z_qty >= 1:
				line.z_done_qty_in_boxes = line.qty_done / line.z_qty

	@api.multi
	@api.onchange('z_done_qty_in_boxes')
	def compute_done_qty(self):
		for line in self:
			if line.z_done_qty_in_boxes >= 1:
				line.qty_done = line.z_done_qty_in_boxes * line.z_qty






	               