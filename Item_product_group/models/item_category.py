from odoo import api, fields, models, tools,_

class ItemCategory(models.Model):
    _name = "item.category"

    name = fields.Char(string='Code')
    description = fields.Char(string='Description')


    
