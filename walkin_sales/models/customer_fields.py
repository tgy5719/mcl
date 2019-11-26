from odoo import models, fields, api, _

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	
	z_walkin	= fields.Boolean(related='partner_id.z_walkin')
	
	z_street_walk		= fields.Char(string='Street')
	z_street2_walk 		= fields.Char(string='Street 2')
	z_city_walk			= fields.Char(string='City')
	z_state_id_walk		= fields.Many2one('res.country.state',string='State')
	z_zip_walk			= fields.Char(string='ZIP')
	z_country_id_walk	= fields.Many2one('res.country',string='Country')
	z_phone_walk		= fields.Char(string='Phone No')
	z_email_walk		= fields.Char(string='Email ID')
	z_mobile_walk		= fields.Char(string='Mobile No')
	