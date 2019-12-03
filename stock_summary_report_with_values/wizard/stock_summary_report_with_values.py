# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Devintelle Solutions (<http://devintellecs.com/>).
#
##############################################################################

from io import StringIO, BytesIO
from datetime import datetime
from odoo import models, fields,api, _
import xlwt
from xlwt import easyxf
import base64
import itertools
from operator import itemgetter
import operator
import pdb

class stock_summary_report_with_values(models.TransientModel):
    _name = "stock.summary.report.with.values"

    @api.model
    def _get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one('res.company',string='Company',required="1", default=_get_company_id)
    warehouse_ids = fields.Many2many('stock.warehouse',string='Warehouse',required="1")
    location_id = fields.Many2one('stock.location',string='Location', domain="[('usage','!=','view')]")
    production_id = fields.Many2one('stock.move',string='Product Id')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    filter_by = fields.Selection([('product','Product'),('category','Product Category')],string='Filter By')
    category_id = fields.Many2one('product.category',string='Category')
    product_ids = fields.Many2many('product.product',string='Products')
    is_group_by_category = fields.Boolean('Group By Category')
    is_zero = fields.Boolean('With Zero Values')





    # Get the Purchase Quantity 
    @api.multi
    def get_purchased_qty(self,product):
        state = 'done'
        move_type = 'incoming'
        location_id = 8 
        query = """select sum(sm.product_uom_qty) from stock_move as sm \
                              JOIN stock_picking_type as spt ON spt.id = sm.picking_type_id \
                              JOIN product_product as pp ON pp.id = sm.product_id \
                              where sm.date < %s and sm.location_id = %s  \
                              and spt.code = %s and sm.product_id = %s and sm.purchase_line_id is not null \
                              and sm.state = %s 
                              """
        start_date = str(self.start_date) + ' 00:00:00'
        if self.location_id:
            params = (start_date,location_id, move_type, self.location_id.id, product.id, state)
        else:
            params = (start_date,location_id, move_type, product.id, state)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0

      # Get the Purchase Quantity  Value
    @api.multi
    def get_purchased_qty_value(self,product):
        state = 'done'
        move_type = 'incoming'
        location_id = 8 
        query = """select sum(sm.value) from stock_move as sm \
                              JOIN stock_picking_type as spt ON spt.id = sm.picking_type_id \
                              JOIN product_product as pp ON pp.id = sm.product_id \
                              where sm.date < %s and sm.location_id = %s  \
                              and spt.code = %s and sm.product_id = %s and sm.purchase_line_id is not null \
                              and sm.state = %s 
                              """
        start_date = str(self.start_date) + ' 00:00:00'
        if self.location_id:
            params = (start_date,location_id, move_type, self.location_id.id, product.id, state)
        else:
            params = (start_date,location_id, move_type, product.id, state)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0
      
    # Get the Return Purchase quantity
    @api.multi
    def get_purchased_returned_qty(self,product):
        state = 'done'
        move_type = 'incoming'
        location_dest_id = 8
        query = """select sum(sm.product_uom_qty) from stock_move as sm \
                              JOIN stock_picking_type as spt ON spt.id = sm.picking_type_id \
                              JOIN product_product as pp ON pp.id = sm.product_id \
                              where sm.date < %s and sm.location_dest_id = %s  \
                              and spt.code = %s and sm.product_id = %s and sm.purchase_line_id is not null \
                              and sm.state = %s 
                              """

        start_date = str(self.start_date) + ' 00:00:00'
        if self.location_id:
            params = (start_date,location_dest_id, move_type, self.location_id.id, product.id, state)
        else:
            params = (start_date,location_dest_id, move_type, product.id, state)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0

    # Get the Return Purchase quantity Values
    @api.multi
    def get_purchased_returned_qty_value(self,product):
        state = 'done'
        move_type = 'incoming'
        location_dest_id = 8
        query = """select sum(sm.value) from stock_move as sm \
                              JOIN stock_picking_type as spt ON spt.id = sm.picking_type_id \
                              JOIN product_product as pp ON pp.id = sm.product_id \
                              where sm.date < %s and sm.location_dest_id = %s  \
                              and spt.code = %s and sm.product_id = %s and sm.purchase_line_id is not null \
                              and sm.state = %s 
                              """

        start_date = str(self.start_date) + ' 00:00:00'
        if self.location_id:
            params = (start_date,location_dest_id, move_type, self.location_id.id, product.id, state)
        else:
            params = (start_date,location_dest_id, move_type, product.id, state)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0

   

    # Get the Manufactured quantity
    @api.multi
    def get_avaliable_manufactured_qty(self,product):
        state = 'done'
        location_id = 7  
        query = """select sum(sm.product_uom_qty) from stock_move as sm \
                                  JOIN product_product as pp ON pp.id = sm.product_id \
                                  where sm.date < %s and sm.location_id = %s and\
                                  sm.product_id = %s and sm.state = %s
                                  """

        start_date = str(self.start_date) + ' 00:00:00'
        params = (start_date,location_id, product.id, state)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0

    # Get the Manufactured quantity Values
    @api.multi
    def get_avaliable_manufactured_qty_value(self,product):
        state = 'done'
        location_id = 7  
        query = """select sum(sm.value) from stock_move as sm \
                                  JOIN product_product as pp ON pp.id = sm.product_id \
                                  where sm.date >= %s and sm.date <= %s and sm.location_id = %s and\
                                  sm.product_id = %s and sm.state = %s
                                  """

        start_date = str(self.start_date) + ' 00:00:00'
        end_date = str(self.end_date) + ' 23:59:59'
        params = (start_date,end_date,location_id, product.id, state)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0

    # Get the positive quantity
    @api.multi
    def get_positive_qty(self,product):
        state = 'done'
        location_id = 5
        query = """select sum(sm.product_uom_qty) from stock_move as sm \
                                  JOIN product_product as pp ON pp.id = sm.product_id \
                                  where sm.date < %s and \
                                  sm.location_id = %s and sm.product_id = %s \
                                  and sm.state = %s
                                  """

        start_date = str(self.start_date) + ' 00:00:00'
        # end_date = str(self.end_date) + ' 23:59:59'

        params = (start_date,location_id, product.id, state)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0

      # Get the positive quantity values
    @api.multi
    def get_positive_qty_value(self,product):
        state = 'done'
        location_id = 5
        query = """select sum(sm.value) from stock_move as sm \
                                  JOIN product_product as pp ON pp.id = sm.product_id \
                                  where sm.date < %s and \
                                  sm.location_id = %s and sm.product_id = %s \
                                  and sm.state = %s
                                  """

        start_date = str(self.start_date) + ' 00:00:00'
        # end_date = str(self.end_date) + ' 23:59:59'

        params = (start_date,location_id, product.id, state)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0

    # Get the sales quantity
    @api.multi
    def get_sold_qty(self,product):
        state = 'done'
        location_dest_id = 9
        query = """select sum(sm.product_uom_qty) from stock_move as sm \
                              JOIN product_product as pp ON pp.id = sm.product_id \
                              where sm.date < %s and sm.location_dest_id = %s \
                              and sm.product_id = %s\
                              and sm.state = %s
                              """

        start_date = str(self.start_date) + ' 00:00:00'
        
        params = (start_date,location_dest_id, product.id, state)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0
    # Get the sales quantity values
    @api.multi
    def get_sold_qty_value(self,product):
        state = 'done'
        location_dest_id = 9
        query = """select sum(sm.value) from stock_move as sm \
                              JOIN product_product as pp ON pp.id = sm.product_id \
                              where sm.date < %s and sm.location_dest_id = %s \
                              and sm.product_id = %s\
                              and sm.state = %s
                              """

        start_date = str(self.start_date) + ' 00:00:00'
        
        params = (start_date,location_dest_id, product.id, state)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0

    # Get the sales return quantity
    @api.multi
    def get_sold_returned_qty(self,product):
        state = 'done' 
        location_id = 9
        query = """select sum(sm.product_uom_qty) from stock_move as sm \
                              JOIN product_product as pp ON pp.id = sm.product_id \
                              where sm.date < %s and sm.location_id = %s \
                              and sm.product_id = %s\
                              and sm.state = %s
                              """

        start_date = str(self.start_date) + ' 00:00:00'
        
        params = (start_date,location_id, product.id, state)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0

    # Get the sales return quantity value
    @api.multi
    def get_sold_returned_qty_value(self,product):
        state = 'done' 
        location_id = 9
        query = """select sum(sm.value) from stock_move as sm \
                              JOIN product_product as pp ON pp.id = sm.product_id \
                              where sm.date < %s and sm.location_id = %s \
                              and sm.product_id = %s\
                              and sm.state = %s
                              """

        start_date = str(self.start_date) + ' 00:00:00'
        
        params = (start_date,location_id, product.id, state)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0

   
    # Get the in consumed quanity
    @api.multi
    def get_consumed_qty(self,product):
        state = 'done'
        location_dest_id = 7
        query = """select sum(sm.product_uom_qty) from stock_move as sm \
                              JOIN product_product as pp ON pp.id = sm.product_id \
                              where sm.date < %s and sm.location_dest_id = %s \
                              and sm.product_id = %s\
                              and sm.state = %s 
                              """

        start_date = str(self.start_date) + ' 00:00:00'
        params = (start_date,location_dest_id, product.id, state)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0


    # Get the in consumed quanity values
    @api.multi
    def get_consumed_qty_value(self,product):
        state = 'done'
        location_dest_id = 7
        query = """select sum(sm.value) from stock_move as sm \
                              JOIN product_product as pp ON pp.id = sm.product_id \
                              where sm.date < %s and sm.location_dest_id = %s \
                              and sm.product_id = %s\
                              and sm.state = %s 
                              """

        start_date = str(self.start_date) + ' 00:00:00'
        params = (start_date,location_dest_id, product.id, state)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0


    #  Get the Negative Quantity
    @api.multi
    def get_negative_qty(self,product):
        state = 'done'
        location_dest_id = 5
        query = """select sum(sm.product_uom_qty) from stock_move as sm \
                                  JOIN product_product as pp ON pp.id = sm.product_id \
                                  where sm.date < %s and \
                                  sm.location_dest_id = %s and sm.product_id = %s \
                                  and sm.state = %s
                                  """

        start_date = str(self.start_date) + ' 00:00:00'
        # end_date = str(self.end_date) + ' 23:59:59'

        params = (start_date,location_dest_id, product.id, state)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0

    #  Get the Negative Quantity
    @api.multi
    def get_negative_qty_value(self,product):
        state = 'done'
        location_dest_id = 5
        query = """select sum(sm.value) from stock_move as sm \
                                  JOIN product_product as pp ON pp.id = sm.product_id \
                                  where sm.date < %s and \
                                  sm.location_dest_id = %s and sm.product_id = %s \
                                  and sm.state = %s
                                  """

        start_date = str(self.start_date) + ' 00:00:00'
        # end_date = str(self.end_date) + ' 23:59:59'

        params = (start_date,location_dest_id, product.id, state)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0


   
    @api.multi
    def get_begining_adjustment_qty(self, product):
        state = 'done'
        query = """select sum(sm.product_uom_qty) from stock_move as sm \
                                  JOIN product_product as pp ON pp.id = sm.product_id \
                                  where sm.date < %s and \
                                  sm.product_id = %s and sm.picking_type_id is null\
                                  and sm.state = %s and sm.company_id = %s
                                  """

        start_date = str(self.start_date) + ' 00:00:00'

        params = (start_date, product.id, state, self.company_id.id)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0

    @api.multi
    def ending_get_begining_adjustment_qty(self, product):
        state = 'done'

        query = """select sum(sm.product_uom_qty) from stock_move as sm \
                                  JOIN product_product as pp ON pp.id = sm.product_id \
                                  where sm.date < %s and \
                                  sm.product_id = %s and sm.picking_type_id is null\
                                  and sm.state = %s and sm.company_id = %s
                                  """

        end_date = str(self.end_date) + ' 23:59:59'

        params = (end_date, product.id, state, self.company_id.id)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0

    @api.multi
    def get_manufactured_qty(self, product):
        state = 'done'
        location_id = 7
        # Difffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
        query = """select sum(sm.product_qty) from stock_move as sm \
                                  JOIN product_product as pp ON pp.id = sm.product_id \
                                  where sm.date >= %s and sm.date <= %s and sm.location_id = %s and \
                                  sm.product_id = %s \
                                  and sm.state = %s and sm.company_id = %s
                                  """

        start_date = str(self.start_date) + ' 00:00:00'
        end_date = str(self.end_date) + ' 23:59:59'

        params = (start_date, end_date,location_id, product.id, state, self.company_id.id)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0


    @api.multi
    def get_consumption_value(self, product):
      location_dest_id = 7
      price_unit = 0
      query = """select sum(sm.product_uom_qty) from stock_move as sm \
                                  JOIN product_product as pp ON pp.id = sm.product_id \
                                  where sm.date >= %s and sm.date <= %s and \
                                  sm.product_id = %s and \
                                  sm.location_dest_id = %s \
                                  and sm.state='done'\
                                  """
      start_date = str(self.start_date) + ' 00:00:00'
      end_date = str(self.end_date) + ' 23:59:59'
      params = (start_date, end_date, product.id,location_dest_id)
      self.env.cr.execute(query, params)
      result = self.env.cr.dictfetchall()
      if result[0].get('sum'):
        return result[0].get('sum')
      return 0.0

    @api.multi
    def get_consumption_value_value(self, product):
      location_dest_id = 7
      price_unit = 0
      query = """select sum(sm.value) from stock_move as sm \
                                  JOIN product_product as pp ON pp.id = sm.product_id \
                                  where sm.date >= %s and sm.date <= %s and \
                                  sm.product_id = %s and \
                                  sm.location_dest_id = %s  \
                                  and sm.state='done'\
                                  """
      start_date = str(self.start_date) + ' 00:00:00'
      end_date = str(self.end_date) + ' 23:59:59'
      params = (start_date, end_date, product.id,location_dest_id)
      self.env.cr.execute(query, params)
      result = self.env.cr.dictfetchall()
      if result[0].get('sum'):
        return result[0].get('sum')
      return 0.0


    # Get the Purchase Quantity in the select
    @api.multi
    def get_receive_qty(self, product):
        state = 'done'
        move_type = 'incoming'
        m_type = ''
        location_id = 8
        query = """select sum(sm.product_uom_qty) from stock_move as sm \
                      JOIN stock_picking_type as spt ON spt.id = sm.picking_type_id \
                      JOIN product_product as pp ON pp.id = sm.product_id \
                      where sm.date >= %s and sm.date <= %s\
                      and spt.code = %s and sm.location_id = %s and sm.product_id = %s \
                      and sm.state = %s and sm.company_id = %s
                      """

        start_date = str(self.start_date)+ ' 00:00:00'
        end_date = str(self.end_date) + ' 23:59:59'
        if self.location_id:
            params = (start_date, end_date,move_type, location_id, product.id, state,
                      self.company_id.id)
        else:
            params = (start_date, end_date, move_type,location_id, product.id, state,self.company_id.id)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0

    # Get the Purchase Quantity values
    @api.multi
    def get_receive_qty_values(self, product):
        state = 'done'
        move_type = 'incoming'
        m_type = ''
        location_id = 8
        query = """select sum(sm.value) from stock_move as sm \
                      JOIN stock_picking_type as spt ON spt.id = sm.picking_type_id \
                      JOIN product_product as pp ON pp.id = sm.product_id \
                      where sm.date >= %s and sm.date <= %s\
                      and spt.code = %s and sm.location_id = %s and sm.product_id = %s \
                      and sm.state = %s and sm.company_id = %s
                      """

        start_date = str(self.start_date)+ ' 00:00:00'
        end_date = str(self.end_date) + ' 23:59:59'
        if self.location_id:
            params = (start_date, end_date,move_type, location_id, product.id, state,
                      self.company_id.id)
        else:
            params = (start_date, end_date, move_type,location_id, product.id, state,self.company_id.id)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0

    # To get the sale Quantity in between the selecting date range
    @api.multi
    def get_sale_delivered_qty(self, product):
        state = 'done'
        move_type = 'outgoing'
        location_dest_id =9
        m_type = ''
        if self.location_id:
            m_type = 'and sm.location_id = %s'

        query = """select sum(sm.product_uom_qty) from stock_move as sm \
                          JOIN stock_picking_type as spt ON spt.id = sm.picking_type_id \
                          JOIN product_product as pp ON pp.id = sm.product_id  \
                          where sm.date >= %s and sm.date <= %s and sm.product_id = %s\
                          and sm.state = %s and sm.location_dest_id = %s\
                          """

        start_date = str(self.start_date) + ' 00:00:00'
        end_date = str(self.end_date) + ' 23:59:59'

        params = (start_date, end_date,  product.id, state,location_dest_id)
        # if self.location_id:
        # else:
        #     params = (start_date, end_date, move_type, product.id, state)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0  


    @api.multi
    def get_pos_adjustment_qty(self, product):
        state = 'done'
        location_id = 5
        location_dest_id = 12
        

        query = """select sum(sm.product_uom_qty) from stock_move as sm \
                                  JOIN product_product as pp ON pp.id = sm.product_id \
                                  where sm.date >= %s and sm.date <= %s and \
                                  sm.location_id = %s  and sm.product_id = %s and sm.picking_type_id is null\
                                  and sm.state = %s
                                  """

        start_date = str(self.start_date) + ' 00:00:00'
        end_date = str(self.end_date) + ' 23:59:59'

        params = (start_date, end_date,location_id, product.id, state)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0

    
    @api.multi
    def get_neg_adjustment_qty(self, product):
        state = 'done'
        location_id = 12
        location_dest_id = 5
        

        query = """select sum(sm.product_uom_qty) from stock_move as sm \
                                  JOIN product_product as pp ON pp.id = sm.product_id \
                                  where sm.date >= %s and sm.date <= %s and \
                                  sm.location_dest_id = %s and sm.product_id = %s and sm.picking_type_id is null\
                                  and sm.state = %s
                                  """

        start_date = str(self.start_date) + ' 00:00:00'
        end_date = str(self.end_date) + ' 23:59:59'

        params = (start_date, end_date,location_dest_id, product.id, state)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0
    @api.multi
    def get_neg_adjustment_qty_value(self, product):
        state = 'done'
        # location_id = 5
        location_dest_id = 5
        

        query = """select sum(sm.value) from stock_move as sm \
                                  JOIN product_product as pp ON pp.id = sm.product_id \
                                  where sm.date >= %s and sm.date <= %s and \
                                  sm.location_dest_id = %s and sm.product_id = %s and sm.picking_type_id is null\
                                  and sm.state = %s
                                  """

        start_date = str(self.start_date) + ' 00:00:00'
        end_date = str(self.end_date) + ' 23:59:59'

        params = (start_date, end_date,location_dest_id, product.id, state)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0


    @api.multi
    def get_availabel_quantity(self, product):
        in_qty_purchased = self.get_purchased_qty(product)
        in_qty_returned_purchased = self.get_purchased_returned_qty(product)
        net_purchased_qty = in_qty_purchased - in_qty_returned_purchased
        in_qty_manufactured = self.get_avaliable_manufactured_qty(product)
        in_qty_positive = self.get_positive_qty(product)
        in_qty_sold = self.get_sold_qty(product)
        in_returned_qty = self.get_sold_returned_qty(product)
        net_sales = in_qty_sold - in_returned_qty
        in_qty_consumed = self.get_consumed_qty(product)
        in_qty_negative = self.get_negative_qty(product)
        # out_qty = self.get_before_outgoing_qty(product)
        # adjust_qty = self.get_begining_adjustment_qty(product)
        total_qty = (net_purchased_qty + in_qty_manufactured + in_qty_positive) - (net_sales + in_qty_consumed + in_qty_negative)
        return total_qty

    @api.multi
    def get_pos_adjustment_qty_value(self, product):
        state = 'done'
        location_id = 5
        location_dest_id = 12
        query = """select sum(sm.value) from stock_move as sm \
                                  JOIN product_product as pp ON pp.id = sm.product_id \
                                  where sm.date >= %s and sm.date <= %s and \
                                  sm.location_id = %s and sm.product_id = %s and sm.picking_type_id is null\
                                  and sm.state = %s
                                  """

        start_date = str(self.start_date) + ' 00:00:00'
        end_date = str(self.end_date) + ' 23:59:59'

        params = (start_date, end_date,location_id, product.id, state)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0

    @api.multi
    def get_sale_delivered_qty_value(self, product):
        state = 'done'
        move_type = 'outgoing'
        location_dest_id =9
        m_type = ''
        if self.location_id:
            m_type = 'and sm.location_id = %s'

        query = """select sum(sm.value) from stock_move as sm \
                          JOIN stock_picking_type as spt ON spt.id = sm.picking_type_id \
                          JOIN product_product as pp ON pp.id = sm.product_id \
                          where sm.date >= %s and sm.date <= %s and sm.product_id = %s \
                          and sm.state = %s and sm.company_id = %s and sm.location_dest_id = %s\
                          """

        start_date = str(self.start_date) + ' 00:00:00'
        end_date = str(self.end_date) + ' 23:59:59'

        params = (start_date, end_date, product.id, state,
                      self.company_id.id,location_dest_id)
        # if self.location_id:
        # else:
        #     params = (start_date, end_date, move_type, product.id, state, self.company_id.id)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        return 0.0

    # Get the later product cost     
    @api.multi
    def get_product_cost(self, product):
        query = """select cost from product_price_history 
                                where product_id = %s 
                                order by id desc
                                  """
        self.env.cr.execute(query, product.ids)
        result = self.env.cr.dictfetchall()
        if result:
          if result[0].get('cost'):
              return result[0].get('cost')
        return 0.0

    @api.multi
    def get_availabel_quantity_value(self, product):
      in_qty_purchased_value = self.get_purchased_qty_value(product)
      in_qty_purchased_returned_value = self.get_purchased_returned_qty_value(product)
      # pdb.set_trace()
      net_purchased_value = in_qty_purchased_value - in_qty_purchased_returned_value
      in_qty_manufactured_value = self.get_avaliable_manufactured_qty_value(product)
      in_qty_sold_value = self.get_sold_qty_value(product)
      in_returned_qty_value = self.get_sold_returned_qty_value(product)
      net_sales_value = in_qty_sold_value - in_returned_qty_value
      in_qty_consumed_value = self.get_consumed_qty_value(product)
      in_qty_positive_value = self.get_positive_qty_value(product)
      in_qty_negative_value = self.get_negative_qty_value(product)
      total_qty_value = (net_purchased_value + in_qty_manufactured_value + in_qty_positive_value) - (net_sales_value + in_qty_consumed_value + in_qty_negative_value)

      return total_qty_value


    def get_product(self):
        product_pool=self.env['product.product']
        if not self.filter_by:
            product_ids = product_pool.search([('type','=','product')])
            return product_ids
        elif self.filter_by == 'product' and self.product_ids:
            return self.product_ids
        elif self.filter_by == 'category' and self.category_id:
            product_ids = product_pool.search([('categ_id','child_of',self.category_id.id),('type','!=','service')])
            return product_ids

    @api.multi
    def group_by_lines(self,lst):
        n_lst = sorted(lst, key=itemgetter('category'))
        groups = itertools.groupby(n_lst, key=operator.itemgetter('category'))
        group_lines = [{'category': k, 'values': [x for x in v]} for k, v in groups]
        return group_lines

    @api.multi
    def get_lines(self):
      lst=[]
      product_ids = self.get_product()
      # print("Product Lentsssssssssssssssssssssssssssssssssssss",len(product_ids))
      for product in product_ids:
        beginning_qty = self.get_availabel_quantity(product)
        # beginning_value = self.get_availabel_quantity_value(product)
        beginning_value = beginning_qty *self.get_product_cost(product)
        received_qty = self.get_receive_qty(product)
        received_value = self.get_receive_qty_values(product)
        sale_del_qty = self.get_sale_delivered_qty(product)
        sale_del_qty_value =  self.get_sale_delivered_qty_value(product)
        mrp_qty = self.get_manufactured_qty(product)
        mrp_value = self.get_avaliable_manufactured_qty_value(product)
        consumption_qty = self.get_consumption_value(product)
        consumption_value = self.get_consumption_value_value(product)
        adjust_qty_positive = self.get_pos_adjustment_qty(product)
        adjust_qty_negative = self.get_neg_adjustment_qty(product)
        adjust_qty_positive_value = self.get_pos_adjustment_qty_value(product)
        adjust_qty_negative_value = self.get_neg_adjustment_qty_value(product)
        adjustment_qty = adjust_qty_positive + adjust_qty_negative
        adjust_qty = abs(adjustment_qty)
        adjust_value = adjust_qty * (adjust_qty_positive_value + adjust_qty_negative_value)
        ending_qty = (beginning_qty + received_qty + mrp_qty + adjust_qty_positive) - (adjust_qty_negative + sale_del_qty + consumption_qty)
        ending_value =ending_qty * self.get_product_cost(product)
        # ending_value = (beginning_value+received_value+mrp_value) -(sale_del_qty_value+consumption_value)
        # if product.id == 15:
        # pdb.set_trace()
        # if not self.is_zero:
        size =''
        if  product.attribute_value_ids:
          for each in product.attribute_value_ids:
            # pdb.set_trace()
            size +=  each.name +','
        else:
          size=''
        if  ending_qty  != 0:
          lst.append({
          'category':product.categ_id.name or 'Untitle',
          'product':product.name +' '+size ,
          'product_lot_num': self.env['stock.production.lot'].search([('product_id','=',product.id)],limit=1).name if product.product_tmpl_id.tracking == 'lot' else ' ',
          'uom' : product.uom_id.name,
          'beginning_qty':beginning_qty,
          'beginning_value':beginning_value,
          'received_qty':received_qty,
          'received_value':received_value,
          'sale_del_qty':sale_del_qty,
          'sale_del_qty_value':sale_del_qty_value,
          'mrp_qty':mrp_qty,
          'mrp_value':mrp_value,
          'consumption_qty':consumption_qty,
          'consumption_value':consumption_value,
          'adjust_qty_positive':adjust_qty_positive,
          'adjust_qty_positive_value':adjust_qty_positive_value,
          'adjust_qty_negative':adjust_qty_negative,
          'adjust_qty_negative_value':adjust_qty_negative_value,
          'adjust_qty':adjust_qty,
          'adjust_value':adjust_value,
          'ending_qty':ending_qty,
          'ending_value':ending_value,
          })
            # else:
            #     lst.append({
          #         'category': product.categ_id.name or 'Untitle',
          #         'product':product.name,
          #         'product_lot_num': self.env['stock.production.lot'].search([('product_id','=',product.id)],limit=1).name if product.product_tmpl_id.tracking == 'lot' else ' ',
          #         'uom' : product.uom_id.name,
          #         'beginning_qty':beginning_qty,
          #         'beginning_value':beginning_value,
          #         'received_qty':received_qty,
          #         'received_value':received_value,
          #         'sale_qty':sale_qty,
          #         'sale_del_qty':sale_del_qty,
          #         'sale_del_qty_value':sale_del_qty_value,
          #         # 'sale_value':sale_value,
          #         # 'internal_qty':internal_qty,
          #         # 'internal_value':internal_value,
          #         'mrp_qty':mrp_qty,
          #         'mrp_value':mrp_value,
          #         'consumption_qty':consumption_qty,
          #         'consumption_value':consumption_value,
          #         'adjust_qty_positive':adjust_qty_positive,
          #         'adjust_qty_positive_value':adjust_qty_positive_value,
          #         'adjust_qty_negative':adjust_qty_negative,
          #         'adjust_qty_negative_value':adjust_qty_negative_value,
          #         'adjust_qty':adjust_qty,
          #         'adjust_value':adjust_value,
          #         'ending_qty':ending_qty,
          #         'ending_value':ending_value,
          #     })
      return lst

        
  

    @api.multi
    def export_stock_ledger(self):
        workbook = xlwt.Workbook()
        filename = 'Detailed Stock Summary Report With Values.xls'
        # Style
        main_header_style = easyxf('font:height 400;pattern: pattern solid, fore_color gray25;'
                                   'align: horiz center;font: color black; font:bold True;'
                                   "borders: top thin,left thin,right thin,bottom thin")

        header_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
                              'align: horiz center;font: color black; font:bold True;'
                              "borders: top thin,left thin,right thin,bottom thin")

        group_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
                              'align: horiz left;font: color black; font:bold True;'
                              "borders: top thin,left thin,right thin,bottom thin")

        text_left = easyxf('font:height 150; align: horiz left;' "borders: top thin,bottom thin")
        text_right_bold = easyxf('font:height 200; align: horiz right;font:bold True;' "borders: top thin,bottom thin")
        text_right_bold1 = easyxf('font:height 200; align: horiz right;font:bold True;' "borders: top thin,bottom thin", num_format_str='0.00')
        text_center = easyxf('font:height 150; align: horiz center;' "borders: top thin,bottom thin")
        text_right = easyxf('font:height 150; align: horiz right;' "borders: top thin,bottom thin",
                            num_format_str='0.00')

        worksheet = []
        warehouse_ids = [1]
        for l in range(0, 3):
            worksheet.append(l)
        work=0
        # for warehouse_id in warehouse_ids:
        worksheet[work] = workbook.add_sheet("Stock Summary")
        for i in range(0,1):
            worksheet[work].col(i).width = 140 * 30

        worksheet[work].write_merge(0, 1, 0, 9, 'DETAILED STOCK SUMMARY REPORT', main_header_style)

        worksheet[work].write(4, 0, 'Company', header_style)
        worksheet[work].write(4, 1, 'Location', header_style)
        worksheet[work].write(4, 2, 'Start Date', header_style)
        worksheet[work].write(4, 3, 'End Date', header_style)
        worksheet[work].write(4, 4, 'Generated By', header_style)
        worksheet[work].write(4, 5, 'Generated Date', header_style)



        worksheet[work].write(5, 0, self.company_id.name, text_center)
        worksheet[work].write(5, 1, self.location_id.name or '', text_center)
        start_date = datetime.strptime(str(self.start_date), '%Y-%m-%d').strftime("%d-%m-%Y")
        worksheet[work].write(5, 2, start_date, text_center)
        end_date = datetime.strptime(str(self.end_date), '%Y-%m-%d').strftime("%d-%m-%Y")
        worksheet[work].write(5, 3, end_date, text_center)
        worksheet[work].write(5, 4, self.env.user.name, text_center)
        worksheet[work].write(5, 5, datetime.now().strftime("%d-%m-%Y %H:%M:%S"), text_center)



        tags = [
                'Opening Stock','Opening Stock Value',
                'Purchased','Purchased Value',
                'Manufactured','Manufactured Value',
                'Consumed','Consumed Value',
                'Sales','Sales Value',
                'Postive Adjustment','Postive Adjustment Value',
                'Negative Adjustment','Negative Adjustment Value',
                'Closing Stock ','Closing Stock Value',]

        r = 9
        worksheet[work].write_merge(r, r, 0, 3, 'Product' , header_style)
        worksheet[work].write_merge(r, r, 4, 6, 'Product Category', header_style)
        worksheet[work].write_merge(r, r, 7, 8, 'UOM', header_style)
        c = 9
        for tag in tags:
          worksheet[work].write(r, c, tag, header_style)
          c+=1
        lines=self.get_lines()
        # print("ListSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS",lines)
        if not self.is_group_by_category:
            # pdb.set_trace()
            r=10
            b_qty = r_qty =b_val= s_val=s_qty =a_qty=a_p_qty_val= a_n_qty_val=e_qty= m_qty=a_val=s_del_qty=a_p_qty=a_n_qty=r_val=s_del_val=e_val=m_val=con_qty=con_val= 0
            for line in lines:
                print(line.get('product'))
                b_qty += line.get('beginning_qty')
                b_val += line.get('beginning_value')
                r_qty += line.get('received_qty')
                r_val += line.get('received_value')
                m_qty += line.get('mrp_qty')
                m_val += line.get('mrp_value')
                con_qty += line.get('consumption_qty')
                con_val += line.get('consumption_value')
                s_del_qty += line.get('sale_del_qty')
                s_del_val += line.get('sale_del_qty_value')
                a_p_qty += line.get('adjust_qty_positive')
                a_p_qty_val += line.get('adjust_qty_positive_value')
                a_n_qty += line.get('adjust_qty_negative')
                a_n_qty_val += line.get('adjust_qty_negative_value')
                a_val += line.get('adjust_value')
                e_qty += line.get('ending_qty')
                e_val += line.get('ending_value')
                c = 4
                worksheet[work].write_merge(r, r, 0, 3, line.get('product'), text_left)
                worksheet[work].write_merge(r, r, 4, 6, line.get('category'), text_left)
                worksheet[work].write_merge(r, r, 7, 8, line.get('uom'), text_left)
                c = 9
                worksheet[work].write(r, c, line.get('beginning_qty'), text_right)
                c+=1
                worksheet[work].write(r, c, line.get('beginning_value'), text_right)
                c+=1
                worksheet[work].write(r, c, line.get('received_qty'), text_right)
                c+=1
                worksheet[work].write(r, c, line.get('received_value'), text_right)
                c+=1
                worksheet[work].write(r, c, line.get('mrp_qty'), text_right)
                c += 1
                worksheet[work].write(r, c, line.get('mrp_value'), text_right)
                c += 1
                worksheet[work].write(r, c, line.get('consumption_qty'), text_right)
                c += 1
                worksheet[work].write(r, c, line.get('consumption_value'), text_right)
                c += 1
                worksheet[work].write(r, c, line.get('sale_del_qty'), text_right)
                c += 1
                worksheet[work].write(r, c, line.get('sale_del_qty_value'), text_right)
                c += 1
                worksheet[work].write(r, c, line.get('adjust_qty_positive'), text_right)
                c += 1
                worksheet[work].write(r, c, line.get('adjust_qty_positive_value'), text_right)
                c += 1
                worksheet[work].write(r, c, line.get('adjust_qty_negative'), text_right)
                c += 1
                worksheet[work].write(r, c, line.get('adjust_qty_negative_value'), text_right)
                c += 1
                worksheet[work].write(r, c, line.get('ending_qty'), text_right)
                c+=1
                worksheet[work].write(r, c, line.get('ending_value'), text_right)
                r+=1
            worksheet[work].write_merge(r, r, 0, 8, 'TOTAL', text_right_bold)
            c = 9
            worksheet[work].write(r, c, round(b_qty,2), text_right_bold1)
            c += 1
            worksheet[work].write(r, c, round(b_val,2), text_right_bold1)
            c += 1
            worksheet[work].write(r, c, round(r_qty,2), text_right_bold1)
            c += 1
            worksheet[work].write(r, c, round(r_val,2), text_right_bold1)
            c += 1
            worksheet[work].write(r, c, round(m_qty,2), text_right_bold1)
            c += 1
            worksheet[work].write(r, c, round(m_val,2), text_right_bold1)
            c += 1
            worksheet[work].write(r, c, round(con_qty,2), text_right_bold1)
            c += 1
            worksheet[work].write(r, c, round(con_val,2), text_right_bold1)
            c += 1
            worksheet[work].write(r, c, round(s_del_qty,2), text_right_bold1)
            c += 1
            worksheet[work].write(r, c, round(s_del_val,2), text_right_bold1)
            c += 1
            worksheet[work].write(r, c, round(a_p_qty,2), text_right_bold1)
            c += 1
            worksheet[work].write(r, c, round(a_p_qty_val,2), text_right_bold1)
            c += 1
            worksheet[work].write(r, c, round(a_n_qty,2), text_right_bold1)
            c += 1
            worksheet[work].write(r, c, round(a_n_qty_val,2), text_right_bold1)
            c += 1
            worksheet[work].write(r, c, round(e_qty,2), text_right_bold1)
            c += 1
            worksheet[work].write(r, c, round(e_val,2), text_right_bold1)
            r += 1
            # else:
            #     lines = self.group_by_lines(lines)
            #     r = 9
            #     for l_val in lines:
            #         worksheet[work].write_merge(r, r, 0, 3, l_val.get('category'), group_style)
            #         r+=1
            #         b_qty =b_val= r_val=s_del_val=r_qty =e_val=a_val= s_qty=m_val= i_qty= a_qty= e_qty=m_qty=s_del_qty =a_p_qty=a_n_qty=con_qty=con_val=0
            #         for line in l_val.get('values'):
            #             b_qty += line.get('beginning_qty')
            #             b_val += line.get('beginning_value')
            #             r_qty += line.get('received_qty')
            #             r_val += line.get('received_value')
            #             # s_qty += line.get('sale_qty')
            #             m_qty += line.get('mrp_qty')
            #             m_val += line.get('mrp_value')
            #             s_del_qty += line.get('sale_del_qty')
            #             s_del_val += line.get('sale_del_qty_value')
            #             con_qty += line.get('consumption_qty')
            #             con_val += line.get('consumption_value')
            #             # s_val += lines.get('sale_value')
            #             # i_qty += line.get('internal_qty')
            #             # i_val += line.get('internal_value')
                        
                        
            #             a_p_qty += line.get('adjust_qty_positive')
            #             a_n_qty += line.get('adjust_qty_negative')
            #             a_qty += line.get('adjust_qty')
            #             a_val += line.get('adjust_value')
            #             e_qty += line.get('ending_qty')
            #             e_val += line.get('ending_value')
            #             worksheet[work].write_merge(r, r, 0, 3, line.get('product'), text_left)
            #             c=4
            #             worksheet[work].write(r, c, line.get('beginning_qty'), text_right)
            #             c+=1
            #             worksheet[work].write(r, c, line.get('beginning_value'), text_right)
            #             c+=1
            #             worksheet[work].write(r, c, line.get('received_qty'), text_right)
            #             c+=1
            #             worksheet[work].write(r, c, line.get('received_value'), text_right)
            #             c+=1
            #             # worksheet[work].write(r, c, line.get('sale_qty'), text_right)
            #             # c += 1
            #             worksheet[work].write(r, c, line.get('mrp_qty'), text_right)
            #             c += 1
            #             worksheet[work].write(r, c, line.get('mrp_value'), text_right)
            #             c += 1
            #             worksheet[work].write(r, c, line.get('consumption_qty'), text_right)
            #             c += 1
            #             worksheet[work].write(r, c, line.get('consumption_value'), text_right)
            #             c += 1
            #             worksheet[work].write(r, c, line.get('sale_del_qty'), text_right)
            #             c += 1
            #             worksheet[work].write(r, c, line.get('sale_del_qty_value'), text_right)
            #             c += 1
            #             # worksheet[work].write(r, c, line.get('sale_value'), text_right)
            #             # c += 1
            #             # worksheet[work].write(r, c, line.get('internal_qty'), text_right)
            #             # c += 1
            #             # worksheet[work].write(r, c, line.get('internal_value'), text_right)
            #             # c += 1
            #             worksheet[work].write(r, c, line.get('adjust_qty_positive'), text_right)
            #             c += 1
            #             worksheet[work].write(r, c, line.get('adjust_qty_negative'), text_right)
            #             c += 1
            #             worksheet[work].write(r, c, line.get('adjust_qty'), text_right)
            #             c += 1
            #             worksheet[work].write(r, c, line.get('adjust_value'), text_right)
            #             c += 1
            #             worksheet[work].write(r, c, line.get('ending_qty'), text_right)
            #             c +=1
            #             worksheet[work].write(r, c, line.get('ending_value'), text_right)
            #             r+=1
            #         worksheet[work].write_merge(r, r, 0, 3, 'TOTAL', text_right_bold)
            #         c = 4
            #         worksheet[work].write(r, c, b_qty, text_right_bold1)
            #         c += 1
            #         worksheet[work].write(r, c, b_val, text_right_bold1)
            #         c += 1
            #         worksheet[work].write(r, c, r_qty, text_right_bold1)
            #         c += 1
            #         worksheet[work].write(r, c, r_val, text_right_bold1)
            #         c += 1
            #         worksheet[work].write(r, c, s_qty, text_right_bold1)
            #         c += 1
            #         worksheet[work].write(r, c, m_qty, text_right_bold1)
            #         c += 1
            #         worksheet[work].write(r, c, m_val, text_right_bold1)
            #         c += 1
            #         worksheet[work].write(r, c, con_qty, text_right_bold1)
            #         c += 1
            #         worksheet[work].write(r, c, con_val, text_right_bold1)
            #         c += 1
            #         worksheet[work].write(r, c, s_del_qty, text_right_bold1)
            #         c += 1
            #         worksheet[work].write(r, c, s_del_val, text_right_bold1)
            #         c += 1
            #         # worksheet[work].write(r, c, s_val, text_right_bold1)
            #         # c += 1
            #         worksheet[work].write(r, c, i_qty, text_right_bold1)
            #         c += 1
            #         # worksheet[work].write(r, c, i_val, text_right_bold1)
            #         # c += 1
            #         worksheet[work].write(r, c, m_val, text_right_bold1)
            #         c += 1
            #         worksheet[work].write(r, c, a_p_qty, text_right_bold1)
            #         c += 1
            #         worksheet[work].write(r, c, a_n_qty, text_right_bold1)
            #         c += 1
            #         worksheet[work].write(r, c, a_qty, text_right_bold1)
            #         c += 1
            #         worksheet[work].write(r, c, a_val, text_right_bold1)
            #         c += 1
            #         worksheet[work].write(r, c, e_qty, text_right_bold1)
            #         c += 1
            #         worksheet[work].write(r, c, e_val, text_right_bold1)
            #         r += 1

                # work +=1


        fp = BytesIO()
        workbook.save(fp)
        export_id = self.env['stock.summary.report.excel'].create(
            {'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        fp.close()

        return {
            'view_mode': 'form',
            'res_id': export_id.id,
            'res_model': 'stock.summary.report.excel',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }



class stock_summary_report_excel(models.TransientModel):
    _name = "stock.summary.report.excel"

    excel_file = fields.Binary('Excel Report')
    file_name = fields.Char('Excel File')
