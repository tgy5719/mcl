from odoo import models, fields, api, _

class CustomerBusinessType(models.Model):
	_name = 'customer.business.type'
	
	name = fields.Char(string="Type")

class VendorBusinessType(models.Model):
	_name = 'vendor.business.type'
	
	name = fields.Char(string="Type")

class ResPartners(models.Model):
	_inherit = 'res.partner'

	z_cus_biz_type = fields.Many2one('customer.business.type',string='Customer Business Type')
	z_ven_biz_type = fields.Many2one('vendor.business.type',string='Vendor Business Type')