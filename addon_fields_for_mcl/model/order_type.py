from odoo import api, fields, models,_

class SaleOrderType(models.Model):
    _name = "sale.order.type"
    name= fields.Char(store=True ,ondelete='cascade')
    description= fields.Text(string='Description',store=True ,ondelete='cascade')

class PurchaseOrderType(models.Model):
	_name = 'purchase.order.type'
	name= fields.Char(store=True ,ondelete='cascade')
	description= fields.Text(string='Description',store=True ,ondelete='cascade')
