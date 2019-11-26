from odoo import models, fields, api, _


class AccountInvoice(models.Model):
	_inherit = 'account.invoice'
	
	z_ven_biz_type = fields.Many2one('vendor.business.type',string='Vendor Business Type',store=True,compute="check_business_type")
	z_cus_biz_type = fields.Many2one('customer.business.type',string='Customer Business Type',store=True,compute="check_business_type")

	@api.multi
	@api.depends('partner_id')
	def check_business_type(self):
		for line in self:
			if line.type == 'out_invoice':
				if line.partner_id:
					line.z_cus_biz_type = line.partner_id.z_cus_biz_type.id
			if line.type == 'in_invoice':
				if line.partner_id:
					line.z_ven_biz_type = line.partner_id.z_ven_biz_type.id
			