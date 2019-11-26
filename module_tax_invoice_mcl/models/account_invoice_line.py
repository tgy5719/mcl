from odoo import api, fields, models, tools, _

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    lot_id = fields.Char('Lot Num',compute="lot_num")

    @api.multi
    @api.depends('invoice_id.origin','product_id')
    def lot_num(self):
    	for line in self:
    		lot_ref = []
    		strip_ref = 0
    		ref = 0
    		if line.invoice_id.origin:
    			#split the sale order to fetch the lot ref based on the shipment
    			sale_order_ref = line.invoice_id.origin.split(", ")
    			#match based on the sale order ref
    			pickings = self.env['stock.picking'].search([('origin','=',sale_order_ref)])
    			for pick in pickings:
    				if pick.sale_id:
    					move_line = self.env['stock.move.line'].search([('product_id','=',line.product_id.id),('picking_id','=',pick.id)])
    					if move_line:
    						for move in move_line:
    							ref = move.lot_id.name
    							lot_ref.append(ref)
    						strip_ref = str(set(lot_ref))
    						line.lot_id = strip_ref.strip("{ }")





