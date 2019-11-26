from odoo import api, fields, models,_

class HrEmployee(models.Model):
    _inherit = 'hr.contract'

    ctc_per_hour = fields.Monetary('CTC Per Hour',digits=(16, 2))

class ProductTMPL(models.Model):
	_inherit = 'product.template'

	z_process_cost = fields.Boolean('Process Cost')
	# z_by_product = fields.Boolean('By Product')

	# z_conversion_ratio = fields.Float('Conversion Ratio',default="1.00")
