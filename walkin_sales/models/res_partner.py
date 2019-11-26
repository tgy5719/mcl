from odoo import models, fields, api, _

class ResPartner(models.Model):
	_inherit = 'res.partner'

	z_walkin	= fields.Boolean(string='Walkin',default=False)
