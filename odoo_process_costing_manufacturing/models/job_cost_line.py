# -*- coding: utf-8 -*-

from odoo import models, fields, api

class JobCostLine(models.Model): 
    _name = 'mrp.job.cost.line'
    _rec_name = 'description'
    
    @api.depends('product_qty','cost_price','ctc_per_hour_id')
    def _compute_total_cost(self):
        for rec in self:
            if rec.product_id:
                rec.total_cost = rec.product_qty * rec.cost_price
            if rec.employee_id:
                rec.total_cost = rec.product_qty * rec.ctc_per_hour_id
    
    @api.depends('actual_quantity','ctc_per_hour_id','cost_price')
    def _compute_mrp_actual_total_cost(self):
        for rec in self:
            if rec.employee_id:
                if rec.actual_quantity and rec.ctc_per_hour_id:
                    rec.total_actual_cost = rec.actual_quantity * rec.ctc_per_hour_id
            if rec.product_id:
                rec.total_actual_cost = rec.actual_quantity * rec.cost_price

    
    routing_workcenter_id = fields.Many2one(
        'mrp.routing.workcenter',
        'Operation',
        copy=True,
        required=True,
    )
    employee_id = fields.Many2one('hr.employee',string='Employee')
    ctc_per_hour_id = fields.Float('CTC Per Hour',compute="_onchange_employee_id")
    product_id = fields.Many2one(
        'product.product',
        string='Cost Element',
        copy=False,domain="[('z_process_cost', '=', True)]")
    description = fields.Char(
        string='Description',
        copy=False,
    )
    reference = fields.Char(
        string='Reference',
        copy=False,
    )
    date = fields.Date(
        string='Date',
        required=False,
        copy=False,
    )
    product_qty = fields.Float(
        string='Planned',
        copy=False,
        
    )
    uom_id = fields.Many2one(
        'uom.uom',#product.uom
        string='UOM',
    )
    cost_price = fields.Float(
        string='Cost / Hour',
        copy=False,
    )
    total_cost = fields.Float(
        string='Total Cost',
        store=True,compute="_compute_total_cost"
    )
    currency_id = fields.Many2one(
        'res.currency', 
        related='mrp_id.custom_currency_id',
        string='Currency', 
        store=True,
        readonly=True
    )
    job_type = fields.Selection(
        selection=[('material','Material'),
                    ('labour','Labour'),
                    ('overhead','Overhead')],
        string="Process Cost Type",
        required=False,
    )
    bom_id = fields.Many2one(
        'mrp.bom',
        related='mrp_id.bom_id',
        store=True,
        string="Bill of Material",
    )
    mrp_id = fields.Many2one(
        'mrp.production',
        string="Manufacturing Order",
    )
    company_id = fields.Many2one(
        'res.company',
        related='mrp_id.company_id',
        store=True,
        string="Company",
    )
    routing_id = fields.Many2one(
        'mrp.routing',
        related='mrp_id.routing_id',
        store=True,
        string="Routing",
    )
    work_order_line_id = fields.Many2one(
        'workorder.job.cost.line',
        'Workorder Job Cost Line'
     )
    actual_quantity = fields.Float(
        string='Actual'
    )
    z_ratio = fields.Float(
        string='Ratio',compute='_change',store=True
    )
    multiply_ratio = fields.Float(
        string='Mutiply Ratio',compute='_change_hrs',store=True
    )
    total_actual_cost = fields.Float(
        string='Total Actual Cost',
        compute="_compute_mrp_actual_total_cost",
    )
#     material_workorder_id = fields.Many2one(
#         'mrp.workorder',
#         string='Workorder',
#     )
#     labour_workorder_id = fields.Many2one(
#         'mrp.workorder',
#         string='Workorder',
#     )
#     overhead_workorder_id = fields.Many2one(
#         'mrp.workorder',
#         string='Workorder',
#     )
    to_produse_product = fields.Many2one(
        'product.product',
        string='Produced Product',
        related='mrp_id.product_id',
        store=True,
    )
    to_produse_qty = fields.Float(
        string='To Produce Qty',
        related='mrp_id.product_qty',
        store=True,
    )
    z_split_order = fields.Many2one('mrp.production',
        string='Split Order',
        related = 'mrp_id.z_ref_doc',
        store=True,
    )
    split_ratio = fields.Float(
        string='Split Ratio',compute='_split',store=True
    )
    z_mo = fields.Many2one('mrp.production',
        string='MO Order',
        compute='_checkname',
        store=True,
    )

    @api.multi
    @api.depends('mrp_id.name')
    def _checkname(self):
        for line in self:
            for l in line.mrp_id:
                line.z_mo = l.id

    @api.multi
    @api.depends('z_split_order')
    def _split(self):
        for l in self:
            workder = self.env['mrp.job.cost.line'].search([('z_mo', '=', l.z_split_order.id),('product_id', '=', l.product_id.id)])
            for line in workder:
                l.split_ratio = line.z_ratio
    

     
    @api.multi
    @api.depends('actual_quantity')
    def _change(self):
          for l in self:
            for n in l.mrp_id:
              l.z_ratio = l.actual_quantity / n.product_qty

    @api.multi
    @api.depends('mrp_id.product_qty')
    def _change_hrs(self):
      for l in self:
        for n in l.mrp_id:
            l.multiply_ratio = l.z_ratio * n.product_qty


    # @api.multi
    # @api.depends('mrp_id.product_qty')
    # def _onchange_hrs(self):
    #     for l in self:  
    #       for n in l.mrp_id:
    #         l.actual = n.multiply
    #         l.actual_split = n.z_split

    # @api.multi
    # @api.depends('mrp_id.product_qty')
    # def _onchange_actual(self):
    #     for l in self:  
    #       for n in l.mrp_id:
    #         l.actual_split = n.z_split

    # @api.multi
    # @api.depends('actual')
    # def _onchange_boolean(self):
    #     for l in self:
    #         if l.actual:
    #             l.actualb = True



    # @api.multi
    # @api.onchange('actualb')
    # def _onchange_write_it(self):
    #     # rec = super(JobCostLine, self).write(vals)
    #     # if vals.get('actual'):
    #     for order in self:
    #         if order.actualb == True:
    #             if order.multiply_ratio > 0.0:
    #                 order.actual_quantity = order.multiply_ratio
    #             if order.actual_split > 0.0:
    #                 order.actual_quantity = order.actual_split

    

    @api.multi
    def _onchange_employee_id(self):
        for rec in self:
            res = self.env['hr.contract'].search([('employee_id','=',rec.employee_id.id)])
            for l in res:
                rec.ctc_per_hour_id = l.ctc_per_hour

    @api.multi
    def _onchange_ctc_cost(self):
        rec.cost_price = rec.product_qty * rec.ctc_per_hour_id
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            rec.product_qty = 1.0
            rec.uom_id = rec.product_id.uom_id
            rec.employee_id = False

    @api.onchange('employee_id')
    def make_product_id_empty(self):
        for line in self:
            if line.employee_id:
                line.product_id = False
            res = self.env['hr.contract'].search([('employee_id','=',line.employee_id.id)])
            for l in res:
                line.ctc_per_hour_id = l.ctc_per_hour

