from odoo import api, fields, models,_

class HrContract(models.Model):
  
    _inherit = 'hr.contract'

    z_hra = fields.Monetary('HRA')
    z_special_allowance = fields.Monetary('Special Allowance')
    z_other_allowance = fields.Monetary('Other Allowance')
    z_conveyance_allowance = fields.Monetary(string='Conveyance Allowance')
    z_food_allowance = fields.Monetary(string='Food Allowance')
    z_income_tax = fields.Monetary(string='Income Tax')
    z_canteen_recovery = fields.Monetary(string='Canteen Recovery')
    z_other_deduction = fields.Monetary(string='Other Deduction')
    z_travel_advance = fields.Monetary(string='Travel Advance')

