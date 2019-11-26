import psycopg2
from odoo.exceptions import UserError
from odoo import api, fields, models, tools, _
class HrPayslip(models.Model):
	_inherit = 'hr.payslip'

	tall = fields.Float('tall',store = True)
	stromb = fields.Char('stromb',compute = '_cats')
	amount_total_number = fields.Char(string = 'amount_word',store=True)
	net_total = fields.Float(string='Net Total',store=True)
	amount_total = fields.Float(sting='amt total',store=True)
	field = fields.Float(string='field')

	@api.multi
	@api.depends('amount_total_number','net_total','tall','stromb')
	def _cats(self):
		for line in self:
			cate = line.net_total
			line.amount_total_number = str(cate)
			line.net_total = round(line.net_total)
			line.tall = round(line.net_total)
			numbe = str(line.tall).split('.')
			money_number = numbe[0]
			if money_number == 0:
				return None
			positions = [None for i in range(4)]
			key_range = 0
			one_place = ["","One ", "Two ", "Three ", "Four ","Five ", "Six ", "Seven ", "Eight ", "Nine "]
			one_ten_place = ["Ten ", "Eleven ", "Twelve ", "Thirteen ", "Fourteen ","Fifteen ", "Sixteen ","Seventeen ", "Eighteen ","Nineteen "]
			ten_place = ["Twenty ", "Thirty ", "Forty ", "Fifty ","Sixty ", "Seventy ", "Eighty ", "Ninety "]
			name_of_number = ["Thousand ","Lakh ","Crore "]
			money_number_money_text = ''
			positions[0] = (int)(money_number) % 1000  # unit
			positions[1] = (int)(money_number)// 1000
			positions[2] = int(money_number) // 100000
			positions[1] = int(positions[1]-100*positions[2]) #thasounds
			positions[3] = int(money_number)//10000000 #crore
			positions[2] = int(positions[2]-100*positions[3]) #lakh
			for counter in range(3, 0, -1):
				if positions[counter] != 0:
					key_range = counter
					break
			for i in range(key_range, -1, -1):
				if positions[i] == 0:
					continue
				ones = positions[i]%10 #ones
				tens = int(positions[i])//10
				hundreds = positions[i]//100#hundred
				tens = tens - 10*hundreds #ten
				if (hundreds > 0):
					money_number_money_text += " "+one_place[int(hundreds)]+" " +"Hundred "
				if (ones > 0 or tens > 0) :
					if(hundreds > 0 and i == 0):
						money_number_money_text += " and "
					if (tens == 0):
						money_number_money_text += " "+one_place[int(ones)]+" "
					elif (tens == 1):
						money_number_money_text += " "+one_ten_place[int(ones)]+" "
					else:
						money_number_money_text += " "+ten_place[int(tens -2)] + one_place[int(ones)]+" "
					if (i != 0):
						money_number_money_text += " "+name_of_number[int(i - 1)]+" "
			money_number_money_text = money_number_money_text 
			line.stromb = str(money_number_money_text)+" "+" Rupees Only"

	'''@api.multi
	@api.depends('amount_total_number','net_total','tall','stromb')
	def _cagee(self):
		self.amount_total_number = str(self.net_total)
	@api.one
	@api.depends('net_total','amount_total','field')
	def _calc_net_sal(self):
		for line in self.line_ids:
			if line.name == "Net Salary":
				self.write({'amount_total': line.total})
				self.net_total = line.total'''
				
	'''@api.multi
	def compute_sheet(self):
		for line in self.line_ids:
			self.net_total = line.browse(self).id.id
			return self.write({'amount_total': self.net_total})'''
	@api.multi
	def compute_sheet(self):
		for payslip in self:
			number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
			# delete old payslip lines
			payslip.line_ids.unlink()
			# set the list of contract for which the rules have to be applied
			# if we don't give the contract, then the rules to apply should be for all current contracts of the employee
			contract_ids = payslip.contract_id.ids or \
				self.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)
			lines = [(0, 0, line) for line in self._get_payslip_lines(contract_ids, payslip.id)]
			payslip.write({'line_ids': lines, 'number': number})
		for lines in self:
			for line in lines.line_ids:
				if line.name == "Net Salary":
					self.write({'net_total': line.total})
					return True 

class Job1(models.Model):
	_inherit = 'hr.employee'

	employee_code = fields.Char(string='Code')


