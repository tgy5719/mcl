from odoo import api, fields, models, tools,_

class ProductGroupSecondary(models.Model):
    _name = "product.group.secondary"

    name = fields.Char(string='Code')
    description = fields.Char(string='Description')
    product_group_primary = fields.Many2one('product.group.primary', string = 'Product Group Primary')



    
    