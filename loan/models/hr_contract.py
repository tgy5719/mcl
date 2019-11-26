from odoo import models, fields, api

class HrContract(models.Model):
	_inherit = 'hr.employee'
	#max_loan_amt = fields.Float(string="Max Loan Amount")
	loan_balance = fields.Float(string="Loan Balance")