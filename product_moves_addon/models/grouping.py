from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class StockMoveLine(models.Model):
	_inherit = "stock.move.line"

	z_categ_id = fields.Many2one('product.category', 'Product Category', compute="_get_category", store=True)

	@api.multi
	@api.depends('product_id')
	def _get_category(self):
		for line in self:
			prods = self.env['product.product'].search([('id','=',line.product_id.id)])
			for prod in prods:
				line.z_categ_id = prod.categ_id