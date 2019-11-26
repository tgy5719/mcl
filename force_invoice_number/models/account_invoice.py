# -*- coding: utf-8 -*-

from collections import OrderedDict
import json
import re
import uuid
from functools import partial

from lxml import etree
from dateutil.relativedelta import relativedelta
from werkzeug.urls import url_encode

from odoo import api, exceptions, fields, models, _
from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, \
    pycompat, date_utils
from odoo.tools.misc import formatLang

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from odoo.addons import decimal_precision as dp
import logging


class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    number = fields.Char(related='move_id.name', store=True, readonly=True, copy=False, compute="apply_force_number")
    force_number = fields.Char(string='Force Invoice Number')

    @api.multi
    @api.depends('force_number')
    def apply_force_number(self):
        for line in self:
            if line.force_number:
                if line.reference:
                    new_ref = line.reference.split('/')
                    new_ref[0] = line.force_number
                    new_ref = new_ref[0]+'/'+new_ref[1]
                    line.move_id.write({'name':line.force_number,'ref':new_ref})
                    line.number = line.force_number
                    line.reference = new_ref