# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round, float_is_zero, pycompat

import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', help="The analytic account related to a sales order.")
    z_analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account for validation purpose', help="The analytic account related to a sales order.",compute="check_analytic_account")
    z_disp_fetch_button = fields.Boolean(string="Display Fetch Button",compute="_compute_move_analytic_tags")
    z_disp_fetch_tags = fields.Boolean(string="Display Tags",default=True)

    @api.multi
    @api.depends('sale_id')
    def _compute_move_analytic_tags(self):
        for line in self:
            if line.sale_id:
                line.z_disp_fetch_button = True
            else:
                line.z_disp_fetch_button = False

    @api.multi
    @api.depends('sale_id','purchase_id')
    def check_analytic_account(self):
        for line in self:
            if line.sale_id:
                line.z_analytic_account_id = line.sale_id.analytic_account_id.id
            if line.purchase_id:
                line.z_analytic_account_id = line.purchase_id.z_account_analytic_id.id

    @api.multi
    @api.onchange('analytic_account_id')
    def onchange_product_id_analytic_tags_shipment(self):
        for lines in self:
            for line in lines.move_ids_without_package:
                if not lines.sale_id:
                    rec = self.env['account.analytic.account'].search([('id', '=', lines.analytic_account_id.id)])
                    line.z_analytic_tag_ids = False
                    line.z_analytic_tag_ids = rec.z_analytic_tag_ids.ids

    @api.multi
    def button_validate(self):
        if not self.analytic_account_id:
            raise UserError(_('Kindly select the Analytic Account before validating this Transfer'))
        if self.sale_id or self.purchase_id:
            if self.analytic_account_id != self.z_analytic_account_id:
                raise UserError(_('Kindly check the Analytic Account in the shipment and also in the respective order. Analytic Account Mismatched..!!!!'))

        if self.sale_id:
            if self.z_disp_fetch_button == True and self.z_disp_fetch_tags == True:
                raise UserError(_('Kindly Fetch the Analytic Tags before Validating the Delivery'))
            for stock in self:
                for move in stock.move_ids_without_package:
                    for line in stock.sale_id:
                        for lines in line.order_line:
                            if move.product_id.id == lines.product_id.id:
                                lines.analytic_tag_ids = move.z_analytic_tag_ids.ids
        return super(StockPicking, self).button_validate()

    #this function works fine if detailed operation is enabled
    #but its not good manual selection of analytical tags which does not have sale id.
    '''@api.onchange('move_line_ids_without_package')
    def change_analytical_tagss(self):
        for picking in self:
            for move in picking.move_ids_without_package:
                for line in picking.move_line_ids_without_package:
                    if move.product_id.id == line.product_id.id:
                        move.z_analytic_tag_ids = line.z_analytic_tag_ids.ids'''

    def change_analytical_tags(self):
        for move in self.move_ids_without_package:
            stock_line = self.env['stock.move.line'].search([('picking_id', '=', move.picking_id.id)])
            if stock_line:
                for line in stock_line:
                    for lines in stock_line:
                        if move.product_id.id == line.product_id.id:
                            if lines.lot_id.id == line.lot_id.id:
                                if line.z_analytic_tag_ids != lines.z_analytic_tag_ids:
                                    raise UserError(_('Analytic tag mismatched'))
                                else:
                                    move.z_analytic_tag_ids = line.z_analytic_tag_ids.ids
                                    self.z_disp_fetch_tags = False


class StockMove(models.Model):
    _inherit = 'stock.move'

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', help="The analytic account related to a sales order.")

    #moving value from stock inventory line
    z_analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    z_num = fields.Char(string="Check")


    
    def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id):
        self.ensure_one()
        AccountMove = self.env['account.move']
        quantity = self.env.context.get('forced_quantity', self.product_qty)
        quantity = quantity if self._is_in() else -1 * quantity

        # Make an informative `ref` on the created account move to differentiate between classic
        # movements, vacuum and edition of past moves.
        ref = self.picking_id.name
        if self.env.context.get('force_valuation_amount'):
            if self.env.context.get('forced_quantity') == 0:
                ref = 'Revaluation of %s (negative inventory)' % ref
            elif self.env.context.get('forced_quantity') is not None:
                ref = 'Correction of %s (modification of past move)' % ref

        move_lines = self.with_context(forced_ref=ref)._prepare_account_move_line(quantity, abs(self.value), credit_account_id, debit_account_id)
        if move_lines:
            date = self._context.get('force_period_date', fields.Date.context_today(self))
            if self.picking_id:
                #value being passed from stock picking/ transfers to journal entries
                new_account_move = AccountMove.sudo().create({
                    'journal_id': journal_id,
                    'line_ids': move_lines,
                    'date': date,
                    'ref': ref,
                    'stock_move_id': self.id,
                    'z_analytic_account_id':self.picking_id.analytic_account_id.id,
                })
                new_account_move.post()
            else:
                #value being passed from stock inventory to journal entries
                new_account_move = AccountMove.sudo().create({
                    'journal_id': journal_id,
                    'line_ids': move_lines,
                    'date': date,
                    'ref': ref,
                    'stock_move_id': self.id,
                    'z_analytic_account_id':self.analytic_account_id.id,
                })
                new_account_move.post()



class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    z_analytic_tag_ids = fields.Many2many('account.analytic.tag',string='Analytic Tags',compute="compute_analytical_tags")


    @api.multi
    @api.depends('lot_id')
    def compute_analytical_tags(self):
        for lines in self:
            if lines.picking_id.sale_id:
                if lines.lot_id:
                    lines.z_analytic_tag_ids = lines.lot_id.z_analytic_tag_ids.ids
            '''if lines.picking_id.sale_id:
                stock_line = self.env['stock.move.line'].search([('product_id', '=', lines.product_id.id)])
                if stock_line:
                    for line in stock_line:
                        if line.production_id:
                            if line.product_id.id == lines.product_id.id:
                                if lines.lot_id:
                                    if line.lot_id.id == lines.lot_id.id:
                                        lines.z_analytic_tag_ids = line.production_id.z_analytic_tag_ids_default.ids'''
                                        




