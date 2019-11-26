# -*- coding: utf-8 -*-

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    post_date = fields.Datetime('Post Date', copy=False)

    @api.multi
    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        for mo in self.filtered(lambda m: m.post_date):
            if mo.post_date:
                stock_moves = self.env['stock.move'].search([('reference', '=', mo.name)])
                stock_move_lines = self.env['stock.move.line'].search([('reference', '=', mo.name)])
                stock_moves.write({'date': mo.post_date})
                stock_move_lines.write({'date': mo.post_date})
                lines = self.env['account.move.line'].search([('name', '=', mo.name)])
                for line in lines:
                    line.move_id.write({'date': mo.post_date})
        return res

