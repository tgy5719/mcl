# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil import relativedelta
from itertools import groupby
from operator import itemgetter

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_round, float_is_zero

PROCUREMENT_PRIORITIES = [('0', 'Not urgent'), ('1', 'Normal'), ('2', 'Urgent'), ('3', 'Very Urgent')]


class StockMove(models.Model):
    _inherit = "stock.move"

    z_price_unit = fields.Float(string="Price Unit",store=True,track_visibility='onchange',compute="compute_price_unit")
    z_tax_id = fields.Many2many('account.tax','z_tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    currency_id = fields.Many2one(related='company_id.currency_id', store=True, string='Currency', readonly=True)
    
    z_price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    z_price_tax = fields.Float(compute='_compute_amount', string='Total Tax', readonly=True, store=True)
    z_price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)
    igst_intransit_account = fields.Many2one('account.account', string='IGST Intransit Account',related="z_tax_id.account_id")

    @api.multi
    @api.depends('product_id','product_uom_qty','quantity_done','picking_id.location_id','picking_id.location_dest_id')
    def compute_price_unit(self):
        for line in self:
            if line.product_id.z_transfer_price > 0:
                line.z_price_unit = line.product_id.z_transfer_price
                if line.location_id.z_internal_transfer_bool == True:
                    line.z_tax_id = False
                    line.z_tax_id = line.product_id.z_supplier_taxes_id.ids
                if line.location_dest_id.z_internal_transfer_bool == True:
                    line.z_tax_id = False
                    line.z_tax_id = line.product_id.z_taxes_id.ids
            else:
                line.z_price_unit = line.product_id.standard_price
                if line.location_id.z_internal_transfer_bool == True:
                    line.z_tax_id = False
                    line.z_tax_id = line.product_id.z_supplier_taxes_id.ids
                if line.location_dest_id.z_internal_transfer_bool == True:
                    line.z_tax_id = False
                    line.z_tax_id = line.product_id.z_taxes_id.ids

    @api.multi
    def _get_accounting_data_for_valuation(self):
        """ Return the accounts and journal to use to post Journal Entries for
        the real-time valuation of the quant. """
        self.ensure_one()
        accounts_data = self.product_id.product_tmpl_id.get_product_accounts()

        if self.location_id.valuation_out_account_id:
            acc_src = self.location_id.valuation_out_account_id.id
        else:
            if self.location_id.z_internal_transfer_bool == True and self.picking_type_id.z_stock_transfer == True:
                acc_src = accounts_data['transfer_account'].id
            elif self.location_id.z_internal_transfer_bool == False and self.picking_type_id.z_stock_transfer == True:
                acc_src = accounts_data['transfer_account'].id
            else:
                acc_src = accounts_data['stock_input'].id

        if self.location_dest_id.valuation_in_account_id:
            acc_dest = self.location_dest_id.valuation_in_account_id.id
        else:
            if self.location_dest_id.z_internal_transfer_bool == True and self.picking_type_id.z_stock_transfer == True:
                acc_dest = accounts_data['transfer_account'].id
            elif self.location_dest_id.z_internal_transfer_bool == False and self.picking_type_id.z_stock_transfer == True:
                acc_dest = accounts_data['transfer_account'].id
            else:
                acc_dest = accounts_data['stock_output'].id

        acc_valuation = accounts_data.get('stock_valuation', False)
        if acc_valuation:
            acc_valuation = acc_valuation.id
        if not accounts_data.get('stock_journal', False):
            raise UserError(_('You don\'t have any stock journal defined on your product category, check if you have installed a chart of accounts.'))
        if not acc_src:
            raise UserError(_('Cannot find a stock input account for the product %s. You must define one on the product category, or on the location, before processing this operation.') % (self.product_id.display_name))
        if not acc_dest:
            raise UserError(_('Cannot find a stock output account for the product %s. You must define one on the product category, or on the location, before processing this operation.') % (self.product_id.display_name))
        if not acc_valuation:
            raise UserError(_('You don\'t have any stock valuation account defined on your product category. You must define one before processing this operation.'))
        if self.location_dest_id.z_internal_transfer_bool == True and self.picking_type_id.z_stock_transfer == True:
            journal_id = accounts_data['transfer_journal'].id
        elif self.location_dest_id.z_internal_transfer_bool == False and self.picking_type_id.z_stock_transfer == True:
            journal_id = accounts_data['transfer_journal'].id
        else:
            journal_id = accounts_data['stock_journal'].id
        return journal_id, acc_src, acc_dest, acc_valuation


    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id):
        """
        Generate the account.move.line values to post to track the stock valuation difference due to the
        processing of the given quant.
        """
        self.ensure_one()

        if self.picking_id.picking_type_id.z_stock_transfer == True:
            if self.product_id.categ_id.z_transfer_price_bool == True:
                valuation_amount = self.product_id.z_transfer_price * self.quantity_done
            else:
                if self._context.get('force_valuation_amount'):
                    valuation_amount = self._context.get('force_valuation_amount')
                else:
                    valuation_amount = cost
        else:
            if self._context.get('force_valuation_amount'):
                valuation_amount = self._context.get('force_valuation_amount')
            else:
                valuation_amount = cost

        # the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
        # the company currency... so we need to use round() before creating the accounting entries.
        debit_value = self.company_id.currency_id.round(valuation_amount)

        # check that all data is correct
        if self.company_id.currency_id.is_zero(debit_value):
            raise UserError(_("The cost of %s is currently equal to 0. Change the cost or the configuration of your product to avoid an incorrect valuation.") % (self.product_id.display_name,))
        credit_value = debit_value


        valuation_partner_id = self._get_partner_id_for_valuation_lines()
        res = [(0, 0, line_vals) for line_vals in self._generate_valuation_lines_data(valuation_partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id).values()]

        return res

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id):
        # This method returns a dictonary to provide an easy extension hook to modify the valuation lines (see purchase for an example)
        self.ensure_one()

        if self._context.get('forced_ref'):
            ref = self._context['forced_ref']
        else:
            ref = self.picking_id.name

        analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in self.z_analytic_tag_ids]

        if self.picking_id.z_interstate_bool == True and self.picking_id.picking_type_id.z_stock_transfer == True:
            if self.picking_id.location_dest_id.z_internal_transfer_bool == True:
                debit_line_vals = {
                    'name': self.name,
                    'product_id': self.product_id.id,
                    'quantity': qty,
                    'product_uom_id': self.product_id.uom_id.id,
                    'ref': ref,
                    'partner_id': partner_id,
                    'debit': debit_value + self.z_price_tax if debit_value > 0 else 0,
                    'credit': -debit_value if debit_value < 0 else 0,
                    'account_id': debit_account_id,
                    'analytic_tag_ids':analytic_tag_ids,
                    #need to add analytic account id
                }
                
                credit_line_vals = {
                    'name': self.name,
                    'product_id': self.product_id.id,
                    'quantity': qty,
                    'product_uom_id': self.product_id.uom_id.id,
                    'ref': ref,
                    'partner_id': partner_id,
                    'credit': credit_value if credit_value > 0 else 0,
                    'debit': -credit_value if credit_value < 0 else 0,
                    'account_id': credit_account_id,
                    'analytic_tag_ids':analytic_tag_ids,
                    #need to add analytic account id
                }
                igst_line_val = {
                    'name': self.name,
                    'product_id': self.product_id.id,
                    'quantity': qty,
                    'product_uom_id': self.product_id.uom_id.id,
                    'ref': ref,
                    'partner_id': partner_id,
                    'debit': 0,
                    'credit': self.z_price_tax,
                    'account_id': self.igst_intransit_account.id,
                    'analytic_tag_ids':analytic_tag_ids,
                    #need to add analytic account id
                }
            if self.picking_id.location_id.z_internal_transfer_bool == True:
                debit_line_vals = {
                    'name': self.name,
                    'product_id': self.product_id.id,
                    'quantity': qty,
                    'product_uom_id': self.product_id.uom_id.id,
                    'ref': ref,
                    'partner_id': partner_id,
                    'debit': debit_value if debit_value > 0 else 0,
                    'credit': -debit_value if debit_value < 0 else 0,
                    'account_id': debit_account_id,
                    'analytic_tag_ids':analytic_tag_ids,
                    #need to add analytic account id
                }
                credit_line_vals = {
                    'name': self.name,
                    'product_id': self.product_id.id,
                    'quantity': qty,
                    'product_uom_id': self.product_id.uom_id.id,
                    'ref': ref,
                    'partner_id': partner_id,
                    'credit': credit_value + self.z_price_tax if credit_value > 0 else 0,
                    'debit': -credit_value if credit_value < 0 else 0,
                    'account_id': credit_account_id,
                    'analytic_tag_ids':analytic_tag_ids,
                    #need to add analytic account id
                }
                igst_line_val = {
                    'name': self.name,
                    'product_id': self.product_id.id,
                    'quantity': qty,
                    'product_uom_id': self.product_id.uom_id.id,
                    'ref': ref,
                    'partner_id': partner_id,
                    'debit': self.z_price_tax,
                    'credit': 0,
                    'account_id': self.igst_intransit_account.id,
                    'analytic_tag_ids':analytic_tag_ids,
                    #need to add analytic account id
                }
        elif self.picking_id.z_interstate_bool == False and self.picking_id.picking_type_id.z_stock_transfer == True:
            if self.picking_id.location_dest_id.z_internal_transfer_bool == True:
                debit_line_vals = {
                    'name': self.name,
                    'product_id': self.product_id.id,
                    'quantity': qty,
                    'product_uom_id': self.product_id.uom_id.id,
                    'ref': ref,
                    'partner_id': partner_id,
                    'debit': debit_value if debit_value > 0 else 0,
                    'credit': -debit_value if debit_value < 0 else 0,
                    'account_id': debit_account_id,
                    'analytic_tag_ids':analytic_tag_ids,
                    #need to add analytic account id
                }
                
                credit_line_vals = {
                    'name': self.name,
                    'product_id': self.product_id.id,
                    'quantity': qty,
                    'product_uom_id': self.product_id.uom_id.id,
                    'ref': ref,
                    'partner_id': partner_id,
                    'credit': credit_value if credit_value > 0 else 0,
                    'debit': -credit_value if credit_value < 0 else 0,
                    'account_id': credit_account_id,
                    'analytic_tag_ids':analytic_tag_ids,
                    #need to add analytic account id
                }
            if self.picking_id.location_id.z_internal_transfer_bool == True:
                debit_line_vals = {
                    'name': self.name,
                    'product_id': self.product_id.id,
                    'quantity': qty,
                    'product_uom_id': self.product_id.uom_id.id,
                    'ref': ref,
                    'partner_id': partner_id,
                    'debit': debit_value if debit_value > 0 else 0,
                    'credit': -debit_value if debit_value < 0 else 0,
                    'account_id': debit_account_id,
                    'analytic_tag_ids':analytic_tag_ids,
                    #need to add analytic account id
                }
                credit_line_vals = {
                    'name': self.name,
                    'product_id': self.product_id.id,
                    'quantity': qty,
                    'product_uom_id': self.product_id.uom_id.id,
                    'ref': ref,
                    'partner_id': partner_id,
                    'credit': credit_value if credit_value > 0 else 0,
                    'debit': -credit_value if credit_value < 0 else 0,
                    'account_id': credit_account_id,
                    'analytic_tag_ids':analytic_tag_ids,
                    #need to add analytic account id
                }
           
        else:
            debit_line_vals = {
            'name': self.name,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': ref,
            'partner_id': partner_id,
            'debit': debit_value if debit_value > 0 else 0,
            'credit': -debit_value if debit_value < 0 else 0,
            'account_id': debit_account_id,
            'analytic_tag_ids':analytic_tag_ids,
            #need to add analytic account id
            }
            credit_line_vals = {
            'name': self.name,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': ref,
            'partner_id': partner_id,
            'credit': credit_value if credit_value > 0 else 0,
            'debit': -credit_value if credit_value < 0 else 0,
            'account_id': credit_account_id,
            'analytic_tag_ids':analytic_tag_ids,
            #need to add analytic account id
            }

        #need to calculate gst and pass to the igst_line_val and make it flow to accounting entry.

        if self.picking_id.z_interstate_bool == True and self.picking_id.picking_type_id.z_stock_transfer == True:
            rslt = {'credit_line_vals': credit_line_vals, 'debit_line_vals': debit_line_vals,'igst_line_val': igst_line_val}
        elif self.picking_id.z_interstate_bool == False and self.picking_id.picking_type_id.z_stock_transfer == True:
            rslt = {'credit_line_vals': credit_line_vals, 'debit_line_vals': debit_line_vals}
        else:
            rslt = {'credit_line_vals': credit_line_vals, 'debit_line_vals': debit_line_vals}
        if credit_value != debit_value:
            # for supplier returns of product in average costing method, in anglo saxon mode
            diff_amount = debit_value - credit_value
            price_diff_account = self.product_id.property_account_creditor_price_difference

            if not price_diff_account:
                price_diff_account = self.product_id.categ_id.property_account_creditor_price_difference_categ
            if not price_diff_account:
                raise UserError(_('Configuration error. Please configure the price difference account on the product or its category to process this operation.'))

            rslt['price_diff_line_vals'] = {
                'name': self.name,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'ref': ref,
                'partner_id': partner_id,
                'credit': diff_amount > 0 and diff_amount or 0,
                'debit': diff_amount < 0 and -diff_amount or 0,
                'account_id': price_diff_account.id,
            }
        return rslt
