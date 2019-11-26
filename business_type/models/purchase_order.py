from odoo import models, fields, api, _
from odoo import tools


class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'
	
	z_ven_biz_type = fields.Many2one('vendor.business.type',string='Vendor Business Type',store=True,compute="check_vendor_business_type")

	@api.multi
	@api.depends('partner_id')
	def check_vendor_business_type(self):
		for line in self:
			if line.partner_id:
				line.z_ven_biz_type = line.partner_id.z_ven_biz_type.id