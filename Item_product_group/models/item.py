from odoo import api, fields, models

class ProductTemplate(models.Model):
    _name='product.template'
    _inherit='product.template'
    item_category = fields.Many2one('item.category', string = 'Item Category')
    product_group_primary = fields.Many2one('product.group.primary', domain="[('item_category', '=', item_category)]", string = 'Product Group Primary')
    product_group_secondary = fields.Many2one('product.group.secondary', domain="[('product_group_primary', '=', product_group_primary)]", string = 'Product Group Secondary')