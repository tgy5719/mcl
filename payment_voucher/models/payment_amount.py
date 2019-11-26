from odoo.exceptions import UserError
from odoo import api, fields, models, _

class PaymentVoucher(models.Model):
    _inherit = "account.payment"

    amount_in_words = fields.Char(compute='_calc_amt_in_words')

    @api.depends('amount_in_words','amount')
    def _calc_amt_in_words(self):
        for line in self:
            ones = ['zero','One','Two','Three','Four','Five','Six','Seven','Eight','Nine']
            tens = ['zero','Ten','Twenty','Thirty','Fourty','Fifty','Sixty','Seventy','Eighty','Ninety']
            teens = ['Ten','Eleven','Twelve','Thirteen','Fourteen','Fifteen','Sixteen','Seventeen','Eighteen','Ninteen']
            place_values_IND = ['','','Hundred and ','Thousand ','','Lakh ','','Crore ','']
            
            
            cur_major = 'Rupees'
            cur_minor = 'Paise'
            

            def num_to_wrd_IND(number):
                words=''
                for d in number:
                    d = int(d)
                    words += ones[d]+' '

                words = words.split(' ')
                words.pop()

                for t in range(len(number)-5,-1,-2):
                    words[t] = tens[int(number[t])]
                    if number[t] == '1':
                        words[t] = teens[int(number[t+1])]
                        words[t+1] = ''

                words[len(number)-2] = tens[int(number[len(number)-2])]
                if number[len(number)-2] == '1':
                    words[len(number)-2] = teens[int(number[len(number)-1])]
                    words[len(number)-1] = ''

                words = words[::-1]
                for pl in range(len(words)):
                    if words[pl] == 'zero':
                        words[pl] = ''
                    elif words[pl] == '':
                        words[pl] += place_values_IND[pl]
                    else:
                        words[pl] += ' '+place_values_IND[pl]
                words = words[::-1]

                number=''
                for word in words:
                    number += word

                return number


            number = line.amount
            number = str(number).split('.')

            if len(number[1]) == 1:
                number[1]+='0'

            number_whole = number_fract = ''

            number_whole = num_to_wrd_IND(number[0])+cur_major
            if number[1] != '00':
                number_whole += ' and '
                number_fract = num_to_wrd_IND(number[1])+cur_minor

            line.amount_in_words = number_whole+number_fract