from odoo import models, fields, api, _,exceptions

class CrmLead(models.Model):
	_inherit = 'crm.lead'

	z_pricelist_id = fields.Many2one('product.pricelist',string="Pricelist",related="user_id.property_product_pricelist")
	z_sales_office = fields.Many2one('office.name',string="Sales Office",related="user_id.z_sales_office")