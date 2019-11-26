# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    post_date = fields.Datetime('Post Date', copy=False)

    @api.multi
    def action_done(self):
        res = super(StockPicking, self).action_done()
        for picking in self.filtered(lambda p: p.post_date):
            if picking.post_date:
                stock_moves = self.env['stock.move'].search([('reference', '=', picking.name)])
                stock_move_lines = self.env['stock.move.line'].search([('reference', '=', picking.name)])
                account_moves = self.env['account.move'].search([('ref', '=', picking.name)])
                stock_moves.write({'date': picking.post_date})
                stock_move_lines.write({'date': picking.post_date})
                account_moves.write({'date': picking.post_date})
        return res
