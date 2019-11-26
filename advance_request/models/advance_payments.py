from datetime import datetime,timedelta
from odoo import api, models, fields, _, exceptions
from dateutil.relativedelta import relativedelta
from time import strptime
from odoo.exceptions import UserError, ValidationError,Warning
from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError

class AdvancedPayments(models.Model):
	_inherit = "purchase.order"

	zadv_payment = fields.One2many('purchase.advance','zconn',string = "Advance Payments")
	zconnection = fields.One2many('account.payment','zrelation_for_po')

class PurchaseAdvancedPayments(models.Model):
	_name = 'purchase.advance'
	name = fields.Char(string='Sequence Number', readonly=True)
	zconn = fields.Many2one('purchase.order',string="Purchase Order",readonly=True)

	zvendor = fields.Many2one('res.partner',string="Vendor", compute='partner_method',store=True)
	zpo_name = fields.Char(string="Purchase Order",compute='po_method',store=True)
	zorder_value = fields.Float(string="Order Value", compute='order_method',readonly=True)
	zadvance_paid = fields.Float(string="Advance Paid")
	zdue_date = fields.Date(string="Due Date")
	zpurpose = fields.Many2one('purchase.simple', string = "Purpose")
	zstatus = fields.Selection(selection=[('open', 'Open'), ('close', 'Close')], string='Status',readonly=True,default='open')

	@api.multi
	@api.depends('zconn.partner_id')
	def partner_method(self):
		for variable_1 in self:
			variable_1.zvendor = variable_1.zconn.partner_id.id

	@api.depends('zconn.name')
	@api.multi
	def po_method(self):
		for variable_1 in self:
			variable_1.zpo_name = variable_1.zconn.name

	def order_method(self):
		for variable_1 in self:
			variable_1.zorder_value = variable_1.zconn.amount_total

	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('purchase.advance')
		return super(PurchaseAdvancedPayments, self).create(vals)

	@api.one
	@api.constrains('zorder_value', 'zadvance_paid')
	def adv_costraints(self):
		if self.zorder_value < self.zadvance_paid:
			raise ValidationError(_('"Order Value" must always be greater than "Advance Paid"'))

class Simple(models.Model):
	_name = 'purchase.simple'

	name = fields.Char(string="Name")

class account_payment(models.Model):
	_inherit = 'account.payment'
	zadvance_payments = fields.Many2one('purchase.advance',string='Advance Payments',domain="[('zstatus','=','open')]")
	zrelation_for_po = fields.Many2one('purchase.order')
	# zstatus_changer = fields.Boolean("Advance Paid",default=False)		

	@api.onchange('zadvance_payments')
	def method_onchange(self):
		for line_2 in self:
			line_2.communication = line_2.zadvance_payments.zpo_name
		for line_3 in self:
			line_3.amount = line_3.zadvance_payments.zadvance_paid
		for line_4 in self:
			line_4.partner_id = line_4.zadvance_payments.zvendor


	# @api.multi
	# def post(self):
	# 	for rec in self:
	# 		if rec.state != 'draft':
	# 			raise UserError(_("Only a draft payment can be posted."))
	# 		if any(inv.state != 'open' for inv in rec.invoice_ids):
	# 			raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))
	# 		if not rec.name:
	# 			if rec.payment_type == 'transfer':
	# 				sequence_code = 'account.payment.transfer'
	# 			else:
	# 				if rec.partner_type == 'customer':
	# 					if rec.payment_type == 'inbound':
	# 						sequence_code = 'account.payment.customer.invoice'
	# 					if rec.payment_type == 'outbound':
	# 						sequence_code = 'account.payment.customer.refund'
	# 				if rec.partner_type == 'supplier':
	# 					if rec.payment_type == 'inbound':
	# 						sequence_code = 'account.payment.supplier.refund'
	# 					if rec.payment_type == 'outbound':
	# 						sequence_code = 'account.payment.supplier.invoice'
	# 			rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
	# 			if not rec.name and rec.payment_type != 'transfer':
	# 				raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))
	# 			amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
	# 		move = rec._create_payment_entry(amount)
	# 		if rec.payment_type == 'transfer':
	# 			transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
	# 			transfer_debit_aml = rec._create_transfer_entry(amount)
	# 			(transfer_credit_aml + transfer_debit_aml).reconcile()
	# 		rec.write({'state': 'posted', 'move_name': move.name})

	# 		for line in self:
	# 			line.zstatus_changer = True
	# 		env_for_update = self.env['purchase.advance'].search([('id','=',self.zadvance_payments.id)])
	# 		for line_1 in env_for_update:
	# 			if line.zstatus_changer == True:
	# 				line_1.zstatus = 'close'
	# 	return True

