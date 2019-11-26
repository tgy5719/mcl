from odoo import api, fields, models,_


class ResPartner(models.Model):
	_inherit="res.partner"
	
	pan_no = fields.Char(string="PAN No.",store=True)
