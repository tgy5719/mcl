from odoo import models, fields, api, _

class productneun(models.Model):
	_name = "product.neun"
	name= fields.Char(string='Category Id',store=True ,index=True,ondelete='cascade')
	description= fields.Char(string='Description',store=True ,ondelete='cascade')