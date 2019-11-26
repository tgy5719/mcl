# -*- coding: utf-8 -*-

from odoo import fields,models,_,api



class ResConfigSettingsvendor(models.TransientModel):
	_inherit = 'res.config.settings'
	

	group_vendor_internal = fields.Boolean("Vendor External", group='base.group_user',implied_group='customer_vendor_product_assets_number.group_vendor_internal')
	group_vendor_external_box = fields.Boolean('Vendor Internal',group='base.group_user',implied_group='customer_vendor_product_assets_number.group_vendor_external_box')

	@api.model
	def get_values(self):
		res = super(ResConfigSettingsvendor, self).get_values()
		res.update(
			group_vendor_internal=self.env['ir.config_parameter'].sudo().get_param('customer_vendor_product_assets_number.group_vendor_internal'),
			group_vendor_external_box=self.env['ir.config_parameter'].sudo().get_param('customer_vendor_product_assets_number.group_vendor_external_box')
		)
		return res
	@api.multi
	def set_values(self):
		super(ResConfigSettingsvendor, self).set_values()
		self.env['ir.config_parameter'].sudo().set_param('customer_vendor_product_assets_number.group_vendor_internal', self.group_vendor_internal)
		self.env['ir.config_parameter'].sudo().set_param('customer_vendor_product_assets_number.group_vendor_external_box', self.group_vendor_external_box)
	@api.constrains('group_vendor_internal')
	def _check_release_vendor(self):
		for r in self:
			if r.group_vendor_internal and self.group_vendor_external_box == True:
				raise models.ValidationError('Both Internal and External Boolean Fields Can Not Be Selected At Time,Select Either One Of It')
