# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError, AccessError

class StockMoveLine(models.Model):
  _inherit = 'stock.move.line'

  z_qty_sq_mtr = fields.Float(string="Qty.SQM")
  z_by_product = fields.Boolean(string="Is by Product",related="product_id.z_by_product")


  '''@api.multi
       
      '''

  @api.onchange('z_qty_sq_mtr')
  def check_conversion_ration(self):
    for line in self:
      if line.z_qty_sq_mtr:
        line.qty_done = line.product_id.z_conversion_ratio * line.z_qty_sq_mtr
