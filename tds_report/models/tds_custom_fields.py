from odoo import models, fields, api, _

class AddPan(models.Model):
	_inherit = 'res.company'
	
	cin_no = fields.Char(string="CIN")
	# pan_no = fields.Char(string="PAN")
	# state_code = fields.Char(string="State Code")