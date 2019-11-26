import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero

class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category'

    z_write_off_account = fields.Many2one('account.account', string='Write Off Account', required=True, domain=[('internal_type','=','other'), ('deprecated', '=', False)], oldname='account_income_recognition_id', help="Account used in the periodical entries, to record a part of the asset as expense.")


class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    def _prepare_move(self, line):
        category_id = line.asset_id.category_id
        account_analytic_id = line.asset_id.account_analytic_id
        analytic_tag_ids = line.asset_id.analytic_tag_ids
        depreciation_date = self.env.context.get('depreciation_date') or line.depreciation_date or fields.Date.context_today(self)
        company_currency = line.asset_id.company_id.currency_id
        current_currency = line.asset_id.currency_id
        prec = company_currency.decimal_places
        amount = current_currency._convert(
            line.amount, company_currency, line.asset_id.company_id, depreciation_date)
        asset_name = line.asset_id.name + ' (%s/%s)' % (line.sequence, len(line.asset_id.depreciation_line_ids))
        move_line_1 = {
            'name': asset_name,
            'account_id': category_id.account_depreciation_id.id,
            'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'partner_id': line.asset_id.partner_id.id,
            'analytic_account_id': account_analytic_id.id if category_id.type == 'sale' else False,
            'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'sale' else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
        }
        move_line_2 = {
            'name': asset_name,
            'account_id': category_id.z_write_off_account.id,
            'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'partner_id': line.asset_id.partner_id.id,
            'analytic_account_id': account_analytic_id.id if category_id.type == 'purchase' else False,
            'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'purchase' else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and line.amount or 0.0,
        }
        move_vals = {
            'ref': line.asset_id.code,
            'date': depreciation_date or False,
            'journal_id': category_id.journal_id.id,
            'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
        }
        return move_vals

        def _prepare_move_grouped(self):
	        asset_id = self[0].asset_id
	        category_id = asset_id.category_id  # we can suppose that all lines have the same category
	        account_analytic_id = asset_id.account_analytic_id
	        analytic_tag_ids = asset_id.analytic_tag_ids
	        depreciation_date = self.env.context.get('depreciation_date') or fields.Date.context_today(self)
	        amount = 0.0
	        for line in self:
	            # Sum amount of all depreciation lines
	            company_currency = line.asset_id.company_id.currency_id
	            current_currency = line.asset_id.currency_id
	            company = line.asset_id.company_id
	            amount += current_currency._convert(line.amount, company_currency, company, fields.Date.today())

	        name = category_id.name + _(' (grouped)')
	        move_line_1 = {
	            'name': name,
	            'account_id': category_id.account_depreciation_id.id,
	            'debit': 0.0,
	            'credit': amount,
	            'journal_id': category_id.journal_id.id,
	            'analytic_account_id': account_analytic_id.id if category_id.type == 'sale' else False,
	            'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'sale' else False,
	        }
	        move_line_2 = {
	            'name': name,
	            'account_id': category_id.z_write_off_account.id,
	            'credit': 0.0,
	            'debit': amount,
	            'journal_id': category_id.journal_id.id,
	            'analytic_account_id': account_analytic_id.id if category_id.type == 'purchase' else False,
	            'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'purchase' else False,
	        }
	        move_vals = {
	            'ref': category_id.name,
	            'date': depreciation_date or False,
	            'journal_id': category_id.journal_id.id,
	            'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
	        }

	        return move_vals
