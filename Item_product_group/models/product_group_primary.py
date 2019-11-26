from odoo import api, fields, models, tools,_

class ProductGroupPrimary(models.Model):
    _name = "product.group.primary"

    name = fields.Char(string='Code')
    description = fields.Char(string='Description')
    item_category = fields.Many2one('item.category', string = 'Item Category')



    
    