#need to change the functionality to fetch transfer price if exists and work on GST
    def _run_valuation(self, quantity=None):
        self.ensure_one()
        if self._is_in():
            valued_move_lines = self.move_line_ids.filtered(lambda ml: not ml.location_id._should_be_valued() and ml.location_dest_id._should_be_valued() and not ml.owner_id)
            valued_quantity = 0
            for valued_move_line in valued_move_lines:
                valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, self.product_id.uom_id)

            # Note: we always compute the fifo `remaining_value` and `remaining_qty` fields no
            # matter which cost method is set, to ease the switching of cost method.
            vals = {}
            price_unit = self._get_price_unit()
            value = price_unit * (quantity or valued_quantity)
            vals = {
                'price_unit': price_unit,
                'value': value if quantity is None or not self.value else self.value,
                'remaining_value': value if quantity is None else self.remaining_value + value,
            }
            vals['remaining_qty'] = valued_quantity if quantity is None else self.remaining_qty + quantity

            if self.product_id.cost_method == 'standard':
                value = self.product_id.standard_price * (quantity or valued_quantity)
                vals.update({
                    'price_unit': self.product_id.standard_price,
                    'value': value if quantity is None or not self.value else self.value,
                })
            self.write(vals)
        elif self._is_out():
            valued_move_lines = self.move_line_ids.filtered(lambda ml: ml.location_id._should_be_valued() and not ml.location_dest_id._should_be_valued() and not ml.owner_id)
            valued_quantity = 0
            for valued_move_line in valued_move_lines:
                valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, self.product_id.uom_id)
            self.env['stock.move']._run_fifo(self, quantity=quantity)
            if self.product_id.cost_method in ['standard', 'average']:
                curr_rounding = self.company_id.currency_id.rounding
                value = -float_round(self.product_id.standard_price * (valued_quantity if quantity is None else quantity), precision_rounding=curr_rounding)
                self.write({
                    'value': value if quantity is None else self.value + value,
                    'price_unit': value / valued_quantity,
                })
        elif self._is_dropshipped() or self._is_dropshipped_returned():
            curr_rounding = self.company_id.currency_id.rounding
            if self.product_id.cost_method in ['fifo']:
                price_unit = self._get_price_unit()
                # see test_dropship_fifo_perpetual_anglosaxon_ordered
                self.product_id.standard_price = price_unit
            else:
                price_unit = self.product_id.standard_price
            value = float_round(self.product_qty * price_unit, precision_rounding=curr_rounding)
            # In move have a positive value, out move have a negative value, let's arbitrary say
            # dropship are positive.
            self.write({
                'value': value if self._is_dropshipped() else -value,
                'price_unit': price_unit if self._is_dropshipped() else -price_unit,
            })


    @api.depends('quantity_done', 'z_price_unit', 'z_tax_id')
    def _compute_amount(self):
        for line in self:
            price = line.z_price_unit
            taxes = line.z_tax_id.compute_all(price, line.currency_id, line.quantity_done, product=line.product_id, partner=line.picking_id.partner_id)
            line.update({
                'z_price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'z_price_total': taxes['total_included'],
                'z_price_subtotal': taxes['total_excluded'],
            })

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    z_price_unit = fields.Float(string="Price Unit",store=True,track_visibility='onchange',compute="compute_price_units")

    @api.multi
    @api.depends('product_id','qty_done','product_uom_id')
    def compute_price_units(self):
        for line in self:
            if line.product_id.z_transfer_price > 0:
                line.z_price_unit = line.product_id.z_transfer_price
                if line.location_id.z_internal_transfer_bool == True:
                    line.z_tax_id = False
                    line.z_tax_id = line.product_id.z_supplier_taxes_id.ids
                if line.location_dest_id.z_internal_transfer_bool == True:
                    line.z_tax_id = False
                    line.z_tax_id = line.product_id.z_taxes_id.ids
            else:
                line.z_price_unit = line.product_id.standard_price
                if line.location_id.z_internal_transfer_bool == True:
                    line.z_tax_id = False
                    line.z_tax_id = line.product_id.z_supplier_taxes_id.ids
                if line.location_dest_id.z_internal_transfer_bool == True:
                    line.z_tax_id = False
                    line.z_tax_id = line.product_id.z_taxes_id.ids