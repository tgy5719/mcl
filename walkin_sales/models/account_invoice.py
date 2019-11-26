from odoo import models, fields, api, _

class AccountInvoice(models.Model):
	_inherit = 'account.invoice'

	zz_walkin	= fields.Boolean(string='Walkin')
	
	zz_street_walk		= fields.Char(string='Street')
	zz_street2_walk 	= fields.Char(string='Street 2')
	zz_city_walk		= fields.Char(string='City')
	zz_state_id_walk	= fields.Many2one('res.country.state',string='State')
	zz_zip_walk			= fields.Char(string='ZIP')
	zz_country_id_walk	= fields.Many2one('res.country',string='Country')
	zz_phone_walk		= fields.Char(string='Phone No')
	zz_email_walk		= fields.Char(string='Email ID')
	zz_mobile_walk		= fields.Char(string='Mobile No')