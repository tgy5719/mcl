
from odoo import api, fields, models, tools


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    z_ven_biz_type = fields.Many2one('vendor.business.type',string='Vendor Business Type')
   

   
    def _select(self):
        return super(PurchaseReport, self)._select() + ",s.z_ven_biz_type as z_ven_biz_type"

    def _from(self):
        return super(PurchaseReport, self)._from() + " left join vendor_business_type z_ven_biz_type on (s.z_ven_biz_type = z_ven_biz_type.id)" 

    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + ",s.z_ven_biz_type" 

