# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo import api, fields, models, _

class PurchaseOrder(models.Model):
	_inherit = "purchase.order"
	amount_total_number = fields.Char(string = 'amount_word')
	words = fields.Char(string = 'words')
	upp = fields.Monetary(string ='upps')
	iii = fields.Float(string = 'iii')
	man = fields.Char(string = 'gante')
	munich = fields.Char('Total (In Words)')
	rey = fields.Char('wwe')
	kook = fields.Char('ramp')
	munk = fields.Char('munk')
	need_for_speed = fields.Char('nfs')
	smack = fields.Char('smack')
	gun = fields.Char('gun')
	gong = fields.Char('gong')
	strombreaker = fields.Char('strombreaker',store = True,compute = '_cont')
	we = fields.Char('we')
	iii = fields.Float(string = 'iii')
	wwe = fields.Char('wwe')
	gone = fields.Char('gone')
	taal = fields.Float('taal')
	@api.one
	@api.depends('amount_total_number','amount_total','taal','strombreaker')
	def _cont(self):
		cate = str(self.amount_total)
		self.amount_total_number = str(cate)
		self.amount_total = round(self.amount_total)
		self.taal = round(self.amount_total)
		numbe = str(self.taal).split('.')
		money_number = numbe[0]		
		if money_number == 0:
			return None
		positions = [None for i in range(4)]
		key_range = 0
		one_place = ["","One ", "Two ", "Three ", "Four ","Five ", "Six ", "Seven ", "Eight ", "Nine "]
		one_ten_place = ["Ten ", "Eleven ", "Twelve ", "Thirteen ", "Fourteen ","Fifteen ", "Sixteen ", 
						"Seventeen ", "Eighteen ","Nineteen "]
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
				money_number_money_text += " "+one_place[int(hundreds)] +" "+"Hundred "
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
			self.strombreaker = str(money_number_money_text)+" "+"Rupees Only"