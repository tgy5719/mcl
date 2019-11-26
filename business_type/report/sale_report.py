
from odoo import models, fields, api, _
from odoo import tools

class SaleReport(models.Model):
    _inherit = "sale.report"

    z_cus_biz_type = fields.Many2one('customer.business.type',string='Customer Business Type')
    z_sale_ofc = fields.Many2one('office.name',string='Sales Office')


    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['days_to_confirm'] = ", DATE_PART('day', s.confirmation_date::timestamp - s.create_date::timestamp) as days_to_confirm"
        fields['invoice_status'] = ', s.invoice_status as invoice_status'
        fields['z_cus_biz_type'] = ',s.z_cus_biz_type as z_cus_biz_type'
        fields['z_sale_ofc'] = ',s.z_sale_ofc as z_sale_ofc'
        groupby += ', s.invoice_status'
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)

        

        
   