from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
class detailcalculation(models.Model):
	_name = 'detail.calculation'
	name = fields.Char('Name',store = True)
	user_id = fields.Many2one('res.users',string = 'Sale Persons')
	invoice_lines = fields.One2many('detail.calculation.line', 'payment_id', string="Invoice Line")
	#invoice_id = fields.Many2one('account.invoice', string="Invoice")
	invoice_ids = fields.Many2many('account.invoice', 'payment_id', 'invoice_id', string="Invoices", copy=False, readonly=True, help="""Technical field containing the invoices for which the payment has been generated. This does not especially correspond to the invoices reconciled with the payment, as it can have been generated first, and reconciled later""")
class detailcalculationline(models.Model):
	_name = 'detail.calculation.line'
	name = fields.Char('Name',store = True,related='invoice_id.number')
	payment_id = fields.Many2one('detail.calculation', string="Payment")
	#invoice = fields.Char('Invoice NO',store = True)
	invoice_amount = fields.Char('Invoice Amount',store = True)
	invoice_id = fields.Many2one('account.invoice', string="Invoice")
	invoice = fields.Char(store = True, string="Invoice Number")
	collection_amount = fields.Monetary('Collection Amount',store = True)
	currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
	collectio_date = fields.Date('Collection Date',store = True)
	date_of_deposite = fields.Date('Date Of Deposit',store = True)
	user_id = fields.Many2one('res.users',string = 'Sale Person')
	z_payment_method = fields.Many2one('custom.fields',string='Payment Method',store=True )
	refference = fields.Many2one('account.payment','Reference')
	z_state = fields.Char('Accounting Status',store=True,default='Open')
	z_payment_ref = fields.Char(string='Pay ref')
	z_seq = fields.Char(string='Collection Reference')
	z_name = fields.Char(string='Collection Reference')
	z_partner_id = fields.Many2one('res.partner',string='Customer')
	z_reference = fields.Char('Ref/Voucher No')
