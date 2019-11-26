from odoo import api, fields, models, _

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    z_parent_id = fields.Many2one('product.category', 'Parent Category', index=True,ondelete='cascade',related='product_id.categ_id.parent_id.parent_id')
    z_status = fields.Char('Status Type',store=True,track_visibility="always",compute='_compute_status_type')
    z_product_category = fields.Char('Product Category',store = True,related = 'product_id.categ_id.complete_name')
    z_production_routing = fields.Char('Routing',store = True,related = 'move_id.production_id.routing_id.name')
    z_consumption_routing = fields.Char('Consumption Routing',store = True,related = 'move_id.raw_material_production_id.routing_id.name')

    z_item_category = fields.Char('Item Category',store = True,related = 'product_id.product_tmpl_id.item_category.name')
    z_pg_primary = fields.Char('Product Group Primary',store = True,related = 'product_id.product_tmpl_id.product_group_primary.name')
    z_pg_secondary = fields.Char('Product Group Secondary',store = True,related = 'product_id.product_tmpl_id.product_group_secondary.name')
    # z_planned_quantity = fields.Float('Planned Quantity',store = True,related = 'production_id.z_planned_qty')

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


class StockQuant(models.Model):
    _inherit = "stock.quant"
    z_parent_id = fields.Many2one('product.category', 'Parent Category', index=True,store = True,ondelete='cascade',related='product_id.categ_id.parent_id')
    z_product_category = fields.Char('Product Category',store = True,related = 'product_id.categ_id.complete_name')

class ProductProduct(models.Model):
    _inherit = "product.product"
    z_parent_id = fields.Many2one('product.category', 'Parent Category', index=True,store = True,ondelete='cascade',related='categ_id.parent_id')
    z_product_category = fields.Char('Product Category',store = True,related = 'categ_id.complete_name')
