from odoo import api, models, fields, _, exceptions


class Total(models.Model):
	_inherit = "mrp.production"




	qty_total = fields.Float(string='Total', store=True)
	product_uom_qty_total = fields.Float(string='Total', store=True)