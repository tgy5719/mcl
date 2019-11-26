from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    invoice_line_id = fields.Many2one(
        comodel_name='account.invoice.line',
        string='Invoice Line',
        copy=False,
        readonly=True,
    )
