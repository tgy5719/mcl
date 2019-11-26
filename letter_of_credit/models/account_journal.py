from odoo import api, fields, models, _

class AccountMove(models.Model):
	_inherit = 'account.move'

	z_lc_no = fields.Many2one('account.letter.credit',string="LC Reference")
	z_ext_doc = fields.Char(string="External Reference")
