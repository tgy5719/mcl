from odoo import models, fields, api, exceptions, _
from odoo.exceptions import Warning
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
import openerp.addons.decimal_precision as dp
import datetime
from datetime import datetime
import math

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    workcenter_id = fields.Many2one('mrp.workcenter',string="Machine Number")
    button_enable_change_wc = fields.Boolean(string="Change Work center",store=True,compute="compute_change_workcenter_validate")
    z_ref_doc = fields.Many2one('mrp.production',string="Reference MO",required=False)
    z_prodn_lines = fields.One2many('mrp.production','z_ref_doc',string="Procuction lines",required=False)
    z_product_name = fields.Char(string='Product Name',compute='get_prod')
    z_product_code = fields.Char(string='Product Code',compute='get_prod')

    @api.multi
    def button_mo_split_qty(self):
        view_id = self.env.ref('split_functionality.wizard_form_mo_order').id
        context = self._context.copy()
        return {
            'name':'Manufacturing Order',
            'view_type':'form',
            'view_mode':'form',
            'views' : [(view_id,'form')],
            'res_model':'mo.order.wizard',
            'view_id':view_id,
            'type':'ir.actions.act_window',
            'target':'new',
            'context':{'parent_obj': self.id},
        }

    @api.multi
    @api.depends('workcenter_id')
    def compute_change_workcenter_validate(self):
        for line in self:
            mo_workorder = self.env['mrp.workorder'].search([('production_id', '=', line.id)])
            for wc in mo_workorder:
                if wc.workcenter_id == line.workcenter_id:
                    line.button_enable_change_wc = True
                else:
                    line.button_enable_change_wc = False

    @api.multi
    @api.depends('product_id')
    def get_prod(self):
        for line in self:
            line.z_product_name = line.product_id.name
            line.z_product_code = line.product_id.default_code


    def button_update_machine(self):
        for line in self:
            if line.state == 'confirmed':
                raise exceptions.Warning(("Plan the process before updating."))
            else:
                if line.workcenter_id:
                    mo_workorder = self.env['mrp.workorder'].search([('production_id', '=', line.id)])
                    for wc in mo_workorder:
                        wc.update({'workcenter_id':line.workcenter_id.id})
                    line.button_enable_change_wc = True
                else:
                    raise exceptions.Warning(("Enter the Machine Number before updating"))
        

