# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare

from itertools import groupby


MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}
# Since invoice amounts are unsigned, this is how we know if money comes in or goes out
MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund': -1,
    'in_invoice': -1,
    'out_refund': 1,
}

#on selection of the record in invoice
class account_register_payments(models.TransientModel):
	_inherit = "account.register.payments"
	z_analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', required=True,help="The analytic account related to a Invoice.")
	z_analytic_tag_ids = fields.Many2many('account.analytic.tag',string='Analytic Tags',copy=True,related="z_analytic_account_id.z_analytic_tag_ids")


class account_payment(models.Model):
	_inherit = "account.payment"

	z_analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', required=True,help="The analytic account related to a Invoice.")
	z_analytic_tag_ids = fields.Many2many('account.analytic.tag',string='Analytic Tags',copy=True,related="z_analytic_account_id.z_analytic_tag_ids")



	def _get_move_vals(self, journal=None):
		journal = journal or self.journal_id
		return {
		'date': self.payment_date,
		'ref': self.communication or '',
		'company_id': self.company_id.id,
		'journal_id': journal.id,
		'z_analytic_account_id':self.z_analytic_account_id.id,
        }
	
	def _get_shared_move_line_vals(self, debit, credit, amount_currency, move_id, invoice_id=False):
		analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in self.z_analytic_tag_ids]
		return {
            'partner_id': self.payment_type in ('inbound', 'outbound') and self.env['res.partner']._find_accounting_partner(self.partner_id).id or False,
            'invoice_id': invoice_id and invoice_id.id or False,
            'move_id': move_id,
            'debit': debit,
            'credit': credit,
            'amount_currency': amount_currency or False,
            'payment_id': self.id,
            'journal_id': self.journal_id.id,
            'analytic_tag_ids': analytic_tag_ids,
        }

	def _get_counterpart_move_line_vals(self, invoice=False):
		analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in self.z_analytic_tag_ids]
		if self.payment_type == 'transfer':
			name = self.name
		else:
			name = ''
			if self.partner_type == 'customer':
				if self.payment_type == 'inbound':
					name += _("Customer Payment")
				elif self.payment_type == 'outbound':
					name += _("Customer Credit Note")
			elif self.partner_type == 'supplier':
				if self.payment_type == 'inbound':
					name += _("Vendor Credit Note")
				elif self.payment_type == 'outbound':
					name += _("Vendor Payment")
			if invoice:
				name += ': '
				for inv in invoice:
					if inv.move_id:
						name += inv.number + ', '
				name = name[:len(name)-2]
		return {
            'name': name,
            'account_id': self.destination_account_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
            'analytic_tag_ids': analytic_tag_ids,
		}