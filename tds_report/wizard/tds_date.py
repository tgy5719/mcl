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

class TdsWizard(models.TransientModel):
    _name = 'tds_report.report.tds'

    date_start = fields.Date(string="Start Date", required=True, default=fields.Date.today)
    date_end = fields.Date(string="End Date", required=True, default=fields.Date.today)
    analysis_report = fields.Binary('TDS REPORT')
    file_name = fields.Char('File Name')
    invoice_report_printed = fields.Boolean('TDS Report Printed')

    @api.multi
    @api.constrains('date_start')
    def _code_constrains(self):
        if self.date_start > self.date_end:
            raise ValidationError(_("'Start Date' must be before 'End Date'"))

    @api.multi
    def action_print_timesheet_analysis(self):
        workbook = xlwt.Workbook()
        sheetbook = xlwt.Workbook()
        amount_tot = 0
        column_heading_style = easyxf('font:height 210;font:bold True;')
        worksheet = workbook.add_sheet('TDS REPORT', cell_overwrite_ok=True)
        sheet = sheetbook.add_sheet('yes', cell_overwrite_ok=True)
        date_start = self.date_start
        date_end = self.date_end 
        salary = "TDS Report for "
        worksheet.write(2, 6, 'Murudeshwar Ceramics Ltd.', easyxf('font:height 250;font:bold True;align: horiz center;'))
        # worksheet.write(4, 6, salary +'  '+ date_start + '  to  '+ date_end, easyxf('font:height 200;font:bold True;align: horiz center;'))
        worksheet.write(6, 0, _('SL NO'), column_heading_style)
        worksheet.write(6, 1, _('POSTING DATE'), column_heading_style) 
        worksheet.write(6, 2, _('VENDOR BILL NO.'), column_heading_style)
        worksheet.write(6, 3, _('STATUS'), column_heading_style)
        worksheet.write(6, 4, _('VENDOR REF.'), column_heading_style)
        worksheet.write(6, 5, _('PARTY CODE'), column_heading_style)
        worksheet.write(6, 6, _('VENDOR NAME'), column_heading_style)
        worksheet.write(6, 7, _('DEDUCTEE PAN NO.'), column_heading_style)
        worksheet.write(6, 8, _('ASSESSEE CODE'), column_heading_style)
        worksheet.write(6, 9, _('TDS SEC'), column_heading_style)
        worksheet.write(6, 10, _('TDS %'), column_heading_style)
        worksheet.write(6, 11, _('TDS BASE AMOUNT'), column_heading_style)
        worksheet.write(6, 12, _('TDS AMOUNT'), column_heading_style)
        worksheet.col(0).width = 4500
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
        partner_dict = {}
        final_value = {}
        row = 7

        for wizard in self:
            domain = [('date_start','>=',wizard.date_start),('date_start','<=',wizard.date_end),('company_id','=',self.env.user.company_id.id)]
            total = 0
            count  = 0
            for tds_name in self.env['account.invoice'].search([('type','=','in_invoice'),('state','in', ('open','paid')),('date','>=',wizard.date_start),('date','<=',wizard.date_end)]):
                for line_1 in tds_name:
                    ass_no = self.env['account.nod.confg'].search(
                        [('partner_id','=',line_1.partner_id.id)])
                    for line_2 in ass_no:
                        for line_3 in self.env['account.invoice.line'].search([('invoice_id','=',line_1.id),]):
                            for line_5 in line_3.tds_nod_id.name:
                                for line_4 in self.env['account.tds.mapping'].search([('name','=',line_5.name)]):
                                    count = count + 1
                                    work = 0

                                    partner_dict.update({line_3.id : [line_3]})
                                    worksheet.write(row, 0, count,  easyxf('font:height 200; align: horiz left;'))
                                    worksheet.write(row, 1, line_1.date, easyxf('font:height 200; align: horiz left;'))
                                    worksheet.write(row, 2, line_1.number, easyxf('font:height 200;align: horiz left;'))
                                    worksheet.write(row, 3, line_1.state, easyxf('font:height 200;align: horiz left;'))
                                    worksheet.write(row, 4, line_1.reference, easyxf('font:height 200;align: horiz left;'))
                                    worksheet.write(row, 5, line_1.partner_id.ref, easyxf('font:height 200;align: horiz left;'))
                                    worksheet.write(row, 6, line_1.partner_id.name, easyxf('font:height 200;align: horiz left;'))
                                    worksheet.write(row, 7, line_1.partner_id.pan_no, easyxf('font:height 200;align: horiz left;'))
                                    worksheet.write(row, 8, line_2.assesse_code.name, easyxf('font:height 200;align: horiz left;'))
                                    worksheet.write(row, 9, line_4.tds_group.tds_section.name, easyxf('font:height 200;align: horiz left;'))
                                    worksheet.write(row, 10, line_4.tds, easyxf('font:height 200;align: horiz left;'))
                                    worksheet.write(row, 11, line_3.price_subtotal, easyxf('font:height 200;align: horiz left;'))
                                    worksheet.write(row, 12, line_3.total_tds_amount, easyxf('font:height 200;align: horiz left;'))
                                    row += 1

            fp = io.BytesIO()
            workbook.save(fp)
            excel_file = base64.encodestring(fp.getvalue())
            wizard.analysis_report = excel_file
            wizard.file_name = 'TDS REPORT.xls'
            wizard.invoice_report_printed = True
            fp.close()

            return {
            'view_mode': 'form',
            'res_id': wizard.id,
            'res_model': 'tds_report.report.tds',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': self.env.context,
            'target': 'new',
                       }
    @api.multi
    def get_report(self):
        """Call when button 'Get Report' is clicked.
        """
        data = {
        'ids': self.ids,
        'model': self._name,
        'form': {
        'date_start': self.date_start,
        'date_end': self.date_end,
            },}
        return self.env.ref('tds_report.action_report_tds').report_action(self,data)

