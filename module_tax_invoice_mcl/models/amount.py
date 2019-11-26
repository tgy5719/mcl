from odoo.exceptions import UserError
from odoo import api, fields, models, _

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    transporter = fields.Char(string="Dispatched Through")
    e_way_no = fields.Char(string='E-way Bill No', store=True)
    z_delivered_to = fields.Char(string="Destination")
    vehicle = fields.Many2many('fleet.vehicle',string='Vehicle')
    ext_vehicle_no = fields.Char(string="External Vehicle No.")
   

    