class BomJobCostLine(models.Model): 
    _name = 'bom.job.cost.line'
    _rec_name = 'description'
    
    @api.depends('product_qty','cost_price')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.product_qty * rec.cost_price
    
    @api.depends('actual_quantity','cost_price')
    def _compute_actual_total_cost(self):
        for rec in self:
            rec.total_actual_cost = rec.actual_quantity * rec.cost_price
    
    routing_workcenter_id = fields.Many2one(
        'mrp.routing.workcenter',
        'Operation',
        copy=True,
        required=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        copy=False,
        required=True,domain="[('z_process_cost', '=', True)]"
    )
    description = fields.Char(
        string='Description',
        copy=False,
    )
    reference = fields.Char(
        string='Reference',
        copy=False,
    )
    date = fields.Date(
        string='Date',
        required=False,
        copy=False,
    )
    product_qty = fields.Float(
        string='Planned Qty',
        copy=False,
        required=True,
    )
    uom_id = fields.Many2one(
        'uom.uom',#'product.uom', 
        string='UOM',
        required=True,
    )
    cost_price = fields.Float(
        string='Cost / Unit',
        copy=False,
    )
    total_cost = fields.Float(
        string='Total Cost',
        compute="_compute_total_cost",
    )
    custom_currency_id = fields.Many2one(
        'res.currency', 
        related='bom_id.custom_currency_id',
        string='Currency', 
        store=True,
        readonly=True
    )
    job_type = fields.Selection(
        selection=[('material','Material'),
                    ('labour','Labour'),
                    ('overhead','Overhead')
                ],
        string="Type",
        required=False,
    )
    bom_id = fields.Many2one(
        'mrp.bom',
        string="BOM",
    )
    actual_quantity = fields.Float(
        string='Actual Qty',
    )
    total_actual_cost = fields.Float(
        string='Total Actual Cost Price',
#         compute="_compute_actual_mrp_total_cost",
    )
    
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            rec.product_qty = 1.0
            rec.cost_price = rec.product_id.standard_price
            rec.uom_id = rec.product_id.uom_id


class WorkJobCostLine(models.Model): 
    _name = 'workorder.job.cost.line'
    _rec_name = 'description'
    
    @api.depends('product_qty','cost_price')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.product_qty * rec.cost_price
    
    @api.depends('actual_quantity','cost_price')
    def _compute_work_actual_total_cost(self):
        for rec in self:
            rec.total_actual_cost = rec.actual_quantity * rec.cost_price
    
    routing_workcenter_id = fields.Many2one(
        'mrp.routing.workcenter',
        'Operation',
        copy=True,
        required=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        copy=False,
        required=True,
    )
    description = fields.Char(
        string='Description',
        copy=False,
    )
    reference = fields.Char(
        string='Reference',
        copy=False,
    )
    date = fields.Date(
        string='Date',
        required=False,
        copy=False,
    )
    product_qty = fields.Float(
        string='Planned Qty',
        copy=False,
        required=True,
    )
    uom_id = fields.Many2one(
        'uom.uom',#product.uom
        string='UOM',
        required=True,
    )
    cost_price = fields.Float(
        string='Cost / Unit',
        copy=False,
    )
    actual_qty = fields.Float(
        string='Actual Cost',
        copy=False,
    )
#     actual_total_cost = fields.Float(
#         string='Total Actual Cost Price',
#         compute="_compute_total_actual_cost",
#     )
    total_cost = fields.Float(
        string='Total Cost',
        compute="_compute_total_cost",
    )
    currency_id = fields.Many2one(
        'res.currency', 
        related='workorder_id.custom_currency_id',
        string='Currency', 
        store=True,
        readonly=True
    )
    job_type = fields.Selection(
        selection=[('material','Material'),
                    ('labour','Labour'),
                    ('overhead','Overhead')
                ],
        string="Type",
        required=False,
    )
    workorder_id = fields.Many2one(
        'mrp.workorder',
        string='Workorder',
    )
    actual_quantity = fields.Float(
        string='Actual Qty',
    )
    total_actual_cost = fields.Float(
        string='Total Actual Cost',
        compute="_compute_work_actual_total_cost",
    )
    
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            rec.product_qty = 1.0
            rec.cost_price = rec.product_id.standard_price
            rec.uom_id = rec.product_id.uom_id

