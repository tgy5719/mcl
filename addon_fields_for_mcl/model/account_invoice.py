from odoo import api, fields, models,_

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    z_sale_ofc = fields.Many2one('office.name',string='Sales Office')
    z_customer_tag = fields.Many2many('res.partner.category', string='CustomerTag')
    z_project_site = fields.Many2one('site.name',string="Project Site")
    z_order_type = fields.Many2one('sale.order.type',string='Order Type',store=True)
    z_payment_method = fields.Many2one('custom.fields',string='Payment Method',store=True ,index=True,ondelete='cascade')
    z_custom_po_no = fields.Char(string='Customer PO Num', store=True)
    z_po_date = fields.Date(String='PO Date', store=True)
    confirmation_date = fields.Datetime(string='Confirmation Date')
    ext_doc_no = fields.Char(string='External Document No', store=True)
    product_packaging = fields.Many2one('product.packaging',string="Package")
    z_no_of_package = fields.Float(string="No Package")

    #Export fields
    port_of_discharge = fields.Many2one('port.order', string='Port Of Discharge')
    port_of_destination = fields.Many2one('port.order', string='Port Of Destination')
    country_of_origin_goods = fields.Many2one('res.country', string='Country Of Origin Of Goods')
    country_of_final_destination = fields.Many2one('res.country', string='Country Of Final Destination')
    pre_carriage= fields.Selection([
        ('air', 'By Air'),
        ('rail', 'Rail'),
        ('road', 'Road')], string='Pre Carriage')
    carriage= fields.Selection([
        ('sea', 'Sea')], string='Carriage')
    export_shipment_method = fields.Many2one('export.shipment', string='Export Shipment Method')
    type_of_container = fields.Many2one('type.container', string='Type Of Container')
    pricelist_id = fields.Many2one('product.pricelist',string="Pricelist")
    z_order_type_po = fields.Many2one('purchase.order.type',string='Order Type',store=True)

class AccountInvoiceLine(models.Model):
	_inherit = 'account.invoice.line'

	product_packaging = fields.Many2one('product.packaging',string="Package")
	

