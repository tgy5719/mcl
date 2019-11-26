# -*- coding: utf-8 -*-

from odoo import fields,models,_,api



class ResConfigSettingscustomer(models.TransientModel):
	_inherit = 'res.config.settings'
	

	group_customer_internal = fields.Boolean(" Customer External", group='base.group_user',implied_group='customer_vendor_product_assets_number.group_customer_internal')
	group_customer_external_box = fields.Boolean(' Customer Internal',group='base.group_user',implied_group='customer_vendor_product_assets_number.group_customer_external_box')

	@api.model
	def get_values(self):
		res = super(ResConfigSettingscustomer, self).get_values()
		res.update(
			group_customer_internal=self.env['ir.config_parameter'].sudo().get_param('customer_vendor_product_assets_number.group_customer_internal'),
			group_customer_external_box=self.env['ir.config_parameter'].sudo().get_param('customer_vendor_product_assets_number.group_customer_external_box')
		)
		return res
	@api.multi
	def set_values(self):
		super(ResConfigSettingscustomer, self).set_values()
		self.env['ir.config_parameter'].sudo().set_param('customer_vendor_product_assets_number.group_customer_internal', self.group_customer_internal)
		self.env['ir.config_parameter'].sudo().set_param('customer_vendor_product_assets_number.group_customer_external_box', self.group_customer_external_box)
	@api.constrains('group_customer_internal')
	def _check_release_customer(self):
		for r in self:
			if r.group_customer_internal and self.group_customer_external_box == True:
				raise models.ValidationError('Both Internal and External Boolean Fields Can Not Be Selected At Time,Select Either One Of It')
