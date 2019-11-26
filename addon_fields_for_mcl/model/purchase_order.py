from odoo import models, fields, api, _

class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'

	
	z_order_type = fields.Many2one('purchase.order.type',string='Order Type',store=True)
	z_payment_method = fields.Many2one('custom.fields',string='Payment Method',store=True ,index=True,ondelete='cascade')
	ext_doc_no = fields.Char(string='External Document No', store=True)
	remark=fields.Text('Remark')
	# Import Fields
	port_of_discharge = fields.Many2one('port.order', string='Port Of Discharge')
	port_of_destination = fields.Many2one('port.order', string='Port Of Destination')
	country_of_origin_goods = fields.Many2one('res.country', string='Country Of Origin Of Goods')
	country_of_final_destination = fields.Many2one('res.country', string='Country Of Final Destination')
	pre_carriage= fields.Selection([
        ('air', 'By Air'),
        ('rail', 'Rail'),
        ('road', 'Road')], string='Pre Carriage')
	carriage= fields.Selection([
        ('sea', 'Sea')], string='Carriage')
	export_shipment_method = fields.Many2one('export.shipment', string='Shipment Method')
	type_of_container = fields.Many2one('type.container', string='Type Of Container')

	@api.multi
	def action_view_invoice(self):
		action = self.env.ref('account.action_vendor_bill_template')
		result = action.read()[0]
		create_bill = self.env.context.get('create_bill', False)
		result['context'] = {
			'type': 'in_invoice',
			'default_purchase_id': self.id,
			'default_currency_id': self.currency_id.id,
			'default_company_id': self.company_id.id,
			'company_id': self.company_id.id,
			'default_z_order_type_po': self.z_order_type.id,
			'default_z_payment_method': self.z_payment_method.id,
			#field is fetched from prix_analytic_account
			'default_z_analytic_account_id':self.z_account_analytic_id.id,
			#field is fetched from letter_of_credit
			'default_lc_no':self.lc_no.id,
			'default_ext_doc_no': self.ext_doc_no,
		}
		if len(self.invoice_ids) > 1 and not create_bill:
			result['domain'] = "[('id', 'in', " + str(self.invoice_ids.ids) + ")]"
		else:
			res = self.env.ref('account.invoice_supplier_form', False)
			result['views'] = [(res and res.id or False, 'form')]
			if not create_bill:
				result['res_id'] = self.invoice_ids.id or False
		return result
	

