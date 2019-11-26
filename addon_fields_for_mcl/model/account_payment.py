from odoo import api, fields, models,_

class account_payment(models.Model):
    _inherit = "account.payment"

    z_voucher_no = fields.Char('Ref/Voucher No',store=True)