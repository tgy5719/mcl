from odoo import models, fields,api

class SaleCategories(models.Model):
	_name = "sale.order.line"
	_inherit = "sale.order.line"

	categ_types = fields.Selection([('products','Products'),('services','Services'),('assets','Assets'),('charge','Charges')],'Category',default='products')
	@api.onchange('categ_types')
	def onchange_use_insurance(self):
		res = {}
		if self.categ_types == 'charge':
			res['domain'] = {'product_id': [('sale_ok', '=', True),'&',('type', '=', 'service'),('categ_charge', '=', True)]}
		elif self.categ_types == 'services':
			res['domain'] = {'product_id': [('sale_ok', '=', True),'&',('type', '=', 'service'),('categ_service', '=', True)]}
		elif self.categ_types == 'assets':
			res['domain'] = {'product_id': [('sale_ok', '=', True),'&',('type', '=', ['product','consu']),('categ_assets', '=', True)]}
		else:
			res['domain'] = {'product_id': [('sale_ok', '=', True),'&',('type', '=', ['product','consu']),('categ_product', '=', True)]}
		return res
