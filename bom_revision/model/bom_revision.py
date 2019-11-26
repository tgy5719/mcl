from odoo import models, fields, api, exceptions, _
from odoo.exceptions import Warning
from odoo.exceptions import UserError
import openerp.addons.decimal_precision as dp
import datetime
from datetime import datetime

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def button_open_mo(self):
        view_id = self.env.ref('bom_revision.mrp_form_order').id
        context = self._context.copy()
        return {
            'name':'Manufacturing Order',
            'view_type':'form',
            'view_mode':'form',
            'views' : [(view_id,'form')],
            'res_model':'mrp.order.wizard',
            'view_id':view_id,
            'type':'ir.actions.act_window',
            'target':'new',
            'context':{'parent_obj': self.id},
        }


class MrpOrderWizard(models.TransientModel):
    _name= 'mrp.order.wizard'
    _description = 'Mrp Order wizard'

    @api.model
    def _get_default_picking_type(self):
        return self.env['stock.picking.type'].search([
            ('code', '=', 'mrp_operation'),
            ('warehouse_id.company_id', 'in', [self.env.context.get('company_id', self.env.user.company_id.id), False])],
            limit=1).id

    product_uom_id = fields.Many2one(
        'uom.uom', 'Product Unit of Measure')
    product_id = fields.Many2one(
        'product.product', 'Product',domain=[('type', 'in', ['product', 'consu'])])
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', related='product_id.product_tmpl_id')
    date_planned_start = fields.Datetime(
        'Deadline Start', copy=False, default=fields.Datetime.now,
        index=True, required=True)
    date_planned_finished = fields.Datetime(
        'Deadline End', copy=False, default=fields.Datetime.now,
        index=True)
    bom_id = fields.Many2one(
        'mrp.bom', 'Change In Recipe',
        help="Bill of Materials allow you to define the list of required raw materials to make a finished product.")
    routing_id = fields.Many2one(
        'mrp.routing', 'Routing',
         store=True,
        help="The list of operations (list of work centers) to produce the finished product. The routing "
             "is mainly used to compute work center costs during operations and to plan future loads on "
             "work centers based on production planning.")
    product_qty = fields.Float(
        'Quantity To Produce',
        digits=dp.get_precision('Product Unit of Measure'), related="mo_id.product_qty",
        required=True)
    mo_id = fields.Many2one('mrp.production',string="Mo Reference")
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        default=_get_default_picking_type, required=True)
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get('mrp.production'),
        required=True)

    @api.depends('product_qty')
    def _quantity_being(self):
    	for line in self:
    		quant = self.env['mrp.production'].search(['&',('id','=',line.mo_id.id),
    			('product_id','=',line.product_id.id)])
    		line.product_qty = quant.product_qty

    @api.onchange('product_id', 'picking_type_id', 'company_id')
    def onchange_product_id(self):
        """ Finds UoM of changed product. """
        if not self.product_id:
            self.bom_id = False
        else:
            bom = self.env['mrp.bom']._bom_find(product=self.product_id, picking_type=self.picking_type_id, company_id=self.company_id.id)
            if bom.type == 'normal':
                self.bom_id = bom.id
            else:
                self.bom_id = False
            self.product_uom_id = self.product_id.uom_id.id
            return {'domain': {'product_uom_id': [('category_id', '=', self.product_id.uom_id.category_id.id)]}}

    @api.multi
    @api.onchange('product_qty')
    def onchange_product_split_quantity(self):
        context=self._context
        record=self.env['mrp.production'].search([('id','=',self._context['parent_obj'])])
        for line in self:
            if record:
                line.product_id = record.product_id.id
                line.bom_id = record.bom_id.id
                line.product_uom_id = record.product_uom_id.id
                line.routing_id = record.routing_id.id
                line.mo_id = record.id
                line.picking_type_id = record.picking_type_id.id

    @api.multi
    def generate_mrp_order(self):
        mo_count = self.env['mrp.production']
        if not mo_count:
            vals = {
                'product_id': self.product_id.id,
                'product_qty': self.product_qty,
                'bom_id': self.bom_id.id,
                'routing_id': self.routing_id.id,
                'product_uom_id':self.product_uom_id.id,
                'date_planned_start': self.date_planned_start,
                'picking_type_id':self.picking_type_id.id
                }
            mo_obj = self.env['mrp.production'].create(vals)
            mo_co = self.env['mrp.production'].search([('id', '=', self.mo_id.id)]).unlink()
            return super(MrpOrderWizard, self).unlink()





class StockMoveInherit(models.Model):
    _inherit = "stock.move"

    quantity_id = fields.Float('Quantity', store=True, compute="_compute_quantity",track_visibility='always')
    product_id = fields.Many2one('product.product')

    @api.depends('quantity_id','product_id','location_id')
    def _compute_quantity(self):
        for line in self:
            quant = self.env['stock.quant'].search(['&',('product_id','=',line.product_id.id),
                ('location_id','=',line.product_id.location_id.id)])
            for q in quant:
                line.quantity_id = q.location_id
