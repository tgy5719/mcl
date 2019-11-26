# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.



from odoo import api, fields, models, _
from datetime import date, timedelta
import datetime

from odoo.exceptions import UserError
import pdb

class AgedPartnerReport(models.TransientModel):
    _name = "aged.partner.wizard"
    _description = "Aged Partner Report"



    report_date = fields.Date('As Of')

    @api.multi
    def partner_count(self):
        invoice_obj= self.env['account.invoice']
        payment_obj= self.env['account.payment']


        if self.env['aged.partner.report'].search([]):
            for each in self.env['aged.partner.report'].search([]):
                each.unlink()



        payment_ids = payment_obj.search([('partner_type','=','customer'),('state','=','posted')])
        for payment in payment_ids:
            account_move_line_id = self.env['account.move.line'].search([('payment_id','=',payment.id),('amount_residual','<',0)])
            date_30 =  datetime.datetime.strptime((self.report_date-timedelta(days=30)).isoformat(), '%Y-%m-%d').date()
            date_60 = datetime.datetime.strptime((self.report_date-timedelta(days=60)).isoformat(), '%Y-%m-%d').date()
            date_90 = datetime.datetime.strptime((self.report_date-timedelta(days=90)).isoformat(), '%Y-%m-%d').date() 
            date_120 = datetime.datetime.strptime((self.report_date-timedelta(days=120)).isoformat(), '%Y-%m-%d').date()
            date_180 = datetime.datetime.strptime((self.report_date-timedelta(days=180)).isoformat(), '%Y-%m-%d').date()
            print(payment,account_move_line_id)
            # pdb.set_trace()
            # if len(account_move_line_id) >=1:
            for each in account_move_line_id:
                if each.id:

                    sub_tot_no_due = each.amount_residual if each.date >= self.report_date else 0.0
                    sub_tot_30 = each.amount_residual if each.date >= date_30 and each.date < self.report_date else 0.0
                    sub_tot_60 = each.amount_residual if each.date >= date_60 and each.date < date_30 else 0.0
                    sub_tot_90 = each.amount_residual if each.date >= date_90 and each.date < date_60 else 0.0
                    sub_tot_120 = each.amount_residual if each.date >= date_120 and each.date < date_90 else 0.0
                    sub_tot_180 = each.amount_residual if each.date >= date_180  and each.date < date_120 else 0.0
                    sub_tot_max = each.amount_residual if each.date <date_180  else 0.0
                    total_amount = sub_tot_no_due+sub_tot_30+sub_tot_60+sub_tot_90+sub_tot_120+sub_tot_180+sub_tot_max

                   

                    new_pay_id = self.env['aged.partner.report'].create({
                                        'partner_id':payment.partner_id.id,
                                        'ref':payment.name,
                                        'due_date':payment.payment_date,
                                        'sub_tot_no_due': sub_tot_no_due,
                                        'sub_tot_30': sub_tot_30,
                                        'sub_tot_60': sub_tot_60,
                                        'sub_tot_90': sub_tot_90,
                                        'sub_tot_120': sub_tot_120,
                                        'sub_tot_180': sub_tot_180,
                                        'older_amount': sub_tot_max,
                                        'total_amount': total_amount,
                                        
                                        })





        for invoice in invoice_obj.search([('type','=', 'out_invoice'),('residual','>',0)]):
            date_30 =  datetime.datetime.strptime((self.report_date-timedelta(days=30)).isoformat(), '%Y-%m-%d').date()
            date_60 = datetime.datetime.strptime((self.report_date-timedelta(days=60)).isoformat(), '%Y-%m-%d').date()
            date_90 = datetime.datetime.strptime((self.report_date-timedelta(days=90)).isoformat(), '%Y-%m-%d').date() 
            date_120 = datetime.datetime.strptime((self.report_date-timedelta(days=120)).isoformat(), '%Y-%m-%d').date()
            date_180 = datetime.datetime.strptime((self.report_date-timedelta(days=180)).isoformat(), '%Y-%m-%d').date()

            due_30_amount= due_60_amount= due_90_amount= due_120_amount= due_180_amount= due_max_amount= no_due_amount=sub_tot_max= 0

            # if invoice.id == 4:
            #     pdb.set_trace()
            sub_tot_no_due = invoice.residual if invoice.date_due >= self.report_date else 0.0
            sub_tot_30 = invoice.residual if invoice.date_due >= date_30 and invoice.date_due < self.report_date else 0.0
            sub_tot_60 = invoice.residual if invoice.date_due >= date_60 and invoice.date_due < date_30 else 0.0
            sub_tot_90 = invoice.residual if invoice.date_due >= date_90 and invoice.date_due < date_60 else 0.0
            sub_tot_120 = invoice.residual if invoice.date_due >= date_120 and invoice.date_due < date_90 else 0.0
            sub_tot_180 = invoice.residual if invoice.date_due >= date_180  and invoice.date_due < date_120 else 0.0
            sub_tot_max = invoice.residual if invoice.date_due <date_180  else 0.0
            total_amount = sub_tot_no_due+sub_tot_30+sub_tot_60+sub_tot_90+sub_tot_120+sub_tot_180+sub_tot_max
            # due_30_amount = invoice.residual if invoice.date_due >=+sub_tot_90 date_30 and invoice.date_due < self.report_date else 0.0
            # sub_tot_no_due = invoice.residual if invoice.date_due >= self.report_date else 0.0
            # no_due_invoice_ids = invoice_obj.search([('id','=', invoice.id),('date_due','>=',self.report_date)])
            # no_due_amount =0.0
            # if no_due_invoice_ids:
            #     for each_no in no_due_invoice_ids:
            #         no_due_amount += each_no.residual
            # if not no_due_invoice_ids:
            #     due_30_invoice_ids = invoice_obj.search([('id','=', invoice.id),('date_due','>=',date_30)])
            #     due_60_invoice_ids = invoice_obj.search([('id','=', invoice.id),('date_due','>',date_30),('date_due','<=',date_60),])
            #     due_90_invoice_ids = invoice_obj.search([('id','=', invoice.id),('date_due','>',date_60),('date_due','<=',date_90),])
            #     due_120_invoice_ids =invoice_obj.search([('id','=', invoice.id),('date_due','>',date_90),('date_due','<=',date_120),])
            #     due_180_invoice_ids =invoice_obj.search([('id','=', invoice.id),('date_due','>',date_120),('date_due','<=',date_180),])
            #     due_max_invoice_ids =invoice_obj.search([('id','=', invoice.id),('date_due','>',date_180)])
            #     # due_30_invoice_ids = invoice_obj.search([('date_due','=',self.report_date),('type','=', 'out_invoice')])

            #     # due_invoice_ids= due_30_invoice_ids+daysue_60_invoice_ids+due_90_invoice_ids+due_120_invoice_ids+due_120_invoice_ids+due_180_invoice_ids
                
            #     if due_30_invoice_ids:
            #         for each_30 in due_30_invoice_ids:
            #             due_30_amount += each_30.residual
            #     if due_60_invoice_ids:
            #         for each_60 in due_60_invoice_ids:
            #             due_60_amount += each_60.residual
            #     if due_90_invoice_ids:
            #         for each_90 in due_90_invoice_ids:
            #             due_90_amount += each_90.residual
            #     if due_120_invoice_ids:
            #         for each_120 in due_120_invoice_ids:
            #             due_120_amount += each_120.residual
            #     if due_180_invoice_ids:
            #         for each_180 in due_180_invoice_ids:
            #             due_180_amount += each_180.residual
            #     if due_max_invoice_ids:
            #         for each_max in due_max_invoice_ids:
            #             due_max_amount += each_max.residual



            

            new_id = self.env['aged.partner.report'].create({
                                'partner_id':invoice.partner_id.id,
                                'ref':invoice.number,
                                'sales_persion_id':invoice.user_id.id,
                                'sales_team_id':invoice.team_id.id,
                                'due_date':invoice.date_due,
                                'sub_tot_no_due': sub_tot_no_due,
                                'sub_tot_30': sub_tot_30,
                                'sub_tot_60': sub_tot_60,
                                'sub_tot_90': sub_tot_90,
                                'sub_tot_120': sub_tot_120,
                                'sub_tot_180': sub_tot_180,
                                'older_amount': sub_tot_max,
                                'total_amount': total_amount,
                                
                                })
        
        tree_view_id = self.env.ref('aged_partner_report.view_aged_partner_tree').id
        # from_view_id = self.env.ref('production_allocation_report.view_assigned_employee_form').id
        return {
                'name': 'Aged Partner',
                # 'view_type': 'form',
                'view_mode': 'tree',
                'views': [(tree_view_id, 'tree')],
                'res_model': 'aged.partner.report',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'context': dict(self.env.context)
                }

