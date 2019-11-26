# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp

# -*- coding: utf-8 -*-

import time
import math

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError



class AccountInvoiceTDS(models.Model):
    _name = "account.invoice.tds"
    _description = "Invoice TDS"
    _order = 'sequence'

    @api.depends('invoice_tds_id.invoice_line_ids')
    def _compute_base_amount_tds(self):
        tds_grouped = {}
        for invoice in self.mapped('invoice_tds_id'):
            tds_grouped[invoice.id] = invoice.get_tds_values()
        for tds_line in self:
            tds_line.base = 0.0
            if tds_line.tds_id:
                key = tds_line.tds_id.get_grouping_key_tds({
                    #need to check this group function for a specified class
                    'tds_id': tds_line.tds_id.id,
                    'account_id': tds_line.account_id.id,
                    'account_analytic_id': tds_line.account_analytic_id.id,
                })
                
    invoice_tds_id = fields.Many2one('account.invoice', string='Invoice TDS', ondelete='cascade', index=True)
    name = fields.Many2one('account.tds.mapping',string='TDS Description', required=True)
    tds_id = fields.Many2one('account.nod.confg.line', string='TDS', ondelete='restrict')
    account_id = fields.Many2one('account.account', string='TDS Account', required=True, domain=[('deprecated', '=', False)])
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic account')
    amount = fields.Monetary()
    amount_rounding = fields.Monetary()
    amount_total = fields.Monetary(string="Amount", compute='_compute_amount_total')
    manual = fields.Boolean(default=True)
    sequence = fields.Integer(help="Gives the sequence order when displaying a list of invoice tds.")
    company_id = fields.Many2one('res.company', string='Company', related='account_id.company_id', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', related='invoice_tds_id.currency_id', store=True, readonly=True)
    base = fields.Monetary(string='Base', compute='_compute_base_amount_tds', store=True)
    price_tds = fields.Monetary(string='TDS',
        store=True, readonly=True, help="Total amount without taxes")

    @api.depends('amount', 'amount_rounding')
    def _compute_amount_total(self):
        for tax_line in self:
            tax_line.amount_total = -tax_line.amount + tax_line.amount_rounding

