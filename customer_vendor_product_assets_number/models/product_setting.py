# -*- coding: utf-8 -*-

from odoo import fields,models,_,api



class ResConfigSettingsproduct(models.TransientModel):
	_inherit = 'res.config.settings'
	

	group_product_internal = fields.Boolean("Product External", group='base.group_user',implied_group='customer_vendor_product_assets_number.group_product_internal')
	group_product_external_box = fields.Boolean('Product Internal',group='base.group_user',implied_group='customer_vendor_product_assets_number.group_product_external_box')

	@api.model
	def get_values(self):
		res = super(ResConfigSettingsproduct, self).get_values()
		res.update(
			group_product_internal=self.env['ir.config_parameter'].sudo().get_param('customer_vendor_product_assets_number.group_product_internal'),
			group_product_external_box=self.env['ir.config_parameter'].sudo().get_param('customer_vendor_product_assets_number.group_product_external_box')
		)
		return res
	@api.multi
	def set_values(self):
		super(ResConfigSettingsproduct, self).set_values()
		self.env['ir.config_parameter'].sudo().set_param('customer_vendor_product_assets_number.group_product_internal', self.group_product_internal)
		self.env['ir.config_parameter'].sudo().set_param('customer_vendor_product_assets_number.group_product_external_box', self.group_product_external_box)
	@api.constrains('group_product_internal')
	def _check_release_product(self):
		for r in self:
			if r.group_product_internal and self.group_product_external_box == True:
				raise models.ValidationError('Both Internal and External Boolean Fields Can Not Be Selected At Time,Select Either One Of It')
