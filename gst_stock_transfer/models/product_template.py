# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import itertools
import operator
import psycopg2

from odoo.addons import decimal_precision as dp

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, RedirectWarning, except_orm
from odoo.tools import pycompat
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
	_inherit = "product.template"

	z_transfer_price = fields.Float(string="Transfer Price")
	z_transfer_check = fields.Boolean(string="Enable Transfer Price",related="categ_id.z_transfer_price_bool")

	z_taxes_id = fields.Many2many('account.tax', 'z_product_taxes_rel', 'z_prod_id', 'z_tax_id', help="Default taxes used when selling the product.", string='Internal Customer Taxes',
        domain=[('type_tax_use', '=', 'sale')], default=lambda self: self.env.user.company_id.account_sale_tax_id)

	z_supplier_taxes_id = fields.Many2many('account.tax', 'z_product_supplier_taxes_rel', 'z_prod_id', 'z_tax_id', string='Internal Vendor Taxes', help='Default taxes used when buying the product.',
        domain=[('type_tax_use', '=', 'purchase')], default=lambda self: self.env.user.company_id.account_purchase_tax_id)

	@api.multi
	def _get_product_accounts(self):
		accounts = super(ProductTemplate, self)._get_product_accounts()
		res = self._get_asset_accounts()
		accounts.update({
            'stock_input': res['stock_input'] or self.property_stock_account_input or self.categ_id.property_stock_account_input_categ_id,
            'stock_output': res['stock_output'] or self.property_stock_account_output or self.categ_id.property_stock_account_output_categ_id,
            'stock_valuation': self.categ_id.property_stock_valuation_account_id or False,
            'transfer_journal':self.categ_id.z_transfer_journal,
            'transfer_account':self.categ_id.z_transfer_account,
            })
		return accounts



#_get_accounting_data_for_valuation....stock_account stock.py 489