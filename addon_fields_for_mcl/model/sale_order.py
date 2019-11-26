from odoo import api, fields, models,_


class SaleOrder(models.Model):
    _inherit = "sale.order"

    z_sale_ofc = fields.Many2one('office.name',string='Sales Office')
    sale_off = fields.Many2one(string="Sale office")
    #z_customer_tag = fields.Many2many('res.partner.category', string='CustomerTag',related='partner_id.category_id')
    z_project_site = fields.Many2one('site.name',string="Project Site")
    z_order_type = fields.Many2one('sale.order.type',string='Order Type',store=True)
    z_payment_method = fields.Many2one('custom.fields',string='Payment Method',store=True ,index=True,ondelete='cascade')
    z_custom_po_no = fields.Char(string='Customer PO NO', store=True)
    z_po_date = fields.Date(String='PO Date', store=True)
    #ext_doc_no = fields.Char(string='External Document No', store=True)
    #Export related fields
    port_of_discharge = fields.Many2one('port.order', string='Port Of Discharge')
    port_of_destination = fields.Many2one('port.order', string='Port Of Destination')
    country_of_origin_goods = fields.Many2one('res.country', string='Country Of Origin Of Goods')
    country_of_final_destination = fields.Many2one('res.country', string='Country Of Final Destination')
    pre_carriage= fields.Selection([
        ('air', 'By Air'),
        ('rail', 'Rail'),
        ('road', 'Road')], string='Pre Carriage')
    carriage= fields.Selection([
        ('sea', 'Sea'),
        ('air', 'By Air'),
        ('rail', 'Rail'),
        ('road', 'Road')], string='Carriage')
    export_shipment_method = fields.Many2one('export.shipment', string='Export Shipment Method')
    type_of_container = fields.Many2one('type.container', string='Type Of Container')
    project_name = fields.Char(string="Project Name")
    proforma_sequence = fields.Char(string="Proforma Invoice Number",readonly=True)

    @api.onchange('partner_id')
    def _onchange_partner_id_sale_ofc(self):
        res = self.env['res.partner'].search([('id', '=', self.partner_id.id)])
        for line in res:
            if self.partner_id:
                self.z_sale_ofc = self.partner_id.z_sales_office



    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sales journal for this company.'))
        invoice_vals = {
            'name': self.client_order_ref or '',
            'origin': self.name,
            'type': 'out_invoice',
            'account_id': self.partner_invoice_id.property_account_receivable_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            #'journal_id': journal_id,
            'currency_id': self.pricelist_id.currency_id.id,
            'comment': self.note,
            'payment_term_id': self.payment_term_id.id,
            'port_of_discharge':self.port_of_discharge.id,
            'port_of_destination':self.port_of_destination.id,
            'country_of_origin_goods':self.country_of_origin_goods.id,
            'country_of_final_destination':self.country_of_final_destination.id,
            'pre_carriage':self.pre_carriage,
            'carriage':self.carriage,
            'export_shipment_method':self.export_shipment_method.id,
            'type_of_container':self.type_of_container.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id,
            'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            'pricelist_id':self.pricelist_id.id,
            'confirmation_date': self.confirmation_date,
            'z_sale_ofc': self.z_sale_ofc.id,
            #'z_customer_tag': self.z_customer_tag.ids,
            'z_order_type': self.z_order_type.id,
            'z_payment_method': self.z_payment_method.id,
            'z_custom_po_no': self.z_custom_po_no,
            'z_po_date': self.z_po_date,
            'z_project_site': self.z_project_site.id,
            #field is from prix_analytic_account
            'z_analytic_account_id':self.analytic_account_id.id,
            #fields from analytic_warehouse
            'journal_id': self.z_journal.id,
            'z_warehouse_id':self.warehouse_id.id,
            #fields from walkin_sales
            'zz_walkin': self.z_walkin,
            'zz_street_walk': self.z_street_walk,
            'zz_street2_walk': self.z_street2_walk,
            'zz_city_walk': self.z_city_walk,
            'zz_state_id_walk': self.z_state_id_walk.id,
            'zz_zip_walk': self.z_zip_walk,
            'zz_country_id_walk': self.z_country_id_walk.id,
            'zz_phone_walk': self.z_phone_walk,
            'zz_email_walk': self.z_email_walk,
            'zz_mobile_walk': self.z_mobile_walk,
            #'ext_doc_no': self.ext_doc_no,
        }
        return invoice_vals

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _prepare_invoice_line(self, qty):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = {}
        account = self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id

        if not account and self.product_id:
            raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))

        fpos = self.order_id.fiscal_position_id or self.order_id.partner_id.property_account_position_id
        if fpos and account:
            account = fpos.map_account(account)

        res = {
            'name': self.name,
            'sequence': self.sequence,
            'origin': self.order_id.name,
            'account_id': account.id,
            'price_unit': self.price_unit,
            'quantity': qty,
            'discount': self.discount,
            'uom_id': self.product_uom.id,
            'product_id': self.product_id.id or False,
            'invoice_line_tax_ids': [(6, 0, self.tax_id.ids)],
            'account_analytic_id': self.order_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'display_type': self.display_type,
            'product_packaging': self.product_packaging.id,
        }
        return res