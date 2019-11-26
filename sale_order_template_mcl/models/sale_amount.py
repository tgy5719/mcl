from odoo.exceptions import UserError
from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = "sale.order"
    tall = fields.Float('tall',stroe = True)
    stromb = fields.Char('stromb',store = True,track_visibility='always',compute = 'change_amount_words')
    amount_total_number = fields.Char(string = 'amount_word')
    amount_stromb = fields.Char('Total amount',store = True,track_visibility='always',compute = '_cats')
    ext_doc_no = fields.Char(string='External Document No', store=True)
    @api.multi
    @api.depends('amount_total_number','amount_total','tall','pricelist_id')
    def _cats(self):
        for line in self:
            cate = str(line.amount_total)
            line.amount_total_number = str(cate)
            line.amount_total = round(line.amount_total)
            line.tall = round(line.amount_total)
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
            line.amount_stromb = str(money_number_money_text)
            #line.stromb = str(money_number_money_text)+" "+" Dollars Only"
    
    @api.depends('pricelist_id','amount_stromb')
    def change_amount_words(self):
        for line in self:
            if line.pricelist_id.id == 1:
                line.stromb = str(line.amount_stromb)+" "+" Rupees Only"
            else:
                line.stromb = str(line.amount_stromb)+" "+" Rupees Only"
