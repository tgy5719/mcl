from odoo import fields,models,api, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    z_sum_orderqty = fields.Float(store=True,track_visibility='onchange',compute='calculate_ordersum_qty', string='Ordered Quantity')
    z_sum_recevqty = fields.Float(store=True,track_visibility='onchange',compute='calculate_recevsum_qty', string='Received Quantity')
    z_sum_invoiceqty = fields.Float(store=True,track_visibility='onchange',compute='calculate_invoicesum_qty', string='Invoiced Quantity')
    z_status = fields.Char('Document Status',store=True,track_visibility="always",compute='_compute_status_type')
    

    @api.multi
    @api.depends('order_line.product_qty')
    def calculate_ordersum_qty(self):
        for oq in self:
            sumordqty = 0
            for line in oq.order_line:
                if line.categ_types == 'products':
                    sumordqty += line.product_qty
            oq.z_sum_orderqty = sumordqty


    @api.multi
    @api.depends('order_line.qty_received')
    def calculate_recevsum_qty(self):
        for rq in self:
            sumrecqty = 0
            for line in rq.order_line:
                if line.categ_types == 'products':
                    sumrecqty += line.qty_received
            rq.z_sum_recevqty = sumrecqty


    @api.multi
    @api.depends('order_line.qty_invoiced')
    def calculate_invoicesum_qty(self):
        for iq in self:
            suminvqty = 0
            for line in iq.order_line:
                if line.categ_types == 'products':
                    suminvqty += line.qty_invoiced
            iq.z_sum_invoiceqty = suminvqty



    @api.multi
    @api.depends('z_sum_orderqty','z_sum_recevqty','z_sum_invoiceqty')
    def _compute_status_type(self):
    	for line in self:
    		if (line.z_sum_orderqty == line.z_sum_recevqty == line.z_sum_invoiceqty):
    			line.z_status = 'GRN & Invoice Done'
    		if (line.z_sum_orderqty == line.z_sum_recevqty) and (line.z_sum_invoiceqty == 0):
    			line.z_status = 'Pending for Invoice'
    		if (line.z_sum_orderqty == line.z_sum_recevqty) and (line.z_sum_invoiceqty != 0) and (line.z_sum_recevqty != line.z_sum_invoiceqty):
    			line.z_status = 'Partial Invoice Done'
    		if (line.z_sum_orderqty != 0) and (line.z_sum_recevqty == 0):
    			line.z_status = 'Pending for GRN'
    		if (line.z_sum_orderqty != line.z_sum_recevqty) and (line.z_sum_recevqty != 0):
    			line.z_status = 'Partial GRN'



