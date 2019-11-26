from odoo import models, fields, api, _
class Employee(models.Model):
	_name = "hr.category"
	name= fields.Char(string='Category Id',store=True ,index=True,ondelete='cascade')
	description= fields.Char(string='Description',store=True ,ondelete='cascade')
class Employee(models.Model):
	_name = "hr.category.internal"
	name= fields.Char(string='Category Id',store=True ,index=True,ondelete='cascade')
	description= fields.Char(string='Description',store=True ,ondelete='cascade')