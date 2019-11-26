import uuid
from datetime import datetime
from urllib import request, parse
from itertools import groupby
from datetime import datetime, timedelta
from werkzeug.urls import url_encode

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT

from odoo.tools.misc import formatLang

from odoo.addons import decimal_precision as dp

class Accountletter(models.Model):
	_name = 'account.letter.credit'
	_description = 'account letter credit'

	name = fields.Char(string='No',store = True,readonly = True)
	#fields added by deekshith
	z_journal_id = fields.Many2one('account.journal',string="Journal",required=True)
	z_account_id = fields.Many2one('account.account',string="GL Account")
	z_vendor_id = fields.Many2one('res.partner',string="LC Master Card")
	z_bool = fields.Boolean(string="LC CheckBox",track_visibility='always',compute="_check_done_journal")

	#addition of new fields done
	lc_no = fields.Char(string = 'LC No',store = True)
	description = fields.Text(string = 'Description',store = True)
	transaction_type = fields.Selection([
		('Purchase', 'Purchase'),
		('Sale', 'Sale'),
		], string='Transaction Type', default='Purchase')
	issued_receive = fields.Many2one('res.partner',string='Issued To/Received From ',store = True)
	issue_date = fields.Datetime(string ='Date Of Issue',store = True,required=True)
	expiry_data = fields.Datetime(string ='Date Of Expiry',store=True,required=True)
	type_lc = fields.Selection([
		('Foriegn', 'Foriegn'),
		('Inland', 'Inland'),
		], string='Type Of LC', default='Foriegn')
	currency = fields.Many2one('res.currency',string = 'Currency Code',store = True)
	exchange = fields.Float(string = 'Exchange Rate',store = True,default = 1)
	lc_value = fields.Float(string = 'LC Value',store = True) 
	release = fields.Boolean(string = 'Released',store = True)
	close = fields.Boolean(string = 'Closed',store = True)
	lc_req_date = fields.Datetime(string = 'LC Requested Date',store = True)
	lc_recv_date = fields.Datetime(string = 'LC Receiving Date',store = True)
	iss_bank = fields.Many2one('res.bank',string = 'Issuing Bank',store = True)
	recv_bank = fields.Many2one('res.bank',string = 'Receiving Bank',store = True)
	value_utilised = fields.Float(string = 'Value Utilized',store = True)
	remaining_amt = fields.Float(string = 'Remaining Amount',store = True,compute = '_remain')
	lc_val_lcy = fields.Float(string = 'LC Value LCY',store = True,compute = '_real')
	currency_function = fields.Char(string = 'Function',store =True,compute='_fetch_currency')
	strict = fields.Char(string = 'filter',store = True)
	strong = fields.Char(store = True,string = 'Strong',compute = '_strong')
	state = fields.Selection([
		('draft', 'Open'),
		('deliv', 'Released'),
		('cancel', 'Closed'),
		], string='Status',readonly=True, select=True, help='Workflow stages', default='draft')
	company_id = fields.Many2one('res.company', string='Company',
    default=lambda self: self.env['res.company']._company_default_get('account.letter.credit'))
	@api.one
	@api.depends('lc_val_lcy','value_utilised')
	def _remain(self):
		self.remaining_amt = (self.lc_val_lcy) - (self.value_utilised)
	@api.one
	@api.depends('exchange','lc_value')
	def _real(self):
		self.lc_val_lcy = (self.exchange)*(self.lc_value)
	@api.one
	@api.depends('company_id')
	def _fetch_currency(self):
		self.currency_function = self.company_id.currency_id.name
	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('account.letter.credit1')
		rec = super(Accountletter, self).create(vals)
		rec.state = 'deliv'
		return rec	
		
	@api.onchange('release','state','close')
	def _release(self):
		if self.release == True:
			self.state = 'deliv'
		'''if self.close == True:
			self.state = 'cancel'''
	@api.onchange('transaction_type')
	def onchange_use_insurance(self):		
		res = {}
		if self.transaction_type == 'Purchase':
			res['domain'] = {'issued_receive': [('supplier', '=',True)]}
		elif self.transaction_type == 'Sale':
			res['domain'] = {'issued_receive': [('customer', '=',True)]}
		else :
			res['domain'] = {'issued_receive': [('supplier', '=',True)]}
		return res
	@api.constrains('expiry_data')
	def _check_release_date1(self):
		for r in self:
			if r.expiry_data < self.issue_date:
				raise models.ValidationError('Expiry date should be greater than Issue date')
	@api.constrains('lc_val_lcy')
	def _check_release_date2(self):
		for r in self:
			if r.lc_val_lcy <= 0.00:
				raise models.ValidationError('Available LC Amount is Less Then What iS Required')
	@api.constrains('lc_recv_date')
	def _check_release_date3(self):
		for r in self:
			if r.lc_recv_date < self.lc_req_date:
				raise models.ValidationError('LC Receving Date Should Select After LC Request Date')
	@api.onchange('currency')
	def onchange_currency(self):
		for line in self:
			if self.currency.name == self.currency_function:
				line.update({'strict':'true'})
			if self.currency.name != self.currency_function:
				line.update({'strict':'false'})

	@api.multi
	def Report_On_Sale(self):
		return self.env.ref('letter_of_credit.report_lc_report').report_action(self)

	@api.onchange('close')
	def _concate(self):
		return {'value':{'close':self.close,'release':False}}
	@api.onchange('release')
	def _concate2(self):
		return {'value':{'release':self.release,'close':False}}
	@api.one
	@api.depends('remaining_amt')
	def _strong(self):
		if self.remaining_amt <= 0:
			self.strong = "yess!"
		if self.remaining_amt > 0:
			self.strong = "noo"
	@api.one
	def closed(self):
		self.write({
			'state': 'cancel',
			'close':'True',
			})

	def post_entries(self):
		vals = {
		'ref': self.lc_no,
		'journal_id':self.z_journal_id.id,
		'z_lc_no':self.id,
		'z_ext_doc':self.lc_value
		}
		credit_obj = self.env['account.move'].create(vals)
		credit_move_lines_obj = self.env['account.move.line']
		all_lines =[]
		move_line = {}
		move_credit_line ={}
		move_credit_line_vendor ={}
		move_line = {
		'account_id': self.issued_receive.property_account_payable_id.id,
		'partner_id': self.issued_receive.id,
		'move_id': credit_obj.id,
		}
		if self.z_account_id:
			move_credit_line = {
			'account_id': self.z_account_id.id,
			'move_id': credit_obj.id,
			}
			credit_move_lines_obj.create(move_credit_line)
		if self.z_vendor_id:
			move_credit_line_vendor = {
			'account_id': self.z_vendor_id.property_account_payable_id.id,
			'partner_id': self.z_vendor_id.id,
			'move_id': credit_obj.id,
			}
			credit_move_lines_obj.create(move_credit_line_vendor)
		credit_move_lines_obj.create(move_line)

	
	@api.onchange('z_vendor_id')
	def account_mapping_vendor(self):
		if self.z_vendor_id:
			self.z_account_id = False

	@api.onchange('z_account_id')
	def account_mapping_account(self):
		if self.z_account_id:
			self.z_vendor_id = False

	@api.multi
	@api.depends('z_journal_id')
	def _check_done_journal(self):
		for line in self:
			journal_ids = self.env['account.move'].search([('z_lc_no', '=', line.id)])
			if journal_ids:
				for move in journal_ids:
					if move.state == "draft":
						line.z_bool = True
	
