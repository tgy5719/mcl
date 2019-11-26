# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import ValidationError

class AccountAnalyticAccount(models.Model):
	_inherit = 'account.analytic.account'

	z_analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')