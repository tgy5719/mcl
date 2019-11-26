from odoo.exceptions import UserError
from odoo import api, fields, models, _

class DelivSlip(models.Model):
    _inherit = "stock.picking"
    amount_total_words = fields.Char('amount_in_words',store=True)
    tal = fields.Float('tal',store = True)
    strom = fields.Char('strom',store = True,compute = '_change_amount_words1')
    word = fields.Char('words',store = True,compute = '_geatt')

    transporter = fields.Char(string="Dispatched Through")
    e_way_no = fields.Char(string='E-way Bill No', store=True)
    z_delivered_to = fields.Char(string="Destination")
    vehicle = fields.Many2many('fleet.vehicle',string='Vehicle')
    ext_vehicle_no = fields.Char(string="External Vehicle No.")

    z_total_amount = fields.Float(string="total amount", compute='_calculate_price_total', store=True)

    @api.depends('move_ids_without_package','move_ids_without_package.z_price_total')
    def _calculate_price_total(self):
        for l in self:
            l.z_total_amount = sum(line.z_price_total for line in l.move_ids_without_package)


    
    @api.multi
    @api.depends('z_total_amount','tal')
    def _geatt(self):
        for l in self:
            cate = str(l.z_total_amount)
            l.amount_total_number = str(cate)
            l.z_total_amount = round(l.z_total_amount)
            l.tal = round(l.z_total_amount)
            numbe = str(l.tal).split('.')
            money_number = numbe[0]
            if money_number == 0:
                return None
            positions = [None for i in range(4)]
            key_range = 0
            one_place = ["","One ", "Two ", "Three ", "Four ","Five ", "Six ", "Seven ", "Eight ", "Nine"]
            one_ten_place = ["Ten ", "Eleven ", "Twelve ", "Thirteen ", "Fourteen ","Fifteen ", "Sixteen ","Seventeen ", "Eighteen ","Nineteen "]
            ten_place = ["Twenty ", "Thirty ", "Forty ", "Fifty ","Sixty ", "Seventy ", "Eighty ", "Ninety "]
            name_of_number = ["Thousand","Lakh","Crore"]
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
                    money_number_money_text += " "+one_place[int(hundreds)]+" "+"Hundred "
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
                l.word = str(money_number_money_text)
                
    @api.depends('word')
    def _change_amount_words1(self):
        for line in self:
            line.strom = str(line.word)+" "+" Rupees Only"