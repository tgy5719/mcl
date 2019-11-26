from odoo import models, fields, api, _

class ResPartners(models.Model):
	_name = 'res.partner1'
	name= fields.Char(string='Category Type',store=True ,ondelete='cascade')
	description= fields.Text(string='Description',store=True ,ondelete='cascade')
class ResPartners(models.Model):
	_name = 'res.partner2'
	name= fields.Char(string='Category Type',store=True ,ondelete='cascade')
	description= fields.Text(string='Description',store=True ,ondelete='cascade')