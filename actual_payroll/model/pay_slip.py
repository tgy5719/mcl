import time
from datetime import datetime
from datetime import time as datetime_time
from dateutil import relativedelta

import babel

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    _description = 'Pay Slip'

    pay_in_ids = fields.One2many('hr.payslip.inherit','pay_on_id',string='Payslip Lines')


    @api.multi
    def compute_sheet(self):
        for payslip in self:
            number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
            # delete old payslip lines
            payslip.line_ids.unlink()
            payslip.pay_in_ids.unlink()
            # set the list of contract for which the rules have to be applied
            # if we don't give the contract, then the rules to apply should be for all current contracts of the employee
            contract_ids = payslip.contract_id.ids or \
                self.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)
            lines = [(0, 0, line) for line in self._get_payslip_lines(contract_ids, payslip.id)]
            lines_1 = [(0, 0, line) for line in self._get_payslip_lines_1(contract_ids, payslip.id)]
            payslip.write({'line_ids': lines, 'number': number})
            payslip.write({'pay_in_ids': lines_1, 'number': number})
        return True

    @api.multi
    def compute_pay_1(self):
        for payslip in self:
            number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
            # delete old payslip lines
            payslip.pay_in_ids.unlink()
            # set the list of contract for which the rules have to be applied
            # if we don't give the contract, then the rules to apply should be for all current contracts of the employee
            contract_ids = payslip.contract_id.ids or \
                self.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)
            lines_1 = [(0, 0, line) for line in self._get_payslip_lines_1(contract_ids, payslip.id)]
            payslip.write({'pay_in_ids': lines_1, 'number': number})
        return True

    @api.multi
    def compute_pay(self):
        for payslip in self:
            contract = self.env['hr.contract'].search([('employee_id','=',payslip.employee_id.id)])
            if contract:
                for line in payslip.line_ids:
                    if line.code == "BASIC":
                        line.actual_amount = contract.wage
                    if line.code == "SA":
                        line.actual_amount = contract.supplementary_allowance
                    if line.code == "DA":
                        line.actual_amount = contract.dearness_allowance_id
                    if line.code == "GROSS":
                        line.actual_amount = contract.wage + contract.supplementary_allowance + contract.dearness_allowance_id

    @api.model
    def _get_payslip_lines_1(self, contract_ids, payslip_id):
        def _sum_salary_rule_category_1(localdict, category, actual_amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category_1(localdict, category.parent_id, actual_amount)
            localdict['categories'].dict[category.code] = category.code in localdict['categories'].dict and localdict['categories'].dict[category.code] + actual_amount or actual_amount
            return localdict

        class BrowsableObject_1(object):
            def __init__(self, employee_id, dict, env):
                self.employee_id = employee_id
                self.dict = dict
                self.env = env

            def __getattr__(self, attr):
                return attr in self.dict and self.dict.__getitem__(attr) or 0.0

        class InputLine_1(BrowsableObject_1):
            """a class that will be used into the python code, mainly for usability purposes"""
            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""
                    SELECT sum(actual_amount) as sum
                    FROM hr_payslip as hp, hr_payslip_input as pi
                    WHERE hp.employee_id = %s AND hp.state = 'done'
                    AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
                    (self.employee_id, from_date, to_date, code))
                return self.env.cr.fetchone()[0] or 0.0

        class WorkedDays_1(BrowsableObject_1):
            """a class that will be used into the python code, mainly for usability purposes"""
            def _sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""
                    SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours
                    FROM hr_payslip as hp, hr_payslip_worked_days as pi
                    WHERE hp.employee_id = %s AND hp.state = 'done'
                    AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
                    (self.employee_id, from_date, to_date, code))
                return self.env.cr.fetchone()

            def sum(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[0] or 0.0

            def sum_hours(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[1] or 0.0

        class Payslips_1(BrowsableObject_1):
            """a class that will be used into the python code, mainly for usability purposes"""

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)
                            FROM hr_payslip as hp, hr_payslip_line as pl
                            WHERE hp.employee_id = %s AND hp.state = 'done'
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.pay_on_id AND pl.code = %s""",
                            (self.employee_id, from_date, to_date, code))
                res = self.env.cr.fetchone()
                return res and res[0] or 0.0

        #we keep a dict with the result because a value can be overwritten by another rule with the same code
        result_dict = {}
        rules_dict = {}
        worked_days_dict = {}
        inputs_dict = {}
        blacklist = []
        payslip = self.env['hr.payslip'].browse(payslip_id)
        for worked_days_line in payslip.worked_days_line_ids:
            worked_days_dict[worked_days_line.code] = worked_days_line
        for input_line in payslip.input_line_ids:
            inputs_dict[input_line.code] = input_line

        categories = BrowsableObject_1(payslip.employee_id.id, {}, self.env)
        inputs = InputLine_1(payslip.employee_id.id, inputs_dict, self.env)
        worked_days = WorkedDays_1(payslip.employee_id.id, worked_days_dict, self.env)
        payslips = Payslips_1(payslip.employee_id.id, payslip, self.env)
        rules = BrowsableObject_1(payslip.employee_id.id, rules_dict, self.env)

        baselocaldict = {'categories': categories, 'rules': rules, 'payslip': payslips, 'worked_days': worked_days, 'inputs': inputs}
        #get the ids of the structures on the contracts and their parent id as well
        contracts = self.env['hr.contract'].browse(contract_ids)
        if len(contracts) == 1 and payslip.struct_id:
            structure_ids = list(set(payslip.struct_id._get_parent_structure().ids))
        else:
            structure_ids = contracts.get_all_structures()
        #get the rules of the structure and thier children
        rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
        #run the rules by sequence
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]
        sorted_rules = self.env['hr.salary.rule'].browse(sorted_rule_ids)

        for contract in contracts:
            employee = contract.employee_id
            localdict = dict(baselocaldict, employee=employee, contract=contract)
            for rule in sorted_rules:
                key = rule.code + '-' + str(contract.id)
                localdict['result'] = None
                localdict['result_qty'] = 1.0
                localdict['result_rate'] = 100
                #check if the rule can be applied
                if rule._satisfy_condition_1(localdict) and rule.id not in blacklist:
                    #compute the amount of the rule
                    actual_amount, qty, rate = rule._compute_rule_1(localdict)
                    #check if there is already a rule computed with that code
                    previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                    #set/overwrite the amount computed for this rule in the localdict
                    tot_rule = actual_amount * qty * rate / 100.0
                    localdict[rule.code] = tot_rule
                    rules_dict[rule.code] = rule
                    #sum the amount for its salary category
                    localdict = _sum_salary_rule_category_1(localdict, rule.category_id, tot_rule - previous_amount)
                    #create/overwrite the rule in the temporary results
                    result_dict[key] = {
                        'salary_rule_id': rule.id,
                        'contract_id': contract.id,
                        'name': rule.name,
                        'code': rule.code,
                        'category_id': rule.category_id.id,
                        'sequence': rule.sequence,
                        'appears_on_payslip': rule.appears_on_payslip,
                        'condition_select_1': rule.condition_select_1,
                        'condition_python_1': rule.condition_python_1,
                        'condition_range_1': rule.condition_range_1,
                        'condition_range_min_1': rule.condition_range_min_1,
                        'condition_range_max_1': rule.condition_range_max_1,
                        'actual_select': rule.actual_select,
                        'actual_fix': rule.actual_fix,
                        'actual_python_compute': rule.actual_python_compute,
                        'actual_percentage': rule.actual_percentage,
                        'actual_percentage_base': rule.actual_percentage_base,
                        'register_id': rule.register_id.id,
                        'actual_amount': actual_amount,
                        'employee_id': contract.employee_id.id,
                        'quantity': qty,
                        'rate': rate,
                    }
                else:
                    #blacklist this rule and its children
                    blacklist += [id for id, seq in rule._recursive_search_of_rules()]

        return list(result_dict.values())

    def get_salary_line_total(self, code):
        self.ensure_one()
        line = self.pay_in_ids.filtered(lambda line: line.code == code)
        if line:
            return line[0].total
        else:
            return 0.0


class HrPayslipInherit(models.Model):
    _name = "hr.payslip.inherit"
    _inherit = 'hr.salary.rule'
    _order = 'contract_id, sequence'

    pay_on_id = fields.Many2one('hr.payslip',string='Pay Slip')
    salary_rule_id = fields.Many2one('hr.salary.rule', string='Rule', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    contract_id = fields.Many2one('hr.contract', string='Contract', required=True, index=True)
    rate = fields.Float(string='Rate (%)', digits=dp.get_precision('Payroll Rate'), default=100.0)
    actual_amount = fields.Float(digits=dp.get_precision('Payroll'))
    quantity = fields.Float(digits=dp.get_precision('Payroll'), default=1.0)
    total_id = fields.Float(compute='_compute_total_1', string='Total', digits=dp.get_precision('Payroll'), store=True)

    @api.depends('quantity', 'actual_amount', 'rate')
    def _compute_total_1(self):
        for line in self:
            line.total_id = float(line.quantity) * line.actual_amount * line.rate / 100

    
class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    actual_amount = fields.Float(help="It is used in computation. For e.g. A rule for sales having "
        "1% commission of basic salary for per product can defined in expression "
        "like result = inputs.SALEURO.amount * contract.wage*0.01.")