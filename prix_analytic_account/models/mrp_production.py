# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round

class MrpProduction(models.Model):
      _inherit = 'mrp.production'

      analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', help="The analytic account related to a sales order.",store=True,track_visibility='always',compute="fetch_analytic_account_id")
      z_analytic_tag_ids = fields.Many2many('account.analytic.tag','tag_id',string='Analytic Tags')
      z_analytic_tag_ids_default = fields.Many2many('account.analytic.tag','tag_default_id', string='Analytic Tags from Defaults')
      z_analytic_tag_ids_picking_type = fields.Many2many('account.analytic.tag','tag_picking_id',string='Analytic Tags from Operation type')

      @api.multi
      @api.depends('location_src_id','product_qty')
      def fetch_analytic_account_id(self):
            for line in self:
                  line.z_analytic_tag_ids_default = line.z_analytic_tag_ids = line.z_analytic_tag_ids_picking_type = False
                  if line.location_src_id:
                        wh_short_code = self.env['stock.warehouse'].search([('code', '=', line.location_src_id.location_id.name)])
                        if wh_short_code:
                              analytic_id = self.env['account.analytic.account'].search([('z_warehouse', '=', wh_short_code.id)])
                              if analytic_id:
                                    for lines in analytic_id[:1]:
                                          line.analytic_account_id = lines.id
                                    analytic_tag_id = self.env['account.analytic.account'].search([('id', '=', line.analytic_account_id.id)])
                                    if analytic_tag_id:
                                          for tags in analytic_tag_id:
                                                line.z_analytic_tag_ids_default = tags.z_analytic_tag_ids.ids
                                                line.z_analytic_tag_ids_picking_type = line.picking_type_id.z_analytic_tag_ids.ids
                                                line.z_analytic_tag_ids = line.z_analytic_tag_ids_default.ids + line.z_analytic_tag_ids_picking_type.ids

      def _generate_finished_moves(self):
            analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in self.z_analytic_tag_ids]
            move = self.env['stock.move'].create({
			'name': self.name,
            'date': self.date_planned_start,
            'date_expected': self.date_planned_start,
            'picking_type_id': self.picking_type_id.id,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'product_uom_qty': self.product_qty,
            'location_id': self.product_id.property_stock_production.id,
            'location_dest_id': self.location_dest_id.id,
            'company_id': self.company_id.id,
            'production_id': self.id,
            'warehouse_id': self.location_dest_id.get_warehouse().id,
            'origin': self.name,
            'group_id': self.procurement_group_id.id,
            'propagate': self.propagate,
            'move_dest_ids': [(4, x.id) for x in self.move_dest_ids],
            'analytic_account_id':self.analytic_account_id.id,
            'z_analytic_tag_ids': analytic_tag_ids,
            
            })
            move._action_confirm()
            return move

      def _generate_raw_move(self, bom_line, line_data):
            quantity = line_data['qty']
            # alt_op needed for the case when you explode phantom bom and all the lines will be consumed in the operation given by the parent bom line
            alt_op = line_data['parent_line'] and line_data['parent_line'].operation_id.id or False
            if bom_line.child_bom_id and bom_line.child_bom_id.type == 'phantom':
                  return self.env['stock.move']
            if bom_line.product_id.type not in ['product', 'consu']:
                  return self.env['stock.move']
            if self.routing_id:
                  routing = self.routing_id
            else:
                  routing = self.bom_id.routing_id
            if routing and routing.location_id:
                  source_location = routing.location_id
            else:
                  source_location = self.location_src_id
            original_quantity = (self.product_qty - self.qty_produced) or 1.0
            analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in self.z_analytic_tag_ids]
            data = {
            'sequence': bom_line.sequence,
            'name': self.name,
            'date': self.date_planned_start,
            'date_expected': self.date_planned_start,
            'bom_line_id': bom_line.id,
            'picking_type_id': self.picking_type_id.id,
            'product_id': bom_line.product_id.id,
            'product_uom_qty': quantity,
            'product_uom': bom_line.product_uom_id.id,
            'location_id': source_location.id,
            'location_dest_id': self.product_id.property_stock_production.id,
            'raw_material_production_id': self.id,
            'company_id': self.company_id.id,
            'operation_id': bom_line.operation_id.id or alt_op,
            'price_unit': bom_line.product_id.standard_price,
            'procure_method': 'make_to_stock',
            'origin': self.name,
            'warehouse_id': source_location.get_warehouse().id,
            'group_id': self.procurement_group_id.id,
            'propagate': self.propagate,
            'unit_factor': quantity / original_quantity,
            'analytic_account_id':self.analytic_account_id.id,
            'z_analytic_tag_ids':analytic_tag_ids,
            }
            return self.env['stock.move'].create(data)

      def _get_raw_move_data(self, bom_line, line_data):
            analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in self.z_analytic_tag_ids]
            quantity = line_data['qty']
            # alt_op needed for the case when you explode phantom bom and all the lines will be consumed in the operation given by the parent bom line
            alt_op = line_data['parent_line'] and line_data['parent_line'].operation_id.id or False
            if bom_line.child_bom_id and bom_line.child_bom_id.type == 'phantom':
                  return
            if bom_line.product_id.type not in ['product', 'consu']:
                  return
            if self.routing_id:
                  routing = self.routing_id
            else:
                  routing = self.bom_id.routing_id
            if routing and routing.location_id:
                  source_location = routing.location_id
            else:
                  source_location = self.location_src_id
            original_quantity = (self.product_qty - self.qty_produced) or 1.0
            return {
            'sequence': bom_line.sequence,
            'name': self.name,
            'date': self.date_planned_start,
            'date_expected': self.date_planned_start,
            'bom_line_id': bom_line.id,
            'picking_type_id': self.picking_type_id.id,
            'product_id': bom_line.product_id.id,
            'product_uom_qty': quantity,
            'product_uom': bom_line.product_uom_id.id,
            'location_id': source_location.id,
            'location_dest_id': self.product_id.property_stock_production.id,
            'raw_material_production_id': self.id,
            'company_id': self.company_id.id,
            'operation_id': bom_line.operation_id.id or alt_op,
            'price_unit': bom_line.product_id.standard_price,
            'procure_method': 'make_to_stock',
            'origin': self.name,
            'warehouse_id': source_location.get_warehouse().id,
            'group_id': self.procurement_group_id.id,
            'propagate': self.propagate,
            'unit_factor': quantity / original_quantity,
            'analytic_account_id':self.analytic_account_id.id,
            'z_analytic_tag_ids':analytic_tag_ids,
            }

      @api.multi
      def post_inventory(self):
            for line in self:
                  for moveline in line.finished_move_line_ids:
                        if moveline.state not in ('done','cancel'):
                              if moveline.lot_id:
                                    moveline.lot_id.z_analytic_tag_ids = moveline.move_id.production_id.z_analytic_tag_ids_default.ids or moveline.production_id.z_analytic_tag_ids_default.ids
            return super(MrpProduction, self).post_inventory()

