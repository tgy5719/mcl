# -*- coding: utf-8 -*-

import time
from datetime import date
from collections import OrderedDict
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools.misc import formatLang, format_date
from odoo.tools import float_is_zero, float_compare
from odoo.tools.safe_eval import safe_eval
from odoo.addons import decimal_precision as dp
from lxml import etree

#----------------------------------------------------------
# Entries
#----------------------------------------------------------

class AccountMove(models.Model):
	_inherit = "account.move"
	_description = "Journal Entries"
	_order = 'date desc, id desc'

	z_analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account',help="The analytic account related to a Invoice.")


	@api.multi
	def post(self,invoice=False):
		for line in self:
			for lines in line.line_ids:
				if line.z_analytic_account_id:
					lines.analytic_account_id = line.z_analytic_account_id.id
		return super(AccountMove,self).post()
	
class AccountMoveLine(models.Model):
	_inherit = "account.move.line"

	analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
