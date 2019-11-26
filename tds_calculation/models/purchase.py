# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP
from odoo.addons import decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    amount_tds = fields.Monetary(string='TDS on Base', store=True, readonly=True, compute='_amount_all', track_visibility='always')

    tds_percent = fields.Float(string="TDS %",digits=(16, 4))
    tds_percent_amount = fields.Float(string="TDS Amount",digits=(16, 4))

    non_pan_tds_percent = fields.Float(string="Non Pan TDS %",digits=(16, 4))
    non_pan_tds_percent_amount = fields.Float(string="Non Pan TDS Amount",digits=(16, 4))

    surcharge_percent = fields.Float(string="Surcharge %",digits=(16, 4))
    surcharge_percent_amount = fields.Float(string="Surcharge Amount",digits=(16, 4))

    e_cess_percent = fields.Float(string="E-Cess %",digits=(16, 4))
    e_cess_percent_amount = fields.Float(string="E-Cess amount",digits=(16, 4))

    she_cess_percent = fields.Float(string="She_cess %",digits=(16, 4))
    she_cess_percent_amount = fields.Float(string="She_Cess Amount",digits=(16, 4))
    
    @api.depends('order_line.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = amount_tds = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                amount_tds += line.price_tds
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_tds': order.currency_id.round(amount_tds),
                'amount_total': amount_untaxed + amount_tax - amount_tds,
            })


  

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    _description = 'Purchase Order Line'
    _order = 'order_id, sequence, id'

    tds_nod_id = fields.Many2many('account.nod.confg.line', string='TDS NOD',domain="[('partner_id', '=', partner_id)]")
    total_tds_amount = fields.Float(string="Total TDS amount", digits=(16, 4))
    price_tds = fields.Float(compute='_compute_amount', string='TDS', store=True)
    product_type = fields.Char(string='Product Type')

    tds_percent = fields.Float(string="TDS %",digits=(16, 4))
    tds_percent_amount = fields.Float(string="TDS Amount",digits=(16, 4))

    non_pan_tds_percent = fields.Float(string="Non Pan TDS %",digits=(16, 4))
    non_pan_tds_percent_amount = fields.Float(string="Non Pan TDS Amount",digits=(16, 4))

    surcharge_percent = fields.Float(string="Surcharge %",digits=(16, 4))
    surcharge_percent_amount = fields.Float(string="Surcharge Amount",digits=(16, 4))

    e_cess_percent = fields.Float(string="E-Cess %",digits=(16, 4))
    e_cess_percent_amount = fields.Float(string="E-Cess amount",digits=(16, 4))

    she_cess_percent = fields.Float(string="She_cess %",digits=(16, 4))
    she_cess_percent_amount = fields.Float(string="She_Cess Amount",digits=(16, 4))




    @api.depends('product_qty', 'price_unit', 'taxes_id','tds_nod_id')
    def _compute_amount(self):
        for line in self:
            tds = line.tds_nod_id.compute_all_tds(line.price_unit, line.order_id.currency_id, line.product_qty, product=line.product_id, partner=line.order_id.partner_id)
            taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_qty, product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_tds': line.total_tds_amount,
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
                'tds_percent': line.tds_percent,
                'tds_percent_amount':line.tds_percent_amount,
                'non_pan_tds_percent':line.non_pan_tds_percent,
                'non_pan_tds_percent_amount':line.non_pan_tds_percent_amount,
                'surcharge_percent':line.surcharge_percent,
                'surcharge_percent_amount':line.surcharge_percent_amount,
                'e_cess_percent':line.e_cess_percent,
                'e_cess_percent_amount':line.e_cess_percent_amount,
                'she_cess_percent':line.she_cess_percent,
                'she_cess_percent_amount':line.she_cess_percent_amount,

                #added to balance the total, because the subtotal value is being fetched all over the process
            })



    @api.onchange('product_id')
    def _onchange_product(self):
        self.product_type = "%s" % (self.product_id.type or "") 


    @api.onchange('product_qty','price_unit','tds_nod_id')
    def _onchange_partner(self):
        if self.tds_nod_id.name.concession_code.id == self.tds_nod_id.concession_code.id:
            if self.tds_nod_id.tds_threshold_applicable == True:
                if self.price_subtotal >= self.tds_nod_id.name.tds_group.tds_threshold_amount:
                    if self.tds_nod_id.name.non_pan_tds_req == True:
                        if self.tds_nod_id.partner_id.pan_no:
                            self.tds_percent_amount = 0
                            self.tds_percent = 0
                            self.non_pan_tds_percent = self.tds_nod_id.name.non_pan_tds # Fetching Non Pan TDS Percent Value
                            self.total_tds_amount = ((self.price_unit * self.product_qty) * self.non_pan_tds_percent /100) #calculating Non Pan TDS total Value
                            self.non_pan_tds_percent_amount = self.total_tds_amount #Non Pad Calculated amount
                            if self.tds_nod_id.name.surcharge > 0:
                                self.surcharge_percent = self.tds_nod_id.name.surcharge  # Fetching Surcharge Percent Value
                                self.surcharge_percent_amount = self.total_tds_amount * self.tds_nod_id.name.surcharge/100 #calculating surcharge amount
                                self.total_tds_amount = self.surcharge_percent_amount + self.total_tds_amount # adding surcharge to the total tds amount
                            if self.tds_nod_id.name.e_cess > 0:
                                if self.tds_nod_id.name.she_cess > 0:
                                    self.she_cess_percent = self.tds_nod_id.name.she_cess # Fetching She_Cess Percent Value
                                    self.e_cess_percent = self.tds_nod_id.name.e_cess # Fetching E_cess Percent Value
                                    self.she_cess_percent_amount = self.total_tds_amount * self.she_cess_percent/100 # calculating she cess amount
                                    self.e_cess_percent_amount = self.total_tds_amount * self.e_cess_percent/100 # Calculating ecess amount
                                    self.total_tds_amount = self.e_cess_percent_amount + self.she_cess_percent_amount + self.total_tds_amount # adding ecess and she_cess to total
                        else:
                            self.non_pan_tds_percent_amount = 0
                            self.non_pan_tds_percent = 0
                            self.tds_percent = self.tds_nod_id.name.tds # fetching tds percent
                            self.total_tds_amount = ((self.price_unit * self.product_qty) * self.tds_percent / 100)
                            self.tds_percent_amount = self.total_tds_amount
                            if self.tds_nod_id.name.surcharge > 0:
                                self.surcharge_percent = self.tds_nod_id.name.surcharge # Fetching Surcharge Percent Value
                                self.surcharge_percent_amount = self.total_tds_amount * self.tds_nod_id.name.surcharge/100 #calculating surcharge amount
                                self.total_tds_amount = self.surcharge_percent_amount + self.total_tds_amount # adding surcharge to the total tds amount
                            if self.tds_nod_id.name.e_cess > 0:
                                if self.tds_nod_id.name.she_cess > 0:
                                    self.she_cess_percent = self.tds_nod_id.name.she_cess # Fetching She_Cess Percent Value
                                    self.e_cess_percent = self.tds_nod_id.name.e_cess  # Fetching E_cess Percent Value
                                    self.she_cess_percent_amount = self.total_tds_amount * self.she_cess_percent/100 # calculating she cess amount
                                    self.e_cess_percent_amount = self.total_tds_amount * self.e_cess_percent/100 # Calculating ecess amount
                                    self.total_tds_amount = self.e_cess_percent_amount + self.she_cess_percent_amount + self.total_tds_amount # adding ecess and she_cess to total
                    else:
                        self.non_pan_tds_percent = 0
                        self.non_pan_tds_percent_amount = 0
                        self.tds_percent = self.tds_nod_id.name.tds  # fetching tds percent
                        self.total_tds_amount = ((self.price_unit * self.product_qty) * self.tds_percent / 100)
                        self.tds_percent_amount = self.total_tds_amount
                        if self.tds_nod_id.name.surcharge > 0:
                            self.surcharge_percent = self.tds_nod_id.name.surcharge  # Fetching Surcharge Percent Value
                            self.surcharge_percent_amount = self.total_tds_amount * self.tds_nod_id.name.surcharge/100 #calculating surcharge amount
                            self.total_tds_amount = self.surcharge_percent_amount + self.total_tds_amount # adding surcharge to the total tds amount
                        if self.tds_nod_id.name.e_cess > 0:
                            if self.tds_nod_id.name.she_cess > 0:
                                self.she_cess_percent = self.tds_nod_id.name.she_cess  # Fetching She_Cess Percent Value
                                self.e_cess_percent = self.tds_nod_id.name.e_cess  # Fetching E_cess Percent Value
                                self.she_cess_percent_amount = self.total_tds_amount * self.she_cess_percent/100 # calculating she cess amount
                                self.e_cess_percent_amount = self.total_tds_amount * self.e_cess_percent/100 # Calculating ecess amount
                                self.total_tds_amount = self.e_cess_percent_amount + self.she_cess_percent_amount + self.total_tds_amount # adding ecess and she_cess to total
            else:
                if self.tds_nod_id.name.non_pan_tds_req == True:
                    if self.tds_nod_id.partner_id.pan_no:
                        self.tds_percent_amount = 0
                        self.tds_percent = 0
                        self.non_pan_tds_percent = self.tds_nod_id.name.non_pan_tds  # Fetching Non Pan TDS Percent Value
                        self.total_tds_amount = ((self.price_unit * self.product_qty) * self.non_pan_tds_percent /100) #calculating Non Pan TDS total Value
                        self.non_pan_tds_percent_amount = self.total_tds_amount #Non Pad Calculated amount
                        if self.tds_nod_id.name.surcharge > 0:
                            self.surcharge_percent = self.tds_nod_id.name.surcharge  # Fetching Surcharge Percent Value
                            self.surcharge_percent_amount = self.total_tds_amount * self.tds_nod_id.name.surcharge/100 #calculating surcharge amount
                            self.total_tds_amount = self.surcharge_percent_amount + self.total_tds_amount # adding surcharge to the total tds amount
                        if self.tds_nod_id.name.e_cess > 0:
                            if self.tds_nod_id.name.she_cess > 0:
                                self.she_cess_percent = self.tds_nod_id.name.she_cess  # Fetching She_Cess Percent Value
                                self.e_cess_percent = self.tds_nod_id.name.e_cess  # Fetching E_cess Percent Value
                                self.she_cess_percent_amount = self.total_tds_amount * self.she_cess_percent/100 # calculating she cess amount
                                self.e_cess_percent_amount = self.total_tds_amount * self.e_cess_percent/100 # Calculating ecess amount
                                self.total_tds_amount = self.e_cess_percent_amount + self.she_cess_percent_amount + self.total_tds_amount # adding ecess and she_cess to total
                    else:
                        self.non_pan_tds_percent_amount = 0
                        self.non_pan_tds_percent = 0
                        self.tds_percent = self.tds_nod_id.name.tds  # fetching tds percent
                        self.total_tds_amount = ((self.price_unit * self.product_qty) * self.tds_percent / 100)
                        self.tds_percent_amount = self.total_tds_amount
                        if self.tds_nod_id.name.surcharge > 0:
                            self.surcharge_percent = self.tds_nod_id.name.surcharge  # Fetching Surcharge Percent Value
                            self.surcharge_percent_amount = self.total_tds_amount * self.tds_nod_id.name.surcharge/100 #calculating surcharge amount
                            self.total_tds_amount = self.surcharge_percent_amount + self.total_tds_amount # adding surcharge to the total tds amount
                        if self.tds_nod_id.name.e_cess > 0:
                            if self.tds_nod_id.name.she_cess > 0:
                                self.she_cess_percent = self.tds_nod_id.name.she_cess  # Fetching She_Cess Percent Value
                                self.e_cess_percent = self.tds_nod_id.name.e_cess  # Fetching E_cess Percent Value
                                self.she_cess_percent_amount = self.total_tds_amount * self.she_cess_percent/100 # calculating she cess amount
                                self.e_cess_percent_amount = self.total_tds_amount * self.e_cess_percent/100 # Calculating ecess amount
                                self.total_tds_amount = self.e_cess_percent_amount + self.she_cess_percent_amount + self.total_tds_amount # adding ecess and she_cess to total
                else:
                    self.non_pan_tds_percent = 0
                    self.non_pan_tds_percent_amount = 0
                    self.tds_percent = self.tds_nod_id.name.tds  # fetching tds percent
                    self.total_tds_amount = ((self.price_unit * self.product_qty) * self.tds_percent / 100)
                    self.tds_percent_amount = self.total_tds_amount
                    if self.tds_nod_id.name.surcharge > 0:
                        self.surcharge_percent = self.tds_nod_id.name.surcharge  # Fetching Surcharge Percent Value
                        self.surcharge_percent_amount = self.total_tds_amount * self.tds_nod_id.name.surcharge/100 #calculating surcharge amount
                        self.total_tds_amount = self.surcharge_percent_amount + self.total_tds_amount # adding surcharge to the total tds amount
                    if self.tds_nod_id.name.e_cess > 0:
                        if self.tds_nod_id.name.she_cess > 0:
                            self.she_cess_percent = self.tds_nod_id.name.she_cess  # Fetching She_Cess Percent Value
                            self.e_cess_percent = self.tds_nod_id.name.e_cess  # Fetching E_cess Percent Value
                            self.she_cess_percent_amount = self.total_tds_amount * self.she_cess_percent/100 # calculating she cess amount
                            self.e_cess_percent_amount = self.total_tds_amount * self.e_cess_percent/100 # Calculating ecess amount
                            self.total_tds_amount = self.e_cess_percent_amount + self.she_cess_percent_amount + self.total_tds_amount # adding ecess and she_cess to total
        else:
            self.total_tds_amount = 0




#need to calculate the amount based on the threshold limits, need to create new db and check the flow once

