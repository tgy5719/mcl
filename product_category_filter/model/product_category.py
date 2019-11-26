from odoo import models, fields, api, _

class ProductCategory(models.Model):
    _inherit = "product.category"

    z_description = fields.Char('Description')
    z_release = fields.Boolean('Release')

class ProductTemplate(models.Model):
    _inherit = "product.template"

    categ_id = fields.Many2one(
        'product.category', 'Product Category',
        change_default=True,required=True,domain=[('z_release', '=', 'True')])