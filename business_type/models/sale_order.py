from odoo import models, fields, api, _
from odoo import tools

class SaleOrder(models.Model):
	_inherit = 'sale.order'
	
	z_cus_biz_type = fields.Many2one('customer.business.type',string='Customer Business Type',store=True,compute="check_business_type_sale")

	@api.multi
	@api.depends('partner_id')
	def check_business_type_sale(self):
		for line in self:
			if line.partner_id:
				line.z_cus_biz_type = line.partner_id.z_cus_biz_type.id

