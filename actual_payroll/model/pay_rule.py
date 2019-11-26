from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

from odoo.addons import decimal_precision as dp

class HrSalaryRule(models.Model):
	_inherit = 'hr.salary.rule'

	name = fields.Char(required=True, translate=True)
	code = fields.Char(required=True,
        help="The code of salary rules can be used as reference in computation of other rules. "
             "In that case, it is case sensitive.")
	sequence = fields.Integer(required=True, index=True, default=5,
        help='Use to arrange calculation sequence')
	quantity = fields.Char(default='1.0',
        help="It is used in computation for percentage and fixed amount. "
             "For e.g. A rule for Meal Voucher having fixed amount of "
             u"1€ per worked day can have its quantity defined in expression "
             "like worked_days.WORK100.number_of_days.")
	category_id = fields.Many2one('hr.salary.rule.category', string='Category', required=True)
	condition_select_1 = fields.Selection([
		('none', 'Always True'),
		('range', 'Range'),
		('python', 'Python Expression')
		], string="Condition Based on", default='none', required=True)
	condition_range_1 = fields.Char(string='Range Based on', default='contract.wage',
    	help='This will be used to compute the % fields values; in general it is on basic,'
    	'but you can also use categories code fields in lowercase as a variable names '
    	'(hra, ma, lta, etc.) and the variable basic.')
	condition_python_1 = fields.Text(string='Python Condition', required=True,
		default='''
                    # Available variables:
                    #----------------------
                    # payslip: object containing the payslips
                    # employee: hr.employee object
                    # contract: hr.contract object
                    # rules: object containing the rules code (previously computed)
                    # categories: object containing the computed salary rule categories (sum of amount of all rules belonging to that category).
                    # worked_days: object containing the computed worked days
                    # inputs: object containing the computed inputs

                    # Note: returned value have to be set in the variable 'result'

                    result = rules.NET > categories.NET * 0.10''',
        help='Applied this rule for calculation if condition is true. You can specify condition like basic > 1000.')
	condition_range_min_1 = fields.Float(string='Minimum Range', help="The minimum amount, applied for this rule.")
	condition_range_max_1 = fields.Float(string='Maximum Range', help="The maximum amount, applied for this rule.")

	actual_select = fields.Selection([
		('percentage', 'Percentage (%)'),
		('fix', 'Fixed Amount'),
		('code', 'Python Code'),
		], string='Actual Type', index=True, required=True, default='fix', help="The computation method for the rule amount.")
	actual_fix = fields.Float(string='Fixed Amount', digits=dp.get_precision('Payroll'))
	actual_percentage = fields.Float(string='Percentage (%)', digits=dp.get_precision('Payroll Rate'),
		help='For example, enter 50.0 to apply a percentage of 50%')
	actual_python_compute = fields.Text(string='Python Code',
		default='''
                    # Available variables:
                    #----------------------
                    # payslip: object containing the payslips
                    # employee: hr.employee object
                    # contract: hr.contract object
                    # rules: object containing the rules code (previously computed)
                    # categories: object containing the computed salary rule categories (sum of amount of all rules belonging to that category).
                    # worked_days: object containing the computed worked days.
                    # inputs: object containing the computed inputs.

                    # Note: returned value have to be set in the variable 'result'

                    result = contract.wage * 0.10''')
	actual_percentage_base = fields.Char(string='Percentage based on', help='result will be affected to a variable')


	@api.multi
	def _compute_rule_1(self, localdict):
		"""
		:param localdict: dictionary containing the environement in which to compute the rule
		:return: returns a tuple build as the base/amount computed, the quantity and the rate
		:rtype: (float, float, float)
		"""
		self.ensure_one()
		if self.actual_select == 'fix':
			try:
				return self.actual_fix, float(safe_eval(self.quantity, localdict)), 100.0
			except:
				raise UserError(_('Wrong quantity defined for salary rule %s (%s).') % (self.name, self.code))
		elif self.actual_select == 'percentage':
			try:
				return (float(safe_eval(self.actual_percentage_base, localdict)),
                        float(safe_eval(self.quantity, localdict)),
                        self.actual_percentage)
			except:
				raise UserError(_('Wrong percentage base or quantity defined for salary rule %s (%s).') % (self.name, self.code))
		else:
			try:
				safe_eval(self.actual_python_compute, localdict, mode='exec', nocopy=True)
				return float(localdict['result']), 'result_qty' in localdict and localdict['result_qty'] or 1.0, 'result_rate' in localdict and localdict['result_rate'] or 100.0
			except:
				raise UserError(_('Wrong python code defined for salary rule %s (%s).') % (self.name, self.code))

	@api.multi
	def _satisfy_condition_1(self, localdict):
		"""
		@param contract_id: id of hr.contract to be tested
		@return: returns True if the given rule match the condition for the given contract. Return False otherwise.
		"""
		self.ensure_one()

		if self.condition_select_1 == 'none':
			return True
		elif self.condition_select_1 == 'range':
			try:
				result = safe_eval(self.condition_range_1, localdict)
				return self.condition_range_min_1 <= result and result <= self.condition_range_max_1 or False
			except:
				raise UserError(_('Wrong range condition defined for salary rule %s (%s).') % (self.name, self.code))
		else:  # python code
			try:
				safe_eval(self.condition_python_1, localdict, mode='exec', nocopy=True)
				return 'result' in localdict and localdict['result'] or False
			except:
				raise UserError(_('Wrong python condition defined for salary rule %s (%s).') % (self.name, self.code))