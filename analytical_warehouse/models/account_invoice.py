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

class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    z_journal = fields.Many2one('account.journal' , string = 'Tax Journal',store = True) 
    z_warehouse_id = fields.Many2one('stock.warehouse',string = 'Warehouse',store= True)
    z_analytic_account_id = fields.Many2one('account.analytic.account',string = 'Account Analytic',store = True)