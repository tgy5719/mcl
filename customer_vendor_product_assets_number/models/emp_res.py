# -*- coding: utf-8 -*-

from odoo import fields,models,_,api



class ResConfigSettingsemp(models.TransientModel):
	_inherit = 'res.config.settings'
	

	group_hr_internal = fields.Boolean(" Employee External", group='base.group_user',implied_group='customer_vendor_product_assets_number.group_hr_internal')
	group_hr_external_box = fields.Boolean('Employee Internal',group='base.group_user',implied_group='customer_vendor_product_assets_number.group_hr_external_box')
	#group_auto_indent_create = fields.Boolean("Auto Indent Creation",group='base.group_user',implied_group='mrpindent.group_auto_indent_create')


	@api.model
	def get_values(self):
		res = super(ResConfigSettingsemp, self).get_values()
		res.update(
			group_hr_internal=self.env['ir.config_parameter'].sudo().get_param('customer_vendor_product_assets_number.group_hr_internal'),
			group_hr_external_box=self.env['ir.config_parameter'].sudo().get_param('customer_vendor_product_assets_number.group_hr_external_box')
		)
		return res
	@api.multi
	def set_values(self):
		super(ResConfigSettingsemp, self).set_values()
		self.env['ir.config_parameter'].sudo().set_param('customer_vendor_product_assets_number.group_hr_internal', self.group_hr_internal)
		self.env['ir.config_parameter'].sudo().set_param('customer_vendor_product_assets_number.group_hr_external_box', self.group_hr_external_box)
	@api.constrains('group_hr_internal')
	def _check_release_date_hr(self):
		for r in self:
			if r.group_hr_internal and self.group_hr_external_box == True:
				raise models.ValidationError('Both Internal and External Boolean Fields Can Not Be Selected At Time,Select Either One Of It')
