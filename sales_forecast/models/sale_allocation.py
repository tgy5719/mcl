# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import uuid
from itertools import groupby
from datetime import datetime, timedelta
from werkzeug.urls import url_encode
from odoo import api, fields, models, _,exceptions
from odoo.exceptions import UserError, AccessError
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp

class SaleAllocation(models.Model):
	_name = "sale.forecaste"
	z_period = fields.Selection([('Monthly','Monthly'),('weekly','weekly'),('Daily','Daily')],string ='Period',store = True)
	z_from_date = fields.Date(string = 'From Date',store = True)
	z_to_date = fields.Date(string = 'To Date',store = True)
	z_allow_linw = fields.One2many('sale.forecaste.line', 'z_allow_id', string='allow Lines', copy=True, auto_join=True)

	@api.constrains('z_to_date')
	def _check_date(self):
		for r in self:
			if r.z_to_date < self.z_from_date:
				raise models.ValidationError('To Date should be greater than From Date')
class SaleAllocationLine(models.Model):
	_name = "sale.forecaste.line"	
	z_allow_id = fields.Many2one('sale.forecaste',string = 'allow id',store = True)
	z_team_id = fields.Many2one('crm.team',string = 'Sale Team',store = True)
	z_user_id = fields.Many2one('res.users',string = 'Sale Person',store = True)
	z_product_id = fields.Many2one('product.product',string = 'Product',store = True)
	z_forecasted_qnty = fields.Float(string = 'Forecasted quantity',store = True)
	z_forecasted_val = fields.Float(string = 'Forecasted Value',store = True)