class TdsAbstract(models.AbstractModel):
    """Abstract Model for report template.
    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """
    _name = 'report.tds_report.report_template_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = datetime.datetime.strptime(data['form']['date_start'], DATE_FORMAT)
        date_end = datetime.datetime.strptime(data['form']['date_end'], DATE_FORMAT)
        
        if not data.get('form'):
            raise UserError("Form content is missing, this report cannot be printed.")
        docs = []

        tds_name = self.env['account.invoice'].search(
            [('type','=','in_invoice'),
            ('state','in',('open','paid')),
            ('date','>=',date_start.strftime(DATE_FORMAT)),
            ('date','<=',date_end.strftime(DATE_FORMAT))])
        for line_1 in tds_name:
            ass_no = self.env['account.nod.confg'].search(
                [('partner_id','=',line_1.partner_id.id)])
            for line_2 in ass_no:
                for line_3 in self.env['account.invoice.line'].search([
                    ('invoice_id','=',line_1.id),
                    ]):
                    for line_5 in line_3.tds_nod_id.name:
                        for line_4 in self.env['account.tds.mapping'].search([('name','=',line_5.name)]):   
                        # tds_p = self.env['account.invoice.line'].search([])
                        # for line_3 in tds_p:
                            docs.append({
                                    'date':line_1.date,
                                    'doc_no':line_1.number,
                                    'state':line_1.state,
                                    'vendor_no':line_1.partner_id.ref,
                                    'partner':line_1.partner_id.name,
                                    'pan_no':line_1.partner_id.pan_no,
                                    'assess_code':line_2.assesse_code.name,
                                    'tds_percent':line_4.tds,
                                    'tds_base':line_3.price_subtotal,
                                    'tds_amount':line_3.total_tds_amount,
                                })
        # map_env = self.env['account.tds.mapping'].search([
        #     ('id','=',nod_name),
        #     ('create_date','>=',date_start.strftime(DATE_FORMAT)),
        #     ('create_date','<=',date_end.strftime(DATE_FORMAT)),
        #     ])
        # acc_inv = map_env.env['account.invoice'].search([('type','=','in_invoice')])
        # for acc_nod_env in acc_inv.env['account.nod.confg.line'].search([]):
        #     docs.append({
        #         'map':map_env.name,
        #         'nod':acc_nod_env.partner_id.name,
        #         })

        # acc_inv = self.env['account.nod.confg.line'].search([])
        # for map_env in acc_inv.env['account.tds.mapping'].search(
        #     [('name','=',nod_name.name),
        #     ('create_date','>=',date_start.strftime(DATE_FORMAT)),
        #     ('create_date','<=',date_end.strftime(DATE_FORMAT))]):
        #     docs.append({
        #         'map': map_env.name
        #         })


        return {
        'doc_ids': data['ids'],
        'doc_model': data['model'],
        'date_start': date_start.strftime(DATE_FORMAT),
        'date_end': date_end.strftime(DATE_FORMAT),
        'docs': docs,
        }