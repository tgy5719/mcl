from odoo import api, fields, models,_

class ResCompany(models.Model):
	_inherit="res.company"

	tan_no = fields.Char(string="TAN",store=True)
	pan_no = fields.Char(string="PAN",store=True)
	factory_reg_no = fields.Char(string="Factory Registration No.",store=True)