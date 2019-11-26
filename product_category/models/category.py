from odoo import models, fields,api

class Category(models.Model):
	_name = 'product.template'
	_inherit = 'product.template'

	categ_assets =  fields.Boolean('Assets', default=False)
	categ_product = fields.Boolean('Products', default=False)
	categ_charge =  fields.Boolean('Charge', default=False)
	categ_service = fields.Boolean('Services', default=False)

	@api.constrains('categ_assets')
	def _check_assets(self):
		if self.type == 'consu' or self.type == 'product' or self.type == 'service':
			for r in self:
				if r.categ_assets == True and self.categ_product == True:
					raise models.ValidationError('Any one of the category type should be selected')
				if r.categ_assets == True and self.categ_charge == True:
					raise models.ValidationError('Any one of the category type should be selected')
				if r.categ_assets == True and self.categ_service == True:
					raise models.ValidationError('Any one of the category type should be selected')


	@api.constrains('categ_product')
	def _check_product(self):
		if self.type == 'consu' or self.type == 'product' or self.type == 'service':
			for r in self:
				if r.categ_product == True and self.categ_assets == True:
					raise models.ValidationError('Any one of the category type should be selected')
				if r.categ_product == True and self.categ_charge == True:
					raise models.ValidationError('Any one of the category type should be selected')
				if r.categ_product == True and self.categ_service == True:
					raise models.ValidationError('Any one of the category type should be selected ')


	@api.constrains('categ_service')
	def _check_service(self):
		if self.type == 'service' or self.type == 'consu' or self.type == 'product':
			for r in self:
				if r.categ_service == True and self.categ_charge == True:
					raise models.ValidationError('Any one of the category type should be selected ')
				if r.categ_service == True and self.categ_assets == True:
					raise models.ValidationError('Any one of the category type should be selected')
				if r.categ_service == True and self.categ_product == True:
					raise models.ValidationError('Any one of the category type should be selected ')


	@api.constrains('categ_charge')
	def _check_charge(self):
		if self.type == 'service' or self.type == 'consu' or self.type == 'product':
			for r in self:
				if r.categ_charge == True and self.categ_service == True:
					raise models.ValidationError('Any one of the category type should be selected')
				if r.categ_charge == True and self.categ_assets == True:
					raise models.ValidationError('Any one of the category type should be selected ')
				if r.categ_charge == True and self.categ_product == True:
					raise models.ValidationError('Any one of the category type should be selected')

	@api.onchange('type')
	def _change_type(self):
		self.categ_product = False
		self.categ_assets = False
		self.categ_service = False
		self.categ_charge = False


		