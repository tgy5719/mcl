from odoo import api, fields, models, _

class StockMove(models.Model):
    _inherit = "stock.move"

    z_status = fields.Char('Status Type',store=True,track_visibility="always",compute='_compute_status_type')
    # z_consumption_routing = fields.Char('Consumption Routing',store = True,related = 'raw_material_production_id.name')

    @api.multi
    @api.depends('location_dest_id','location_id')
    def _compute_status_type(self):
    	for line in self:
    		if line.location_dest_id.id == 9:
    			line.z_status = 'Sale'
    		if line.location_dest_id.id == 7:
    			line.z_status = 'Consumption'
    		if line.location_id.id == 7:
    			line.z_status = 'Production'
    		if line.location_id.id == 8:
    			line.z_status = 'Purchase'
    		if line.location_id.id == 5:
    			line.z_status = 'Positive Adjustment'
    		if line.location_dest_id.id == 5:
    			line.z_status = 'Negative Adjustment'