# -*- coding: utf-8 -*-

from odoo import api, fields, models,exceptions,_
from odoo.addons import decimal_precision as dp
from datetime import datetime
import odoo.addons.decimal_precision as dp
from odoo.exceptions import Warning
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare
import time
import math
import datetime
from datetime import datetime

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _get_line_numbers(self):
        line_num = 0
        for l in self:
            line_num = line_num + 1
            l.z_line_no = line_num   

    z_line_no = fields.Integer(compute='_get_line_numbers', string='Sl No')

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.multi
    def _get_line_numbers(self):
        line_num = 0
        for l in self:
            line_num = line_num + 1
            l.z_line_no = line_num   

    z_line_no = fields.Integer(compute='_get_line_numbers', string='Sl No')

