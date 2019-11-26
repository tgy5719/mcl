# -*- coding: utf-8 -*-
from odoo.addons import decimal_precision as dp
from collections import namedtuple
import json
import time
from odoo.exceptions import UserError, ValidationError,Warning
from itertools import groupby
from odoo import api, fields, models,_,exceptions
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
from operator import itemgetter

class SaleOrder(models.Model):
	_inherit = "sale.order"

	z_journal = fields.Many2one('account.journal',string='Tax Journal',store=True)
	warehouse_id = fields.Many2one(
		'stock.warehouse', string='Warehouse',
        required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        compute="fetch_warehouse")

	@api.multi
	@api.depends('analytic_account_id','partner_id')
	def fetch_warehouse(self):
		for line in self:
			if line.analytic_account_id:
				company = self.env.user.company_id.id
				line.warehouse_id = line.analytic_account_id.z_warehouse.id
				line.z_journal = line.warehouse_id.z_journal
			else:
				company = self.env.user.company_id.id
				line.warehouse_id = self.env['stock.warehouse'].search([('company_id', '=', company)], limit=1)
				line.z_journal = line.warehouse_id.z_journal



