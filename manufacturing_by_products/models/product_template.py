from odoo import api, fields, models,_

class ProductTMPL(models.Model):
	_inherit = 'product.template'
	
	z_by_product = fields.Boolean('By Product')
	z_conversion_ratio = fields.Float('Conversion Ratio',default="1.00")
