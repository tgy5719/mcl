from odoo import models, fields, api, _,exceptions

class ResUsers(models.Model):
	_inherit = 'res.users'

	z_password = fields.Char(string="Password")


class ResPartner(models.Model):
	_inherit = 'res.partner'

	zip = fields.Char(string="Zip",required=True)
	z_sales_manager = fields.Boolean(string="Is a Sales Manager")

