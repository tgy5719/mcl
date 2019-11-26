from odoo import api, fields, models, _

class Inventory(models.Model):
    _inherit = "stock.inventory"

    z_reason = fields.Many2one('reason.name',string="Reason")

