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

class AccountInvoice(models.Model):
	_inherit = 'account.invoice'

	lc_no = fields.Many2one('account.letter.credit',string='LC NO',store=True,domain="['&',('release','=',True),('close','=',False),('strong','=','noo')]")
	lc_released = fields.Datetime(string = 'LC Release Date',compute = '_fetch_lc')
	@api.one
	@api.depends('lc_no')
	def _fetch_lc(self):
		self.lc_released = self.lc_no.issue_date
	
	def action_invoice_open(self):
		if self.lc_no:
			self.lc_no.value_utilised = self.lc_no.value_utilised + self.amount_total
		return super(AccountInvoice,self).action_invoice_open()
		
class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'
	lc_no = fields.Many2one('account.letter.credit',string='LC NO',store=True,domain="[('release','=',True),'&',('close','=',False),('strong','=','noo')]")


