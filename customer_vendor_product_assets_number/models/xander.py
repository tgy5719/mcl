from odoo import models, fields, api, _

class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = ['product.category']
    xander =  fields.Many2one('product.neun',store=True,string='Sequence Type', ondelete='cascade')
    name= fields.Char(string='Category Name',store=True ,ondelete='cascade',required = True)
    
