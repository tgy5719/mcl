# -*- coding: utf-8 -*-

from odoo import models, fields,api


class AccountAccount(models.Model):
    _inherit = 'account.account'

    compacted = fields.Boolean('Compacte entries.', help='If flagged, no details will be displayed in the Standard report, only compacted amounts.', default=False)
    type_third_parties = fields.Selection([('no', 'No'), ('supplier', 'Supplier'), ('customer', 'Customer')], string='Third Partie', required=True, default='no')
class AccountAccount(models.Model):
	_inherit = 'account.move.line'
	zuser_id = fields.Many2one('crm.team',string = 'Saleperson',compute = "flow_saleteam",store = True)
	@api.multi
	@api.depends('invoice_id')
	def flow_saleteam (self):
		for line in self:
			line.zuser_id = line.invoice_id.team_id.id
# class AccountAccount(models.Model):
# 	_inherit = 'account.move'
# 	user_id = fields.Many2one('res.users','Saleperson')
# class AccountAccount(models.Model):
# 	_inherit = 'account.invoice'
# 	saleperson = fields.Many2one('res.users'string = 'Saleperson',related = 'user_id.name')