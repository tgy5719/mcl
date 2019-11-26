from odoo import api, fields, models, _

class MrpProduction(models.Model):
	_inherit = 'mrp.production'

	default_code = fields.Char('Code',store=True,track_visibility='always',compute='_onchange_product_id_default_code')
	z_order_type = fields.Many2one('mrp.production.type',string='Order Type',store=True)

	@api.depends('product_id')
	def _onchange_product_id_default_code(self):
		for line in self:
			line.default_code = line.product_id.default_code

class MrpProductionType(models.Model):
	_name = "mrp.production.type"
	name= fields.Char(store=True ,ondelete='cascade')
	description= fields.Text(string='Description',store=True ,ondelete='cascade')

class MrpBom(models.Model):
	_inherit = 'mrp.bom'

	default_code = fields.Char('Code',store=True,track_visibility='always',compute='_onchange_product_bom')

	@api.depends('product_tmpl_id')
	def _onchange_product_bom(self):
		for line in self:
			line.default_code = line.product_tmpl_id.default_code


