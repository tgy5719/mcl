# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.



from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
from datetime import timedelta
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
from xlwt import easyxf
from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError,Warning
import xlwt
import io
import base64

import datetime
import math
import pdb

class SalesSummary(models.TransientModel):
    _name = "sales.summary"
    _description = "Sales Summary Report"

    date_start = fields.Date(string="Start Date", required=True, default=fields.Date.today)
    date_end = fields.Date(string="End Date", required=True, default=fields.Date.today)
    sales_report = fields.Binary('Sales REPORT')
    file_name = fields.Char('File Name')
    sales_report_printed = fields.Boolean('Sales Report Printed')

    @api.multi
    @api.constrains('date_start')
    def _code_constrains(self):
        if self.date_start > self.date_end:
            raise ValidationError(_("'Start Date' must be before 'End Date'"))
    @api.multi
    def get_summary(self):
        workbook = xlwt.Workbook()
        amount_tot = 0
        column_heading_style = easyxf('font:height 210;font:bold True;align: horiz center;')
        worksheet = workbook.add_sheet('Sales Report', cell_overwrite_ok=True)
        right_alignment= easyxf('font:height 200; align: horiz right;')
        center_alignment= easyxf('font:height 200; align: horiz center;')
        left_alignment= easyxf('font:height 200; align: horiz left;')
        current_company_name = self.env.user.company_id.name
        report_heading = " Sales Register from" + ' ' + datetime.datetime.strftime(self.date_start, '%d-%m-%Y') + ' '+ 'To' + ' '+ datetime.datetime.strftime( self.date_end, '%d-%m-%Y')
        worksheet.write_merge(1, 1, 6, 12, report_heading, easyxf('font:height 250;font:bold True;align: horiz center;'))
        worksheet.write_merge(2, 2, 6, 12, current_company_name, easyxf('font:height 250;font:bold True;align: horiz center;'))
        worksheet.write(3, 0, _('SL NO'), column_heading_style)
        worksheet.write(3, 1, _('Invoice No'), column_heading_style) 
        worksheet.write(3, 2, _('Invoice Date'), column_heading_style)
        worksheet.write(3, 3, _('Customer Code'), column_heading_style)
        worksheet.write(3, 4, _('Customer Name'), column_heading_style)
        worksheet.write(3, 5, _('GST No'), column_heading_style)
        worksheet.write(3, 6, _('Customer State'), column_heading_style)
        worksheet.write(3, 7, _('Customer City'), column_heading_style)
        worksheet.write(3, 8, _('Sale Order No'), column_heading_style)
        worksheet.write(3, 9, _('Sales Order Date'), column_heading_style)
        worksheet.write(3, 10, _('Picking ID'), column_heading_style)
        worksheet.write(3, 11, _('Product Category 1'), column_heading_style)
        worksheet.write(3, 12, _('Product Category 2'), column_heading_style)
        worksheet.write(3, 13, _('Product Category 3'), column_heading_style)
        worksheet.write(3, 14, _('Product Code'), column_heading_style)
        worksheet.write(3, 15, _('Product Name'), column_heading_style)
        worksheet.write(3, 16, _('HSN Code'), column_heading_style)
        worksheet.write(3, 17, _('BOX'), column_heading_style)
        worksheet.write(3, 18, _('Uom'), column_heading_style)
        worksheet.write(3, 19, _('Qty Invoiced'), column_heading_style)
        worksheet.write(3, 20, _('Unit Price'), column_heading_style)
        worksheet.write(3, 21, _('Pricing Branch'), column_heading_style)
        worksheet.write(3, 22, _('Branch Selling Price'), column_heading_style)
        worksheet.write(3, 23, _('Diff B/W IP - BSP'), column_heading_style)
        worksheet.write(3, 24, _('Amount Exclusive Tax'), column_heading_style)
        worksheet.write(3, 25, _('Insurance / Freight'), column_heading_style)
        worksheet.write(3, 26, _('CGST Rate %'), column_heading_style)
        worksheet.write(3, 27, _('SGST Rate %'), column_heading_style)
        worksheet.write(3, 28, _('CGST Amount'), column_heading_style)
        worksheet.write(3, 29, _('SGST Amount'), column_heading_style)
        worksheet.write(3, 30, _('Total Tax Amount'), column_heading_style)
        worksheet.write(3, 31, _('Amount Inclusive Tax'), column_heading_style)
        worksheet.write(3, 32, _('COGS '), column_heading_style)
        worksheet.write(3, 33, _('COGS Contribution '), column_heading_style)
        worksheet.write(3, 34, _('GP Margin '), column_heading_style)
        worksheet.write(3, 35, _('GP Margin % '), column_heading_style)
        worksheet.write(3, 36, _('Sales Person'), column_heading_style)
        worksheet.write(3, 37, _('Sales Team'), column_heading_style)
        worksheet.write(3, 38, _('Sales Team Manager'), column_heading_style)
        worksheet.write(3, 39, _('Sales Office'), column_heading_style)
        worksheet.write(3, 40, _('Analytical Account Id'), column_heading_style)
        worksheet.col(1).width = 4500
        worksheet.col(2).width = 4500
        worksheet.col(3).width = 4500
        worksheet.col(4).width = 4500
        worksheet.col(5).width = 4500
        worksheet.col(6).width = 4500
        worksheet.col(7).width = 4500
        worksheet.col(8).width = 4500
        worksheet.col(9).width = 4500
        worksheet.col(10).width = 4500
        worksheet.col(11).width = 4500
        worksheet.col(12).width = 4500
        worksheet.col(28).width = 4500
        worksheet.row(1).height = 300
        worksheet.row(2).height = 300
        partner_dict = {}
        final_value = {}
        row = 4

        for wizard in self:
            domain = [('date_start','>=',wizard.date_start),('date_start','<=',wizard.date_end),('company_id','=',self.env.user.company_id.id)]
            total = 0
            count  = 1
            tot_sgst = tot_cgst = tot_gst = tot_amount = tot_cogs_amount = tot_with_tax_amount = tot_gp_amount =  0.0
            
            for invoice in self.env['account.invoice'].search([('type','=','out_invoice'),('state','in', ('open','paid')),('date_invoice','>=',wizard.date_start),('date_invoice','<=',wizard.date_end)]):
                sgst_rate= sgst_amount= cgst_rate= cgst_amount= 0.0
                for invoice_line in invoice.invoice_line_ids:
                    
                    for each_line in invoice_line.invoice_line_tax_ids:
                        for each_tax in each_line.children_tax_ids:
                            sgst_rate  = each_tax.amount if each_tax.amount else ' '
                            cgst_rate  = each_tax.amount if each_tax.amount else ' '
                    sale_order_id = self.env['sale.order'].search([('name','=',invoice.origin)])
                    picking_id = self.env['stock.picking'].search([('origin','=',invoice.origin)],limit=1)
                    product_catg_name =  ' '
                    sub_total_amount = round(invoice_line.price_unit*invoice_line.quantity,2)
                    sgst_amount = round(sub_total_amount*sgst_rate/100,2)
                    cgst_amount = round(sub_total_amount*cgst_rate/100,2)
                    gst_total = round(sgst_amount+cgst_amount,2)
                    total_with_tax_amount = round(sub_total_amount-gst_total,2)
                    cogs_amount = round(sub_total_amount *(80/100),2)
                    bsp =0.0
                    gp_amount = round(sub_total_amount-cogs_amount,2)
                    price_list_id = self.env['product.pricelist.item'].search([('pricelist_id','=',invoice.pricelist_id.id),('product_id','=',invoice_line.product_id.id)])
                    if price_list_id:
                        bsp = price_list_id.fixed_price or 0.0
                    diff_bsp = round(bsp - invoice_line.price_unit,2)
                    freight =0.0
                    if invoice_line.product_id.type == 'service':
                        freight = invoice_line.price_unit
                        diff_bsp = 0.0

                    worksheet.write(row, 0, count,  center_alignment)
                    worksheet.write(row, 1, invoice.number, center_alignment)
                    worksheet.write(row, 2, datetime.datetime.strftime(invoice.date_invoice, '%d-%m-%Y'),center_alignment)
                    worksheet.write(row, 3, invoice.partner_id.ref if invoice.partner_id.ref else '',center_alignment)
                    worksheet.write(row, 4, invoice.partner_id.name, left_alignment)
                    worksheet.write(row, 5, invoice.partner_id.vat, center_alignment)
                    worksheet.write(row, 6, invoice.partner_id.state_id.name, center_alignment)
                    worksheet.write(row, 7, invoice.partner_id.city, left_alignment)
                    worksheet.write(row, 8, sale_order_id.name, center_alignment)
                    worksheet.write(row, 9, datetime.datetime.strftime(sale_order_id.confirmation_date, '%d-%m-%Y'), center_alignment)
                    worksheet.write(row, 10, picking_id.name, center_alignment)
                    path_ids=invoice_line.product_id.product_tmpl_id.categ_id.parent_path.split('/')
                    cont_row = 0
                    col = 11
                    for path in path_ids:
                        if len(path):
                            if int(path) and cont_row <= 3:
                                categ_ids = self.env['product.category'].search([('id','=',int(path))])
                                worksheet.write(row, col, categ_ids.name, left_alignment)
                                cont_row += 1
                                col += 1
                    worksheet.write(row, 14, invoice_line.product_id.default_code, left_alignment)
                    worksheet.write(row, 15, invoice_line.product_id.name, left_alignment)
                    worksheet.write(row, 16, invoice_line.product_id.l10n_in_hsn_code if invoice_line.product_id.l10n_in_hsn_code else ' ', center_alignment)
                    worksheet.write(row, 17, invoice_line.z_no_of_package, right_alignment)
                    worksheet.write(row, 18, invoice_line.uom_id.name, center_alignment)
                    worksheet.write(row, 19, invoice_line.quantity, right_alignment)
                    worksheet.write(row, 20, invoice_line.price_unit, right_alignment)
                    worksheet.write(row, 21, invoice.pricelist_id.name, left_alignment)
                    worksheet.write(row, 22, bsp, right_alignment)
                    worksheet.write(row, 23, diff_bsp, right_alignment)
                    worksheet.write(row, 24, sub_total_amount, right_alignment)
                    worksheet.write(row, 25, freight, right_alignment)
                    worksheet.write(row, 26, cgst_rate, right_alignment)
                    worksheet.write(row, 27, sgst_rate, right_alignment)
                    worksheet.write(row, 28, cgst_amount, right_alignment)
                    worksheet.write(row, 29, sgst_amount, right_alignment)
                    worksheet.write(row, 30, gst_total, right_alignment)
                    worksheet.write(row, 31, total_with_tax_amount, right_alignment)
                    worksheet.write(row, 32, cogs_amount, right_alignment)
                    worksheet.write(row, 33, '80%', center_alignment)
                    worksheet.write(row, 34, gp_amount, right_alignment)
                    worksheet.write(row, 35, '20%', center_alignment)
                    worksheet.write(row, 36, invoice.user_id.name, left_alignment)
                    worksheet.write(row, 37, invoice.team_id.name, left_alignment)
                    worksheet.write(row, 38, invoice.team_id.user_id.name, left_alignment)
                    worksheet.write(row, 39, invoice.z_sale_ofc.name, left_alignment)
                    worksheet.write(row, 40, invoice_line.account_analytic_id.name, left_alignment)
                    row += 1
                    count += 1
                    tot_sgst += sgst_amount
                    tot_cgst += cgst_amount
                    tot_gst += gst_total
                    tot_amount += sub_total_amount
                    tot_with_tax_amount += total_with_tax_amount
                    tot_cogs_amount += cogs_amount
                    tot_gp_amount += gp_amount
                worksheet.write(row, 24, tot_amount, column_heading_style)
                worksheet.write(row, 28, tot_cgst, column_heading_style)
                worksheet.write(row, 29, tot_sgst, column_heading_style)
                worksheet.write(row, 30, tot_gst, column_heading_style)
                worksheet.write(row, 31, tot_with_tax_amount, column_heading_style)
                worksheet.write(row, 32, tot_cogs_amount, column_heading_style)
                worksheet.write(row, 34, tot_gp_amount, column_heading_style)

        fp = io.BytesIO()
        workbook.save(fp)
        excel_file = base64.encodestring(fp.getvalue())
        self.sales_report = excel_file
        self.file_name = 'Sales Register.xls'
        self.sales_report_printed = True
        fp.close()

        return {
        'view_mode': 'form',
        'res_id': self.id,
        'res_model': 'sales.summary',
        'view_type': 'form',
        'type': 'ir.actions.act_window',
        'context': self.env.context,
        'target': 'new',
                   }