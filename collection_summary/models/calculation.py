from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
class salecalculation(models.Model):
	_name = 'sale.calculation'
	name = fields.Char('Name',related = 'user_id.name',store = True)
	user_id = fields.Many2one('res.users',string = 'Sale Person',readonly=True)
	invoice_lines = fields.One2many('sale.calculation.line', 'payment_id', string="Invoice Line")
	
	invoice_ids = fields.Many2many('account.invoice', 'payment_id', 'invoice_id', string="Invoices", copy=False, readonly=True, help="""Technical field containing the invoices for which the payment has been generated. This does not especially correspond to the invoices reconciled with the payment, as it can have been generated first, and reconciled later""")
	@api.multi
	def update_invoice_lines(self):
		for inv in self.invoice_lines:
			inv.open_amount = inv.invoice_id.residual 
		self.onchange_partner_id()
	@api.multi
	def onchange_partner_id(self):
		if self.user_id:
			vals = {}
			line = [(6, 0, [])]
			invoice_ids = []
			invoice_ids = self.env['account.invoice'].search([('user_id', 'in', [self.user_id.id]),('state', '=','open'),('type','=', 'out_invoice')])
			for inv in invoice_ids[::-1]:
				vals = {
					'invoice_id': inv.id,
					}
				line.append((0, 0, vals))
			self.invoice_lines = line
	@api.model
	def create(self,vals):
		res = super(salecalculation,self).create(vals)
		if vals.get('invoice_lines'):
			res.invoice_ids = res.invoice_lines.mapped('invoice_id')
		return res

	@api.multi
	def write(self,vals):
		res = super(salecalculation,self).write(vals)
		#vals.get('update_sale_detail_calculation')
		if vals.get('invoice_lines'):
			self.invoice_ids = self.invoice_lines.mapped('invoice_id')
		return res
	@api.multi
	def update_sale_detail_calculation(self):
		for line in self.invoice_lines:
			line.z_seq = self.env['ir.sequence'].next_by_code('calculation.sequence')
			if line.date_of_deposite < line.collectio_date:
				raise models.ValidationError('Date Of Deposit Should be Greater Then Date Of Collection')
		indent_count = self.env['detail.calculation']
		if not indent_count:
			vals = {
			'name':self.name,
			'user_id':self.user_id.id,
			}
			sale_obj = self.env['detail.calculation'].create(vals)
			move_lines_obj = self.env['detail.calculation.line']
			for line in self.invoice_lines:
				move_line = {}
				move_line = {
					'payment_id':sale_obj.id,
					'z_name':line.z_name,
					'user_id':line.user_id.id,
					'invoice':line.invoice,
					'z_payment_method':line.z_payment_method.id,
					'invoice_amount':line.invoice_amount,
					'collection_amount':line.collection_amount,
					'collectio_date':line.collectio_date,
					'date_of_deposite':line.date_of_deposite,
					'refference':line.refference.id,
					'z_state':line.z_state,
					'z_payment_ref':line.z_payment_ref,
					'z_seq':line.z_seq,
					'z_partner_id':line.partner_id.id,
					'z_reference':line.z_reference,
					}
				move_lines_obj.create(move_line)
				line.unlink()
		return True
	
class salecalculationline(models.Model):
	_name = 'sale.calculation.line'
	name = fields.Char('Name',store = True,related='invoice_id.number')
	payment_id = fields.Many2one('sale.calculation', string="Payment")
	#invoice = fields.Char('Invoice NO',store = True)
	invoice_amount = fields.Float('Invoice Amount',store = True,compute='_get_invoice_data')
	invoice_id = fields.Many2one('account.invoice', string="Invoice")
	invoice = fields.Char(related='invoice_id.number', string="Invoice Number",store=True)
	collection_amount = fields.Monetary('Collection Amount',store = True)
	currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
	collectio_date = fields.Date('Collection Date',store = True)
	date_of_deposite = fields.Date('Date Of Deposit',store = True)
	user_id = fields.Many2one('res.users',string = 'Sale Person',related = 'payment_id.user_id')
	z_payment_method = fields.Many2one('custom.fields',string='Payment Method')
	refference = fields.Many2one('account.payment','Reference')
	partner_id = fields.Many2one('res.partner', string='Customer',related='invoice_id.partner_id')
	z_name = fields.Char(string='Order line Reference',compute='_get_seq_data')
	z_seq = fields.Char(string='Collection Reference')
	z_payment_ref = fields.Char(string='Pay ref',related='invoice_id.reference')
	z_state = fields.Char('Accounting Status',default='Open')
	z_amount_due = fields.Float('Amount Due',compute='_amount_amt_due')
	z_amount_due_tot = fields.Float('Collection Amount Due',compute='_amount_amt_due')
	z_reference = fields.Char('Ref/Voucher No')
	#cal_id = fields.Many2one('payment.invoice.line', string="payment")

	@api.multi
	@api.depends('invoice_id')
	def _get_invoice_data(self):
		for data in self:
			invoice_id = data.invoice_id
			data.invoice_amount = invoice_id.amount_total 

	# @api.model
	# def create(self, vals):
	# 	vals['name'] = self.env['ir.sequence'].next_by_code('calculation.sequence')
	# 	result = super(salecalculationline, self).create(vals)
	# 	return result
	# @api.multi
	@api.depends('z_seq','invoice')
	def _get_seq_data(self):
		for data in self:
			if data.z_seq and data.invoice:
				data.z_name = str(data.invoice)+'-'+ str(data.z_seq)
	
	@api.multi
	@api.depends('collection_amount','invoice')
	def _amount_amt_due(self):
		for due in self:
			tot = 0
			dom = self.env['detail.calculation.line'].search([('invoice','=',due.invoice)])
			for d in dom:
				tot = tot + d.collection_amount
				due.z_amount_due = tot
				due.z_amount_due_tot = due.invoice_amount - due.z_amount_due
           