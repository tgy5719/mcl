# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_utils, float_compare


class Inventory(models.Model):
    _inherit = "stock.inventory"
    _description = "Inventory"
    _order = "date desc, id desc"

    z_analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', required=True,help="The analytic account related to a sales order.")



class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"
    _description = "Inventory Line"
    _order = "product_id, inventory_id, location_id, prod_lot_id"

    z_analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')


    def _get_move_values(self, qty, location_id, location_dest_id, out):
        self.ensure_one()
        analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in self.z_analytic_tag_ids]
        return {
            'name': _('INVs:') + (self.inventory_id.name or ''),
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'product_uom_qty': qty,
            'date': self.inventory_id.date,
            'company_id': self.inventory_id.company_id.id,
            'inventory_id': self.inventory_id.id,
            'state': 'confirmed',
            'restrict_partner_id': self.partner_id.id,
            'analytic_account_id':self.inventory_id.z_analytic_account_id.id,
            'z_analytic_tag_ids':analytic_tag_ids,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'move_line_ids': [(0, 0, {
                'product_id': self.product_id.id,
                'lot_id': self.prod_lot_id.id,
                'product_uom_qty': 0,  # bypass reservation here
                'product_uom_id': self.product_uom_id.id,
                'qty_done': qty,
                'package_id': out and self.package_id.id or False,
                'result_package_id': (not out) and self.package_id.id or False,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
                'owner_id': self.partner_id.id,
            })]
        }

