from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp

class ProductTemplate(models.Model):
    _inherit = "product.template"

    z_uom_so_id = fields.Many2one('uom.uom','Sale Unit of Measure')

class ProductPackaging(models.Model):
    _inherit = "product.packaging"
    z_no_of_package = fields.Float(string="No Package")
