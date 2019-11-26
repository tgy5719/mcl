from odoo.exceptions import UserError
from odoo import api, fields, models, _

class AccountInvoiceDollars(models.Model):
    _inherit = "account.invoice"
    amount_total_words1 = fields.Char('amount_in_words',store=True)
    tal1 = fields.Float('tal',stroe = True)
    strom = fields.Char('strom',store = True)
    word = fields.Char('words',store = True,compute = '_great')
    @api.multi
    @api.depends('amount_total','tal1','strom')
    def _great(self):
        for l in self:
        	cate1 = str(l.amount_total)
        	l.amount_total_number1 = str(cate1)
        	l.amount_total1 = round(l.amount_total)
        	l.tal = round(l.amount_total)
        	numbe1 = str(l.tal).split('.')
        	money_number1 = numbe1[0]
        	if money_number1 == 0:
        		return None
        	positions1 = [None for i in range(4)]
        	key_range1 = 0
        	one_place1 = ["","One ", "Two ", "Three ", "Four ","Five ", "Six ", "Seven ", "Eight ", "Nine"]
        	one_ten_place1 = ["Ten ", "Eleven ", "Twelve ", "Thirteen ", "Fourteen ","Fifteen ", "Sixteen ","Seventeen ", "Eighteen ","Nineteen "]
        	ten_place1 = ["Twenty ", "Thirty ", "Forty ", "Fifty ","Sixty ", "Seventy ", "Eighty ", "Ninety "]
        	name_of_number1 = ["Thousand","Lakh","Crore"]
        	money_number_money_text1 = ''
        	positions1[0] = (int)(money_number1) % 1000  # unit
        	positions1[1] = (int)(money_number1)// 1000
        	positions1[2] = int(money_number1) // 100000
        	positions1[1] = int(positions1[1]-100*positions1[2]) #thasounds
        	positions1[3] = int(money_number1)//10000000 #crore
        	positions1[2] = int(positions1[2]-100*positions1[3]) #lakh
        	for counter1 in range(3, 0, -1):
        		if positions1[counter1] != 0:
        			key_range1 = counter1
        			break
        	for i in range(key_range1, -1, -1):
        		if positions1[i] == 0:
        			continue
        		ones = positions1[i]%10 #ones
        		tens = int(positions1[i])//10
        		hundreds = positions1[i]//100#hundred
        		tens = tens - 10*hundreds #ten
        		if (hundreds > 0):
        			money_number_money_text1 += " "+one_place1[int(hundreds)]+" "+"Hundred "
        		if (ones > 0 or tens > 0) :
        			if(hundreds > 0 and i == 0):
        				money_number_money_text1 += " and "
        			if (tens == 0):
        				money_number_money_text1 += " "+one_place1[int(ones)]+" "
        			elif (tens == 1):
        				money_number_money_text1 += " "+one_ten_place1[int(ones)]+" "
        			else:
        				money_number_money_text1 += " "+ten_place1[int(tens -2)] + one_place1[int(ones)]+" "
        			if (i != 0):
        				money_number_money_text1 += " "+name_of_number1[int(i - 1)]+" "
        		money_number_money_text1 = money_number_money_text1 
        		l.word = str(money_number_money_text1)+" "+" Dollars Only"
        
