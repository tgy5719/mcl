# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import except_orm
from odoo.exceptions import UserError, AccessError


class HrLoan(models.Model):
    _name = 'hr.loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Loan Request"

    @api.one
    def _compute_loan_amount(self):
        total_paid = 0.0
        for loan in self:
            for line in loan.loan_lines:
                if line.paid:
                    total_paid += line.amount
            self.total_amount = loan.loan_amount + loan.loan_balance_update
            self.total_paid_amount = total_paid
            self.balance_amount = self.total_amount - self.total_paid_amount

    name = fields.Char(string="Loan Name", default="/", readonly=True)
    date = fields.Date(string="Date", default=fields.Date.today(), readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    department_id = fields.Many2one('hr.department', related="employee_id.department_id", readonly=True,
                                    string="Department")
    installment = fields.Integer(string="No Of Installments", default=1)
    payment_date = fields.Date(string="Payment Start Date", required=True, default=fields.Date.today())
    loan_lines = fields.One2many('hr.loan.line', 'loan_id', string="Loan Line", index=True)
    emp_account_id = fields.Many2one('account.account', string="Treasury Account")
    treasury_account_id = fields.Many2one('account.account', string="Loan Account")
    journal_id = fields.Many2one('account.journal', string="Journal")
    company_id = fields.Many2one('res.company', 'Company', readonly=True,
                                 default=lambda self: self.env.user.company_id,
                                 states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    job_position = fields.Many2one('hr.job', related="employee_id.job_id", readonly=True, string="Job Position")
    loan_amount = fields.Float(string="Loan/Advance Amount", required=True)
    total_amount = fields.Float(string="Total Amount", readonly=True, compute='_compute_loan_amount')
    balance_amount = fields.Float(string="Balance Amount", compute='_compute_loan_amount')
    total_paid_amount = fields.Float(string="Total Paid Amount", compute='_compute_loan_amount')
    
    state = fields.Selection([
        
        ('draft', 'Draft'),
        ('waiting_approval_1', 'Submitted'),
        ('new', 'Ready To Submit'),
        ('computed', 'Computed'),
        ('waiting_approval_2', 'Waiting Approval'),
        ('approve', 'Approved'),
        ('refuse', 'Refused'),
        ('balance', 'Loan Balance Update'),
        ('close', 'Close'),
        ('cancel', 'Canceled'),
    ], string="State", default='draft', track_visibility='onchange', copy=False, )
    loan_type = fields.Selection([('interest_free', 'Interest Free'),
        ('flate_rate', 'Flate Rate'),
        ('yearly_reduction', 'Yearly Reduction'),
        ('monthly_reduction', 'Monthly Reduction'),],string="Loan Type")
    rate_of_interest = fields.Float(string="Rate Of Interest%")
    loan_balance_update = fields.Float(string="Loan Balance", required = True)
    @api.model
    def create(self, values):
        loan_count = self.env['hr.loan'].search_count([('employee_id', '=', values['employee_id']), ('state', '!=', 'close'),('state', '!=', 'refuse'),
                                                       ('balance_amount', '!=', 0)])
        if loan_count:
            raise except_orm('Error!', 'The employee has already a pending installment')
        else:
            values['name'] = self.env['ir.sequence'].get('hr.loan.seq') or ' '
            res = super(HrLoan, self).create(values)
            return res
            

    @api.multi
    def action_refuse(self):
        return self.write({'state': 'refuse'})

    @api.multi
    def action_submit(self):
        var1 = self.loan_amount + self.loan_balance_update
        self.write({'state': 'waiting_approval_1'})
        for data in self:
            if not data.loan_lines:
                raise except_orm('Error!', 'Please Compute installment')
            else:
                self.write({'state': 'waiting_approval_1'})
    """"@api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})"""
    @api.multi
    def action_close(self):
        self.write({'state': 'close'})
    @api.multi
    def action_approve(self):
        self.write({'state': 'approve'})
    @api.multi
    def action_update_loan_balance(self):
        var1 = self.env['hr.employee'].search([])
        for i in var1:
            var2 = self.env['hr.loan'].search([])
            for j in var2:
                if i.name == j.employee_id.name:
                    j.loan_balance_update = i.loan_balance
        self.write({'state': 'draft'})

    @api.multi
    def compute_installment(self):
        """This automatically create the installment the employee need to pay to
        company based on payment start date and the no of installments.
            """
        var1 = self.loan_amount + self.loan_balance_update
        #if self.employee_id.max_loan_amt < var1:
            #raise UserError(_("Loan Amount Exceeds The Maximum Loan Amount"))
        self.write({'state': 'waiting_approval_1'})
        for loan in self:
            date_start = datetime.strptime(str(loan.payment_date), '%Y-%m-%d')
            var1 = loan.loan_amount + loan.employee_id.loan_balance 
            var5 = var1 / loan.installment
            amount = var5
            for i in range(1, loan.installment + 1):
                self.env['hr.loan.line'].create({
                    'date': date_start,
                    'amount': amount,
                    'employee_id': loan.employee_id.id,
                    'loan_id': loan.id})
                date_start = date_start + relativedelta(months=1)
        return True

    @api.multi
    def unlink(self):
        for order in self:
            if order.state in ('approve', 'close','refuse'):
                raise UserError(_('Cannot delete Loan records which are Approved/Closed/Refused'))
        return super(HrLoan, self).unlink()


class InstallmentLine(models.Model):
    _name = "hr.loan.line"
    _description = "Installment Line"

    date = fields.Date(string="Payment Date", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    amount = fields.Float(string="Amount", required=True)
    paid = fields.Boolean(string="Paid")
    loan_id = fields.Many2one('hr.loan', string="Loan Ref.")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.")


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.one
    def _compute_employee_loans(self):
        """This compute the loan amount and total loans count of an employee.
            """
        self.loan_count = self.env['hr.loan'].search_count([('employee_id', '=', self.id)])

    loan_count = fields.Integer(string="Loan Count", compute='_compute_employee_loans')


    
        


