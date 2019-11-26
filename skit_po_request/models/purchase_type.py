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

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
_STATES = [
  ('draft', 'Draft'),
  ('to_approve', 'To be approved'),
  ('approved', 'Approved'),
  ('rejected', 'Rejected')
]


class PurchaseRequestLine(models.Model):
  _name = "purchase.type"
  name = fields.Char('Name',store = True)
