from odoo import models, fields, api


class LeadProduct(models.Model):
    _inherit = 'crm.lead'

    pdt_line = fields.One2many('crm.product_line', 'pdt_crm', string="Product")

    def sale_action_quotations_new(self):
        vals = {'partner_id': self.partner_id.id,
                'user_id': self.user_id.id,
                'medium_id':self.medium_id.id,
                'source_id':self.source_id.id,
                'campaign_id':self.campaign_id.id,
                'team_id':self.team_id.id,
                'opportunity_id':self.id
                }
        sale_order = self.env['sale.order'].create(vals)
        order_line = self.env['sale.order.line']
        for data in self.pdt_line:
            pdt_value = {
                        'price_unit':data.market_price,            
                        'order_id': sale_order.id,
                        'product_id': data.product_id.id,
                        'name': data.name,
                        'product_uom_qty': data.product_uom_qty,
                        'uom_id': data.uom_id.id
                }
            order_line.create(pdt_value)
        view_id = self.env.ref('sale.view_order_form')
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
            'res_id': sale_order.id,
            'view_id': view_id.id,
        }


class LeadProductLine(models.Model):
    _name = 'crm.product_line'

    product_id = fields.Many2one('product.product', string="Product",
                                 change_default=True, ondelete='restrict', required=True)

    name = fields.Text(string='Description')
    pdt_crm = fields.Many2one('crm.lead')
    product_uom_qty = fields.Float(string='Quantity', default=1.0)
    #price_unit = fields.Float(string='Cost Price')
    market_price = fields.Float(string='Sale Price',store=True)
    #qty_hand = fields.Integer(string='Quantity On Hand')
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure')


    @api.onchange('product_id','product_uom_qty')
    def product_data(self):
        data = self.env['product.template'].search([('name', '=', self.product_id.name)])
        self.name = data.name
        #self.price_unit = data.list_price
        self.uom_id = data.uom_id
        self.market_price = data.list_price
        #self.qty_hand = data.qty_available
