from odoo import models, fields, api,_

class CloseLoan(models.TransientModel):
    _name = 'close.loan'
    reason = fields.Many2one('loan.close', string="Reason",required=True)
    
    @api.multi
    def send_mail(self):
        order = self.env['hr.loan'].search([])
        for var in order:
            order_2 = self.env['hr.employee'].search([])
            for var2 in order_2:
                if var2.name == var.employee_id.name:
                    var2.loan_balance = var.balance_amount
        return var.write({'state': 'close'})

class LoanClose(models.Model):
    _name = 'loan.close'
    name = fields.Char('Name')
        