class MoOrderWizard(models.TransientModel):
    _name= 'mo.order.wizard'
    _description = 'Mo Order wizard'

    product_uom_id = fields.Many2one(
        'product.uom', 'Product Unit of Measure', required=True)
    product_id = fields.Many2one(
        'product.product', 'Product',
        required=True)
    date_planned_start = fields.Datetime(
        'Deadline Start', copy=False, default=fields.Datetime.now,
        index=True, required=True)
    date_planned_finished = fields.Datetime(
        'Deadline End', copy=False, default=fields.Datetime.now,
        index=True)
    bom_id = fields.Many2one(
        'mrp.bom', 'Bill of Material',
        help="Bill of Materials allow you to define the list of required raw materials to make a finished product.")
    routing_id = fields.Many2one(
        'mrp.routing', 'Routing',
         store=True,
        help="The list of operations (list of work centers) to produce the finished product. The routing "
             "is mainly used to compute work center costs during operations and to plan future loads on "
             "work centers based on production planning.")
    product_qty = fields.Float(
        'Quantity To Produce',
        default=1.0, digits=dp.get_precision('Product Unit of Measure'),
        required=True)
    new_product_qty = fields.Float(
        'Quantity To Produce',
        default=1.0, digits=dp.get_precision('Product Unit of Measure'),
        required=True)
    mo_id = fields.Many2one('mrp.production',string="Mo Reference")
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type', required=True)
    location_src_id = fields.Many2one(
        'stock.location', 'Raw Materials Location', required=True,
        help="Location where the system will look for components.")
    location_dest_id = fields.Many2one(
        'stock.location', 'Finished Products Location', required=True,
        help="Location where the system will stock the finished products.")
    name = fields.Many2one('mrp.production',string="Ref.Doc.",required=False)
    
    @api.model
    def _update_product_to_produce(self, production, qty):
        production_move = production.move_finished_ids.filtered(lambda x:x.product_id.id == production.product_id.id and x.state not in ('done', 'cancel'))
        if production_move:
            production_move.write({'product_uom_qty': qty})
        else:
            production_move = production._generate_finished_moves()
            production_move = production.move_finished_ids.filtered(lambda x : x.state not in ('done', 'cancel') and production.product_id.id == x.product_id.id)
            production_move.write({'product_uom_qty': qty})

    @api.multi
    @api.onchange('product_qty')
    def onchange_product_split_quantity(self):
        context=self._context
        record=self.env['mrp.production'].search([('id','=',self._context['parent_obj'])])
        for line in self:
            if record:
                line.product_id = record.product_id.id
                line.product_qty = record.product_qty
                line.bom_id = record.bom_id.id
                line.product_uom_id = record.product_uom_id.id
                line.routing_id = record.routing_id.id
                line.mo_id = record.id
                line.picking_type_id = record.picking_type_id.id
                line.location_dest_id = record.location_dest_id.id
                line.location_src_id = record.location_src_id.id
                line.name = record.id

    @api.multi
    def generate_mo_order(self):
        for line in self:
            mo_update = self.env['mrp.production'].search([('id', '=', self.mo_id.id)])
            if mo_update:
                for order in mo_update:
                    if line.new_product_qty >= line.product_qty:
                        raise exceptions.Warning(("Entered Quantity is Greater the the defined Quantity"))
                    else:
                        order.update({'product_qty':line.product_qty - line.new_product_qty})
        mo_count = self.env['mrp.production']
        if not mo_count:
            vals = {
                'product_id': self.product_id.id,
                'product_qty': self.new_product_qty,
                'bom_id': self.bom_id.id,
                'routing_id': self.routing_id.id,
                'product_uom_id':self.product_uom_id.id,
                'date_planned_start': self.date_planned_start,
                'picking_type_id':self.picking_type_id.id,
                'location_src_id':self.location_src_id.id,
                'location_dest_id':self.location_dest_id.id,
                'z_ref_doc':self.name.id
                }
            mo_obj = self.env['mrp.production'].create(vals)
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for wizard in self:
            production = wizard.mo_id
            produced = sum(production.move_finished_ids.filtered(lambda m: m.product_id == production.product_id).mapped('quantity_done'))
            if wizard.product_qty < produced:
                raise UserError(_("You have already processed %d. Please input a quantity higher than %d ")%(produced, produced))
            production.write({'product_qty': wizard.product_qty - wizard.new_product_qty})
            done_moves = production.move_finished_ids.filtered(lambda x: x.state == 'done' and x.product_id == production.product_id)
            qty_produced = production.product_id.uom_id._compute_quantity(sum(done_moves.mapped('product_qty')), production.product_uom_id)
            factor = production.product_uom_id._compute_quantity(production.product_qty - qty_produced, production.bom_id.product_uom_id) / production.bom_id.product_qty
            boms, lines = production.bom_id.explode(production.product_id, factor, picking_type=production.bom_id.picking_type_id)
            for line, line_data in lines:
                production._update_raw_move(line, line_data)
            operation_bom_qty = {}
            for bom, bom_data in boms:
                for operation in bom.routing_id.operation_ids:
                    operation_bom_qty[operation.id] = bom_data['qty']
            self._update_product_to_produce(production, production.product_qty - qty_produced)
            moves = production.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            moves._action_assign()
            for wo in production.workorder_ids:
                operation = wo.operation_id
                if operation_bom_qty.get(operation.id):
                    cycle_number = math.ceil(operation_bom_qty[operation.id] / operation.workcenter_id.capacity)  # TODO: float_round UP
                    wo.duration_expected = (operation.workcenter_id.time_start +
                                 operation.workcenter_id.time_stop +
                                 cycle_number * operation.time_cycle * 100.0 / operation.workcenter_id.time_efficiency)
                quantity = wo.qty_production - wo.qty_produced
                if production.product_id.tracking == 'serial':
                    quantity = 1.0 if not float_is_zero(quantity, precision_digits=precision) else 0.0
                else:
                    quantity = quantity if (quantity > 0) else 0
                if float_is_zero(quantity, precision_digits=precision):
                    wo.final_lot_id = False
                    wo.active_move_line_ids.unlink()
                wo.qty_producing = quantity
                if wo.qty_produced < wo.qty_production and wo.state == 'done':
                    wo.state = 'progress'
                # assign moves; last operation receive all unassigned moves
                # TODO: following could be put in a function as it is similar as code in _workorders_create
                # TODO: only needed when creating new moves
                moves_raw = production.move_raw_ids.filtered(lambda move: move.operation_id == operation and move.state not in ('done', 'cancel'))
                if wo == production.workorder_ids[-1]:
                    moves_raw |= production.move_raw_ids.filtered(lambda move: not move.operation_id)
                moves_finished = production.move_finished_ids.filtered(lambda move: move.operation_id == operation) #TODO: code does nothing, unless maybe by_products?
                moves_raw.mapped('move_line_ids').write({'workorder_id': wo.id})
                (moves_finished + moves_raw).write({'workorder_id': wo.id})
                if quantity > 0 and wo.move_raw_ids.filtered(lambda x: x.product_id.tracking != 'none') and not wo.active_move_line_ids:
                    wo._generate_lot_ids()
        return {}
