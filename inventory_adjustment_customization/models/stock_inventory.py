# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_utils, float_compare


class Inventory(models.Model):
	_inherit = "stock.inventory"
	_description = "Inventory"
	_order = "date desc, id desc"

	z_from_product_id = fields.Many2one(
        'product.product', 'From Product',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Specify Product to focus your inventory on a particular Product.")
	z_to_product_id = fields.Many2one(
        'product.product', 'To Product',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Specify Product to focus your inventory on a particular Product.")

	@api.model
	def _selection_filter(self):
		res_filter = [
		('none', _('All products')),
		('category', _('One product category')),
		('product', _('One product only')),
		('partial', _('Select products manually')),
		('product_to_product',_('Product to Product Transfer'))]
		if self.user_has_groups('stock.group_tracking_owner'):
			res_filter += [('owner', _('One owner only')), ('product_owner', _('One product for a specific owner'))]
		if self.user_has_groups('stock.group_production_lot'):
			res_filter.append(('lot', _('One Lot/Serial Number')))
		if self.user_has_groups('stock.group_tracking_lot'):
			res_filter.append(('pack', _('A Pack')))
		return res_filter

	@api.onchange('filter')
	def _onchange_filter(self):
		# if self.filter not in ('owner', 'product_owner','product_to_product'):
  #           self.partner_id = False
		if self.filter not in ('product_to_product'):
			self.z_from_product_id = False
			self.z_to_product_id = False

		if self.filter in ('product','product_to_product'):
			self.exhausted = True
			if self.product_id:
				return {'domain': {'product_id': [('product_tmpl_id', '=', self.product_id.product_tmpl_id.id)]}}
			if self.z_from_product_id:
				return {'domain': {'product_id': [('product_tmpl_id', '=', self.z_from_product_id.product_tmpl_id.id)]}}
			if self.z_to_product_id:
				return {'domain': {'product_id': [('product_tmpl_id', '=', self.z_to_product_id.product_tmpl_id.id)]}}
		return super(Inventory,self)._onchange_filter()

	def _get_inventory_lines_values(self):
		# TDE CLEANME: is sql really necessary ? I don't think so
		locations = self.env['stock.location'].search([('id', 'child_of', [self.location_id.id])])
		domain = ' location_id in %s AND quantity != 0 AND active = TRUE'
		args = (tuple(locations.ids),)
		vals = []
		Product = self.env['product.product']
        # Empty recordset of products available in stock_quants
		quant_products = self.env['product.product']
        # Empty recordset of products to filter
		products_to_filter = self.env['product.product']

		if self.company_id:
			domain += ' AND company_id = %s'
			args += (self.company_id.id,)
		if self.partner_id:
			domain += ' AND owner_id = %s'
			args += (self.partner_id.id,)

		if self.lot_id:
			domain += ' AND lot_id = %s'
			args += (self.lot_id.id,)

		if self.product_id:
			domain += ' AND product_id = %s'
			args += (self.product_id.id,)
			products_to_filter |= self.product_id

		if self.package_id:
			domain += ' AND package_id = %s'
			args += (self.package_id.id,)

		if self.category_id:
			categ_products = Product.search([('categ_id', 'child_of', self.category_id.id)])
			domain += ' AND product_id = ANY (%s)'
			args += (categ_products.ids,)
			products_to_filter |= categ_products


		if self.z_from_product_id:
			domain += ' AND product_id = %s'
			args += (self.z_from_product_id.id,)
			products_to_filter |= self.z_from_product_id

		if self.z_to_product_id:
			domain += ' AND product_id = %s'
			args += (self.z_to_product_id.id,)
			products_to_filter |= self.z_to_product_id

		self.env.cr.execute("""SELECT product_id, sum(quantity) as product_qty, location_id, lot_id as prod_lot_id, package_id, owner_id as partner_id
            FROM stock_quant
            LEFT JOIN product_product
            ON product_product.id = stock_quant.product_id
            WHERE %s
            GROUP BY product_id, location_id, lot_id, package_id, partner_id """ % domain, args)

		for product_data in self.env.cr.dictfetchall():
            # replace the None the dictionary by False, because falsy values are tested later on
			for void_field in [item[0] for item in product_data.items() if item[1] is None]:
				product_data[void_field] = False
			product_data['theoretical_qty'] = product_data['product_qty']
			if product_data['product_id']:
				product_data['product_uom_id'] = Product.browse(product_data['product_id']).uom_id.id
				quant_products |= Product.browse(product_data['product_id'])
			vals.append(product_data)
		if self.exhausted:
			exhausted_vals = self._get_exhausted_inventory_line(products_to_filter, quant_products)
			vals.extend(exhausted_vals)
		return vals

	def action_validate(self):
		for line in self:
			if line.filter == 'product_to_product':
				from_pro = to_prod = 0
				for lines in line.line_ids:
					if lines.product_id.id == line.z_from_product_id.id:
						from_pro = lines.adjust_qty
					if lines.product_id.id == line.z_to_product_id.id:
						to_prod = lines.adjust_qty
				if from_pro != to_prod:
					raise UserError(_('From and To product adjustable qty is not matching.'))
		return super(Inventory,self).action_validate()

class InventoryLine(models.Model):
	_inherit = "stock.inventory.line"

	adjust_qty = fields.Float(
        'Adjust Quantity',
        digits=dp.get_precision('Product Unit of Measure'), default=0)

	@api.onchange('adjust_qty')
	def compute_real_quantity(self):
		for line in self:
			if line.product_id.id == line.inventory_id.z_from_product_id.id:
				line.product_qty = line.theoretical_qty - line.adjust_qty
			if line.product_id.id == line.inventory_id.z_to_product_id.id:
				line.product_qty = line.theoretical_qty + line.adjust_qty