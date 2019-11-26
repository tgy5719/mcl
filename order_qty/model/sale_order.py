from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    z_uom_ratio = fields.Float(string='Ratio', store=True,track_visibility='always',compute='_onchange_product_id_uom')
    product_packaging = fields.Many2one('product.packaging',string="Size",domain="[('product_id', '=', product_id)]")
    z_no_of_package = fields.Float(string="No of Boxes")
    product_uom_qty = fields.Float(string='Qt. in Sq. Mt ',digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    z_no_package = fields.Float(string='No of Boxes')
    z_quantity_ft = fields.Float('Qty in Sq. ft')
    z_uom_so_id = fields.Many2one('uom.uom','SUOM')
    z_sales_price_sqft = fields.Float('Sales price Sq. Ft')
    z_sales_price = fields.Float('Sales price', store=True,track_visibility='always',compute='_onchange_product_id_uom')
    # z_delivered_boxes = fields.Float(strig="No of Delivered Boxes",compute='_onchange_product_id_uom')    
    #z_ordered_qty = fields.Float(string="Ordered_qty")
    @api.multi
    @api.onchange('z_no_of_package','product_packaging')
    def compute_price_check_qty(self):
        qty = 0.0
        for line in self:
            if line.z_no_of_package >= 1 and line.product_packaging:
                qty = line.z_no_of_package * (line.product_packaging.qty * line.z_uom_ratio)
                line.z_quantity_ft = qty
                line.product_uom_qty = qty / line.z_uom_ratio

    @api.onchange('product_packaging','z_quantity_ft')
    def compute_price_check_package(self):
        package = 0.0
        for line in self:
            if line.z_quantity_ft > 0 and line.product_packaging:
                package = line.z_quantity_ft / (line.product_packaging.qty * line.z_uom_ratio)
                line.z_no_of_package = package
                line.product_uom_qty = line.z_quantity_ft / line.z_uom_ratio
                if int((line.z_no_of_package-int(line.z_no_of_package))*10) > 0:
                    line.z_no_of_package = int(line.z_no_of_package)+1
                else:
                    line.z_no_of_package = int(line.z_no_of_package)

    @api.onchange('product_uom_qty','product_packaging')
    def compute_price_check_package1(self):
        prod = 0.0
        for line in self:
            if line.product_uom_qty and line.z_uom_ratio > 0 and line.product_packaging :
                prod = line.product_uom_qty * line.z_uom_ratio
                line.z_quantity_ft = prod
                line.z_no_of_package = line.product_uom_qty / line.product_packaging.qty
                if int((line.z_no_of_package-int(line.z_no_of_package))*10) > 0:
                    line.z_no_of_package = int(line.z_no_of_package)+1
                else:
                    line.z_no_of_package = int(line.z_no_of_package)

    @api.depends('product_id','qty_delivered')
    def _onchange_product_id_uom(self):
        box = 0.0
        for line in self:
            if line.product_id:
                line.z_uom_so_id = line.product_id.z_uom_so_id
                if line.product_id.z_uom_so_id.uom_type == 'bigger':
                    line.z_uom_ratio = line.product_id.z_uom_so_id.factor_inv
                else:
                    line.z_uom_ratio = line.product_id.z_uom_so_id.factor
            for l in line.order_id:
                if l.z_sales_person:
                    var = self.env['product.pricelist.item'].search([('pricelist_id','=',l.pricelist_id.id),('product_id','=',line.product_id.id)])
                    for rec in var:
                        line.z_sales_price = rec.fixed_price
            # if line.qty_delivered > 0:
            #     box = line.qty_delivered / line.product_packaging.qty
            #     line.z_delivered_boxes = box
                

    @api.onchange('price_unit')
    def _onchange_price_unit(self):
        for line in self:
            if line.price_unit and line.z_uom_ratio > 0:
                line.z_sales_price_sqft = line.price_unit / line.z_uom_ratio

    @api.onchange('z_sales_price_sqft')
    def _onchange_sales_price_sqft(self):
        for line in self:
            if line.z_sales_price_sqft and line.z_uom_ratio > 0:
                line.price_unit = line.z_sales_price_sqft * line.z_uom_ratio


    @api.multi
    def write(self, values):
        result = super(SaleOrderLine, self).write(values)
        total = price = 0
        for l in self:
            if l.state == 'draft':
                if l.price_unit < l.z_sales_price:
                    raise UserError(_("Unit Price must not be lower than Sales price"))
        return result










    '''@api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = self.product_uom_qty or 1.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        result = {'domain': domain}

        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False
                return result

        name = self.get_sale_order_line_multiline_description_sale(product)

        if self.product_custom_attribute_value_ids or self.product_no_variant_attribute_value_ids:
            name += '\n'

        if self.product_custom_attribute_value_ids:
            for product_custom_attribute_value in self.product_custom_attribute_value_ids:
                if product_custom_attribute_value.custom_value and product_custom_attribute_value.custom_value.strip():
                    name += '\n' + product_custom_attribute_value.attribute_value_id.name + ': ' + product_custom_attribute_value.custom_value.strip()

        if self.product_no_variant_attribute_value_ids:
            for no_variant_attribute_value in self.product_no_variant_attribute_value_ids.filtered(
                lambda product_attribute_value: not product_attribute_value.is_custom
            ):
                name += '\n' + no_variant_attribute_value.attribute_id.name + ': ' + no_variant_attribute_value.name

        vals.update(name=name)

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)

        return result'''

