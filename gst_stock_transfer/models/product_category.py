# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

from odoo.addons import decimal_precision as dp

from odoo.tools import float_compare, pycompat


class ProductCategory(models.Model):
    _inherit = "product.category"

    z_transfer_price_bool = fields.Boolean(string="Enable Transfer Price Valuation",default=False)
    z_transfer_journal = fields.Many2one('account.journal',string="Transfer Journal")
    z_transfer_account = fields.Many2one('account.account',string="Intransit Account")