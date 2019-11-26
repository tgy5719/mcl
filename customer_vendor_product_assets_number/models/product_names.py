from odoo import models, fields, api, _

class productnames(models.Model):
	_name = 'product.names'
	name= fields.Char(string='Category Name',store=True ,ondelete='cascade')
	description= fields.Char(string='Description',store=True ,ondelete='cascade')

