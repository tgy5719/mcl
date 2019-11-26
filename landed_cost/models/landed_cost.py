from datetime import datetime,timedelta
from odoo import api, models, fields, _, exceptions
from dateutil.relativedelta import relativedelta
from time import strptime
from odoo.exceptions import UserError, ValidationError,Warning
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class LandedCost(models.Model):
	_inherit = 'stock.landed.cost'

	zreference = fields.Many2one('account.invoice',string='Reference')
	zvendor = fields.Many2one('res.partner', string='Vendor')

class PurchaseOrder(models.Model):
	_inherit = 'account.invoice'

	bool_for_settings = fields.Boolean(string='Checking for Landed Cost Tick',readonly = True)

	@api.multi
	def method_settings(self):
		environment_settings = self.env['res.config.settings']
		for line_1 in environment_settings:
			if line_1.module_stock_landed_costs == True:
				self.bool_for_settings = True

	# settings_config_relation = fields.One2many('res.config.settings','relation_to_settings')


	def post_entry(self):
		# generates all the landed cost records
		# for l in self.order_line.search([('product_id.bool_landed_cost','=',True)]):
		# 	envi = self.env['stock.landed.cost'].create({
		# 		'zreference':self.id,
		# 		'zvendor':self.partner_id.id,
		# 		'account_journal_id':3,
		# 		'date': fields.Datetime.today(),
				# 'cost_lines': [
				# 		(0, 0, {
				# 		'product_id': l.product_id.id,
				# 		'price_unit': l.price_subtotal,
				# 		'split_method': l.product_id.split_method,
				# 		})]
					# })

		# for l in self.order_line.search([('product_id.bool_landed_cost','=',True)]):
		# envi = self.env['stock.landed.cost'].create({
		# 	'zreference':self.id,
		# 	'zvendor':self.partner_id.id,
		# 	'account_journal_id':3,
		# 	'date': fields.Datetime.today(),
		# 	'cost_lines': [
		# 			(0, 0, {
		# 			'product_id': l.product_id.id,
		# 			'price_unit': l.price_subtotal,
		# 			'split_method': l.product_id.split_method,
		# 			})]
		# 		})

		# order_line = self.env['purchase.order.line'].search([('product_id.bool_landed_cost','=',True)])


		
		vals = {
			'zreference':self.id,
			'zvendor':self.partner_id.id,
			'account_journal_id':3,
			'date': fields.Datetime.today(),
		}
		landed_obj = self.env['stock.landed.cost'].create(vals)
		

		stock_landed_obj = self.env['stock.landed.cost.lines']
		move_line = {}	
		for line_1 in self.invoice_line_ids:
			if line_1.product_id.bool_landed_cost == True:
				move_line = {
				'product_id': line_1.product_id.id,
				'name': line_1.name,
				'split_method': line_1.product_id.split_method,
				'price_unit': line_1.price_subtotal,
				'cost_id':landed_obj.id
				}
				stock_landed_obj.create(move_line)






		
        # for line in self.move_raw_ids:
        #     if line.reserved_availability < line.product_uom_qty:
        #         qty = line.product_uom_qty - line.reserved_availability
        #         move_line = {}
        #         move_line = {
        #                     	'product_id': line.product_id.id,
        #                 	    'product_uom_qty': qty,
        #               	        'product_uom_qty_reserved': line.reserved_availability,
        #                         'product_uom': line.product_id.uom_id.id,
        #                         'location_id': line.product_id.property_stock_production.id,
        #                         'location_dest_id': line.product_id.property_stock_inventory.id,
        #                         'mrp_indent_product_line_id': indent_obj.id
        #                         }
        #             move_lines_obj.create(move_line)

		# line = self.env['stock.landed.cost'].search([(self.product_id.bool_landed_cost,'=',True)])
		# for l in line:
		# 	vals = {
		# 	'zreference':self.id,
		# 	'zvendor':self.partner_id.id,
		# 	'account_journal_id':3,
		# 	'date': fields.Datetime.today(),
		# 	'cost_lines': [
		# 					(0, 0, {
		# 					'product_id': l.product_id.id,
		# 					'price_unit': l.price_subtotal,
		# 					'split_method': l.product_id.split_method,
		# 					})]
		# 		}
		# 	landed_var = self.env['stock.landed.cost'].create(self.vals)
		

		# prod = self.env['purchase.order.line'].search([('product_id.bool_landed_cost','=',True)])
		# for product_id in prod:
		# 	product_id = self.product_id

		# for line in self.order_line:
		# 	values = {
		# 		'product_id': line.product_id.id,
		# 		'price_unit': line.price_subtotal,
		# 		'split_method':'equal',
		# 		}
		# order = self.env['stock.landed.cost.lines']

		# prod = self.env['purchase.order.line']
		# for order in prod:
		# 	order_lines = self.env['stock.landed.cost.lines'].create({
	        #     'order_line': [
	        #         (0, 0, {
	        #             'product_id': order.product_id.id,
	        #             'price_unit': order.price_subtotal,
	        #             'split_method': 'equal',
	        #         })]
	        # })
       
	
	# @api.multi
	# def landed_cost_button(self):
	# 	# action = self.env.ref('stock_landed_costs.view_stock_landed_cost_form')
	# 	# result = action.read()[0]
	# 	# landed_cost = self.env.context.get('landed_cost', False)
	# 	# result['context'] = {
	# 	# 'type': 'ir.actions.act_window',
	# 	# 'zreference': self.id,
	# 	# 'zvendor': self.partner_id.id,
	# 	# 'account_journal_id': 3,
	# 	# 'date': fields.Datetime.today(),}
	# 	# return result
		
	# 	view_id = self.env.ref('landed_cost.inherit_landed_cost_form').id
	# 	context = self._context.copy()
	# 	vals = {
	# 	'zreference':self.id,
	# 	'zvendor':self.partner_id.id,
	# 	'account_journal_id': 3,
	# 	'date': fields.Datetime.today()
	# 	}
	# 	return {
 #            'name':'Landed Cost',
 #            'view_type':'form',
 #            'view_mode':'form',
 #            'views' : [(view_id,'form')],
 #            'res_model':'stock.landed.cost',
 #            'view_id':view_id,
 #            'type':'ir.actions.act_window',
 #            'target':'new',
 #            'context':context,
 #            }
'''        action = self.env.ref('account.action_vendor_bill_template')
        result = action.read()[0]
        create_bill = self.env.context.get('create_bill', False)
        # override the context to get rid of the default filtering
        result['context'] = {
            'type': 'in_invoice',
            'default_purchase_id': self.id,
            'default_currency_id': self.currency_id.id,
            'default_company_id': self.company_id.id,
            'company_id': self.company_id.id
        }
'''

# class ResConfigSettings(models.TransientModel):
#     _inherit = 'res.config.settings'

#     module_stock_landed_costs = fields.Boolean("Landed Costs",
#         help="Affect landed costs on reception operations and split them among products to update their cost price.")


class BoolForLC(models.Model):
	_inherit = 'product.template'

	bool_landed_cost = fields.Boolean(string="Boolean For Landed Cost", related="landed_cost_ok", readonly=True)



