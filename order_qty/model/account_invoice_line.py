from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    z_no_of_package = fields.Float(string="No of Boxes",compute='_onchange_quantity',store=True)

    @api.depends('quantity')
    def _onchange_quantity(self):
        box = 0.0
        for line in self:
            if line.quantity > 0 and line.product_packaging.qty != 0:
                box = line.quantity / line.product_packaging.qty
                line.z_no_of_package = box