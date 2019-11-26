from odoo import api, fields, models,_


class StockPickingfield(models.Model):
	_inherit = "stock.picking"

	z_invoice_number= fields.Char(string='Invoice Number')

	