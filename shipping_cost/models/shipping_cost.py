from datetime import datetime,timedelta
from odoo import api, models, fields, _, exceptions
from dateutil.relativedelta import relativedelta
from time import strptime
from odoo.exceptions import UserError, ValidationError,Warning
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ShippingCost(models.Model):
	_inherit = 'delivery.carrier'

	delivery_type = fields.Selection(selection_add=[('pcent', "Based on Percentage")])
	percent = fields.Float(string="Percentage")
    
class SaleOrderInherited(models.Model):
    _inherit = 'sale.order'

    retreived_value = fields.Float(String= 'Calculated Value',compute='cal_method', readonly=True)
    delivery_price = fields.Float(string='Estimated Delivery Price', readonly=True, copy=False)

    def cal_method(self):
        if self.carrier_id.delivery_type == 'pcent':
            delivery_env = self.env['delivery.carrier']
            self.retreived_value = ((self.carrier_id.percent*self.amount_untaxed)/100)
            self.delivery_price = self.retreived_value

    def get_delivery_price(self):
        if self.carrier_id.delivery_type == 'pcent':
            self.cal_method()
            # res = order.carrier_id.rate_shipment(order)
            self.delivery_rating_success = True
            # self._create_delivery_line(self.carrier_id, self.delivery_price)
        else:
            for order in self.filtered(lambda o: o.state in ('draft', 'sent') and len(o.order_line) > 0):
                # We do not want to recompute the shipping price of an already validated/done SO
                # or on an SO that has no lines yet
                order.delivery_rating_success = False
                res = order.carrier_id.rate_shipment(order)
                if res['success']:
                    order.delivery_rating_success = True
                    order.delivery_price = res['price']
                    order.delivery_message = res['warning_message']
                else:
                    order.delivery_rating_success = False
                    order.delivery_price = 0.0
                    order.delivery_message = res['error_message']
    @api.multi
    def set_delivery_line(self):
        # delivery_price = self.delivery_price
        if self.carrier_id.delivery_type == 'pcent':
            self._remove_delivery_line()
            self._create_delivery_line(self.carrier_id, self.delivery_price)
            return True

        else:
            # Remove delivery products from the sales order
            self._remove_delivery_line()

            for order in self:
                if order.state not in ('draft', 'sent'):
                    raise UserError(_('You can add delivery price only on unconfirmed quotations.'))
                elif not order.carrier_id:
                    raise UserError(_('No carrier set for this order.'))
                elif not order.delivery_rating_success:
                    raise UserError(_('Please use "Check price" in order to compute a shipping price for this quotation.'))
                else:
                    price_unit = order.carrier_id.rate_shipment(order)['price']
                    # TODO check whether it is safe to use delivery_price here
                    order._create_delivery_line(order.carrier_id, price_unit)
        return True



    # @api.onchange('retreived_value')
    # def compute_price(self):
    #     self.delivery_price = self.retreived_value


    # def calculate(self):
    # 	carrier_env = self.env['delivery.carrier']
    # 	sol_valls = {'product_id': self.iPadMini.id,
    # 			'name': "[A1232] Large Cabinet",
    # 			'product_uom': self.env.ref('uom.product_uom_unit').id,
    # 			'product_uom_qty': 1.0,
    # 			'price_unit':self.iPadMini.lst_price,}

    # 	so_valls = {'partner_id': self.agrolait.id,
    # 				'carrier_id': self.env.ref('shipping_cost.delivery_carrier_shipping_cost').id,
    # 				'delivery_price':self.amount_untaxed + (carrier_env.percent * self.amount_untaxed)/100,
    # 				'order_line': [(0, 0, sol_valls)]}

    # 	sale_order = carrier_env.create(so_valls)
    # 	sale_order.get_delivery_price()

    # def percent_rate_shipment(self, order):
    #     ''' Compute the price of the order shipment

    #     :param order: record of sale.order
    #     :return dict: {'success': boolean,
    #                    'price': a float,
    #                    'error_message': a string containing an error message,
    #                    'warning_message': a string containing a warning message}
    #                    # TODO maybe the currency code?
    #     '''
    #     self.ensure_one()
    #     if hasattr(self, '%s_rate_shipment' % self.delivery_type):
    #         res = getattr(self, '%s_rate_shipment' % self.delivery_type)(order)
    #         # apply margin on computed price
    #         res['price'] = res['price'] * (1.0 + (float(self.margin) / 100.0))
    #         # free when order is large enough
    #         if res['success'] and self.free_over and order._compute_amount_total_without_delivery() >= self.amount:
    #             res['warning_message'] = _('Info:\nThe shipping is free because the order amount exceeds %.2f.\n(The actual shipping cost is: %.2f)') % (self.amount, res['price'])
    #             res['price'] = 0.0
    #         return res

    # def get_delivery_price(self):
    #     for order in self.filtered(lambda o: o.state in ('draft', 'sent') and len(o.order_line) > 0):
    #         # We do not want to recompute the shipping price of an already validated/done SO
    #         # or on an SO that has no lines yet
    #         order.delivery_rating_success = False
    #         res = order.carrier_id.percent_rate_shipment(order)
    #         if res['success']:
    #             order.delivery_rating_success = True
    #             order.delivery_price = res['price']
    #             order.delivery_message = res['warning_message']
    #         else:
    #             order.delivery_rating_success = False
    #             order.delivery_price = 0.0
    #             order.delivery_message = res['error_message']

    # get_delivery_price(self)


    # def get_delivery_price(self):

    

    # def get_delivery_price(self):
    #     if self.carrier_id.delivery_type == 'pcent':
    #         value = pcent_rate_shipment()
    #         if res['success']:
    #             value.delivery_rating_success = True
    #             value.delivery_price = res['price']
    #             value.delivery_message = res['warning_message']
    #         else:
    #             value.delivery_rating_success = False
    #             value.delivery_price = 0.0
    #             value.delivery_message = res['error_message']

    #     else:
    #         for order in self.filtered(lambda o: o.state in ('draft', 'sent') and len(o.order_line) > 0):
    #             # We do not want to recompute the shipping price of an already validated/done SO
    #             # or on an SO that has no lines yet
    #             order.delivery_rating_success = False
    #             res = order.carrier_id.rate_shipment(order)
    #             if res['success']:
    #                 order.delivery_rating_success = True
    #                 order.delivery_price = res['price']
    #                 order.delivery_message = res['warning_message']
    #             else:
    #                 order.delivery_rating_success = False
    #                 order.delivery_price = 0.0
    #                 order.delivery_message = res['error_message']

    # def pcent_rate_shipment(self):
    #     delivery = self.env['delivery.carrier']
    #     check_pcent = delivery.percent
    #     so_valls = {}
    #     pcent_price = self.amount_untaxed + (delivery.check_pcent * self.amount_untaxed)/100
    #     so_valls : {'success': True,
    #                 'price': pcent_price,
    #                 'error_message': False,
    #                 'warning_message': False}
    #     return so_valls