from odoo import api, fields, models,_


class AgedPartnerReport(models.Model):
    _name = "aged.partner.report"
    _description = "Aged Partner Report"


    partner_id = fields.Many2one('res.partner',"Partner")
    sales_persion_id = fields.Many2one('res.users',"Salesperson")
    sales_team_id = fields.Many2one('crm.team',"Sales Team")
    due_date = fields.Date(string='Date')
    ref = fields.Char(string='Document Ref')
    sub_tot_no_due = fields.Integer(string='No Due')
    sub_tot_30 = fields.Integer(string='1-30')
    sub_tot_60 = fields.Integer(string='31-60')
    sub_tot_90 = fields.Integer(string='61-90')
    sub_tot_120 = fields.Integer(string='91-120') 
    sub_tot_180 = fields.Integer(string='120-180') 
    older_amount = fields.Integer('Older')
    total_amount = fields.Integer('Total Amount')


# class ccountMoveLine(models.Model):
#     _inherit = "account.move.line"


#     debit_value = fields.Float("Debit Value")
#     credit_value = fields.Float("Credit Value")


