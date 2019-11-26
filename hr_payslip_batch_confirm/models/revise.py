# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero

class HrPayslipRun(models.Model):
	_inherit = 'hr.payslip.run'

	z_post_entry = fields.Boolean(string="Ready to post entry",default=False,copy=False)
	z_posted_entry = fields.Boolean(string="Posted",default=False,copy=False)
	z_total_amount = fields.Float(string="Total Value")
	z_analytic_account_id_ref = fields.Char(string="Analytic Account ref")
	z_analytic_account_id_con = fields.Char(string="Analytic Account Consolidated")

	z_payslip_account_lines = fields.One2many('hr.payslip.account.lines','payslip_account_line_id')

	z_debit_ref = fields.Char(string="Debit Ref")
	z_credit_ref = fields.Char(string="Credit Ref")



	@api.multi
	def compute_sheet(self):
		payslip_ids = self.env['hr.payslip'].search([('date_from', '=', self.date_start),('date_to','=',self.date_end),('state','=','draft')])
		#fetching the debit and credit accounts of the employees in batch processing
		if payslip_ids:
			#for fetching credit list
			credit_lists = []
			#for fetching debit list
			debit_lists = []
			#for appending the ids to the list from the credit and debit accounts
			credit = debit = 0
			#loop to fetch the credit and debit account ids and display and also for the further computation
			for slip in payslip_ids:
				for lines in slip.details_by_salary_rule_category:
					if lines.salary_rule_id.account_credit:
						credit = lines.salary_rule_id.account_credit.id
					if lines.salary_rule_id.account_debit:
						debit = lines.salary_rule_id.account_debit.id

					debit_lists.append(debit)
					credit_lists.append(credit)
					self.z_credit_ref = list(set(credit_lists))
					self.z_debit_ref = list(set(debit_lists))

			#list to fetch the analytic account ids
			lists = []
			#append the analytic accoun ids from a loop
			acc = 0
			#loop to fetch the analytic account ids and also for the further computation
			for slip in payslip_ids:
				if slip.z_analytic_account_id:
					#adding the analytic account id to a variable 'a'
					acc = slip.z_analytic_account_id.id
					#appending the variable to lists
					lists.append(acc)
					#adding the lists to the field for further computations
					self.z_analytic_account_id_ref = lists
					#To remove  the repeated values in list, using the set functionality and adding to new field
					self.z_analytic_account_id_con = list(set(lists))


			#loop to create a lines using analytic account (Not required)
			for deb in set(debit_lists):
				for line in set(lists):
					total = neg_total = 0
					debit_account_id = credit_account_id = 0
					payslip_id = self.env['hr.payslip'].search([('date_from', '=', self.date_start),('date_to','=',self.date_end),('state','=','draft'),('z_analytic_account_id','=',line)])
					for slip in payslip_id:
						for lines in slip.details_by_salary_rule_category:
							if lines.salary_rule_id.account_debit.id == deb:
								debit_account_id = lines.salary_rule_id.account_debit.id
								#credit_account_id = lines.salary_rule_id.account_credit.id
								if lines.total > 0:
									total += lines.total
								
					#for debit value
					if total:
						pay_lines_debit = self.env['hr.payslip.account.lines']
						move_lines_debit={}
						move_lines_debit = {
							'payslip_account_line_id':self.id,
							'z_debit': total,
							'z_analytic_account_id':line,
							'z_account_debit':debit_account_id,
						}
						pay_lines_debit.create(move_lines_debit)
			#
			for cr in set(credit_lists):
				for line in set(lists):
					total = neg_total = 0
					debit_account_id = credit_account_id = 0
					payslip_id = self.env['hr.payslip'].search([('date_from', '=', self.date_start),('date_to','=',self.date_end),('state','=','draft'),('z_analytic_account_id','=',line)])
					for slip in payslip_id:
						for lines in slip.details_by_salary_rule_category:
							if lines.salary_rule_id.account_credit.id == cr:
								#debit_account_id = lines.salary_rule_id.account_debit.id
								credit_account_id = lines.salary_rule_id.account_credit.id
								if lines.total > 0:
									total += lines.total
								

					#for credit value
					if total:
						pay_lines_credit = self.env['hr.payslip.account.lines']
						move_lines_credit={}
						move_lines_credit = {
							'payslip_account_line_id':self.id,
							'z_credit': total,
							'z_analytic_account_id':line,
							'z_account_credit':credit_account_id,

						}
						pay_lines_credit.create(move_lines_credit)

			for deb in set(debit_lists):
				for line in set(lists):
					total = neg_total = 0
					debit_account_id = credit_account_id = 0
					payslip_id = self.env['hr.payslip'].search([('date_from', '=', self.date_start),('date_to','=',self.date_end),('state','=','draft'),('z_analytic_account_id','=',line)])
					for slip in payslip_id:
						for lines in slip.details_by_salary_rule_category:
							if lines.salary_rule_id.account_debit.id == deb:
								debit_account_id = lines.salary_rule_id.account_debit.id
								credit_account_id = lines.salary_rule_id.account_credit.id
								if lines.total < 0:
									neg_total += lines.total
					#for debit value
					if neg_total:
						pay_lines_debit = self.env['hr.payslip.account.lines']
						move_lines_debit={}
						move_lines_debit = {
							'payslip_account_line_id':self.id,
							'z_credit': -(neg_total),
							'z_analytic_account_id':line,
							'z_account_credit':debit_account_id,
						}
						pay_lines_debit.create(move_lines_debit)

			for cr in set(credit_lists):
				for line in set(lists):
					total = neg_total = 0
					debit_account_id = credit_account_id = 0
					payslip_id = self.env['hr.payslip'].search([('date_from', '=', self.date_start),('date_to','=',self.date_end),('state','=','draft'),('z_analytic_account_id','=',line)])
					for slip in payslip_id:
						for lines in slip.details_by_salary_rule_category:
							if lines.salary_rule_id.account_credit.id == cr:
								#debit_account_id = lines.salary_rule_id.account_debit.id
								credit_account_id = lines.salary_rule_id.account_credit.id
								if lines.total < 0:
									neg_total += lines.total

					#for credit value
					if neg_total:
						pay_lines_credit = self.env['hr.payslip.account.lines']
						move_lines_credit={}
						move_lines_credit = {
							'payslip_account_line_id':self.id,
							'z_debit': -(neg_total),
							'z_analytic_account_id':line,
							'z_account_debit':credit_account_id,

						}
						pay_lines_credit.create(move_lines_credit)


		
			for slip in payslip_ids:
				#slip.state='done'
				for line in slip.input_line_ids:
					if line.loan_line_id:
						line.loan_line_id.action_paid_amount()
			#self.z_post_entry = True
			

		#passing the data to journal entries
	@api.multi
	def post_entry(self):
		for line in self:
			line_ids = []
			date = line.date_start
			name = _('Payslip of %s') % (line.name)
			move_dict = {
                'narration': name,
                'ref': line.name,
                'journal_id': line.journal_id.id,
                'date': date,
                'state':'draft'
            }
			for lines in line.z_payslip_account_lines:
				if lines.z_account_debit:
					debit_line = (0, 0, {
                        'name': line.name,
                        'account_id': lines.z_account_debit.id,
                        'analytic_account_id':lines.z_analytic_account_id.id,
                        'journal_id': line.journal_id.id,
                        'date': date,
                        'debit': lines.z_debit,
                        })
					line_ids.append(debit_line)
				if lines.z_account_credit:
					credit_line = (0, 0, {
                        'name': line.name,
                        'account_id': lines.z_account_credit.id,
                        'analytic_account_id':lines.z_analytic_account_id.id,
                        'journal_id': line.journal_id.id,
                        'date': date,
                        'credit': lines.z_credit,
                        })
					line_ids.append(credit_line)
			move_dict['line_ids'] = line_ids
			move = self.env['account.move'].create(move_dict)
			move.post()
			self.z_posted_entry = True



			
		'''for line in self.slip_ids:
									precision = self.env['decimal.precision'].precision_get('Payroll')
						
									for slip in line:
										line_ids = []
										debit_sum = 0.0
										credit_sum = 0.0
										date = slip.date or slip.date_to
						
										name = _('Payslip of %s') % (slip.employee_id.name)
										move_dict = {
							                'narration': name,
							                'ref': slip.number,
							                'journal_id': slip.journal_id.id,
							                'date': date,
							                }
										for line in slip.details_by_salary_rule_category:
											amount = slip.credit_note and -line.total or line.total
											if float_is_zero(amount, precision_digits=precision):
												continue
											debit_account_id = line.salary_rule_id.account_debit.id
											credit_account_id = line.salary_rule_id.account_credit.id
						
											if debit_account_id:
												debit_line = (0, 0, {
							                        'name': line.name,
							                        'partner_id': line._get_partner_id(credit_account=False),
							                        'account_id': debit_account_id,
							                        'journal_id': slip.journal_id.id,
							                        'date': date,
							                        'debit': amount > 0.0 and amount or 0.0,
							                        'credit': amount < 0.0 and -amount or 0.0,
							                        'analytic_account_id': line.salary_rule_id.analytic_account_id.id,
							                        'tax_line_id': line.salary_rule_id.account_tax_id.id,
							                        })
												line_ids.append(debit_line)
												debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']
						
											if credit_account_id:
												credit_line = (0, 0, {
							                        'name': line.name,
							                        'partner_id': line._get_partner_id(credit_account=True),
							                        'account_id': credit_account_id,
							                        'journal_id': slip.journal_id.id,
							                        'date': date,
							                        'debit': amount < 0.0 and -amount or 0.0,
							                        'credit': amount > 0.0 and amount or 0.0,
							                        'analytic_account_id': line.salary_rule_id.analytic_account_id.id,
							                        'tax_line_id': line.salary_rule_id.account_tax_id.id,
							                        })
												line_ids.append(credit_line)
												credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
						
										if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
											acc_id = slip.journal_id.default_credit_account_id.id
											if not acc_id:
												raise UserError(_('The Expense Journal "%s" has not properly configured the Credit Account!') % (slip.journal_id.name))
											adjust_credit = (0, 0, {
							                    'name': _('Adjustment Entry'),
							                    'partner_id': False,
							                    'account_id': acc_id,
							                    'journal_id': slip.journal_id.id,
							                    'date': date,
							                    'debit': 0.0,
							                    'credit': debit_sum - credit_sum,
							                    })
											line_ids.append(adjust_credit)
						
										elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
											acc_id = slip.journal_id.default_debit_account_id.id
											if not acc_id:
												raise UserError(_('The Expense Journal "%s" has not properly configured the Debit Account!') % (slip.journal_id.name))
											adjust_debit = (0, 0, {
							                    'name': _('Adjustment Entry'),
							                    'partner_id': False,
							                    'account_id': acc_id,
							                    'journal_id': slip.journal_id.id,
							                    'date': date,
							                    'debit': credit_sum - debit_sum,
							                    'credit': 0.0,
							                    })
											line_ids.append(adjust_debit)
										move_dict['line_ids'] = line_ids
										move = self.env['account.move'].create(move_dict)
										slip.write({'move_id': move.id, 'date': date})
										move.post()
										slip.state='done'
									self.z_post_entry = True'''

class HrPayslipAccountLine(models.Model):
	_name = 'hr.payslip.account.lines'

	payslip_account_line_id = fields.Many2one('hr.payslip.run',string="Payslip account Line")
	z_analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account',help="The analytic account related to a Invoice.")
	z_debit = fields.Float(string="Debit")
	z_credit = fields.Float(string="Credit")
	z_account_debit = fields.Many2one('account.account', 'Debit Account', domain=[('deprecated', '=', False)])
	z_account_credit = fields.Many2one('account.account', 'Credit Account', domain=[('deprecated', '=', False)])