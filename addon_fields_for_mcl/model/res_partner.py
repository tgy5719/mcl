from odoo import api, fields, models,_

class ResPartner(models.Model):
    _inherit = 'res.partner'

    z_sales_office = fields.Many2one('office.name',string="Sales Office")
    gst_reg_type = fields.Selection([('registered','Registered'),('unregistered','Unregistered'),('composite','Composite')],string="GST Registration Type")

    @api.multi
    @api.onchange('vat')
    def _gst(self):
    	for l in self:
    		if l.vat:
    			l.gst_reg_type = 'registered'
    		else:
    			l.gst_reg_type = 'unregistered'



           