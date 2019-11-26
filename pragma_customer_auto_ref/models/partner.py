# -*- coding: utf-8 -*-




from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import pdb

class ResPartner(models.Model):
    _inherit = 'res.partner'
    _name = _inherit

    z_partner_category = fields.Many2one('partner.category',string="Partner Category",required=True)
    z_partner = fields.Boolean('Partner')

    

    @api.model
    def create(self, vals):
        if 'z_partner' in vals and vals['z_partner']:
            sequence_type =  vals.get('z_partner_category')
            sequence_type = self.env['partner.category'].browse(sequence_type)
            if sequence_type:
                vals['ref'] = sequence_type.partner_category.next_by_id()

        return super(ResPartner, self).create(vals)

    @api.multi
    @api.onchange('z_partner_category')
    def Onchange_partner(self):
        for l in self:
            if l.z_partner_category.partner_category:
                l.z_partner = True
            else:
                l.z_partner = False

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _name = _inherit

    z_partner = fields.Boolean('Partner')
    default_code= fields.Char(string='Internal Reference',compute = "_trackcode",store=True)
    default_code1= fields.Char(string='Internal Reference')

    @api.multi
    @api.onchange('categ_id')
    def Onchange_partner(self):
        for l in self:
            # print("category_id",l.categ_id.sequence_id)
            if l.categ_id.sequence_id:
                l.z_partner = True
            else:
                l.z_partner = False
    @api.depends('default_code1')
    def _trackcode(self):
        
        print(self.default_code1)
        self.default_code = self.default_code1   

    @api.model
    def create(self, vals):
        if 'z_partner' in vals and vals['z_partner']:
            sequence_type =  vals.get('categ_id')
            sequence_type = self.env['product.category'].browse(sequence_type)
            if sequence_type:
                new_code = sequence_type.sequence_id.next_by_id()
                vals.update({'default_code1': new_code,'default_code': new_code})
                # pdb.set_trace()

        return super(ProductTemplate, self).create(vals)



    # @api.depends('default_code1')
    # def _compute_default_code(self):
    #     print(self.product_variant_ids)
    #     if not self.default_code1:
    #         unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
    #         for template in unique_variants:
    #             template.default_code = template.product_variant_ids.default_code
    #         for template in (self - unique_variants):
    #             template.default_code = ''    
    #     else:
    #         self.default_code = self.default_code1
    #     return super(ProductTemplate, self)


class ProductCategory(models.Model):
    _inherit = 'product.category'

    sequence_id = fields.Many2one('ir.sequence',string='Sequence')


class PartnerCategory(models.Model):
    _name = 'partner.category'

    name = fields.Char(string='Name')
    full_name = fields.Char(string='Full Name')
    active_id = fields.Boolean(string='Active')
    partner_category = fields.Many2one('ir.sequence',string="Sequence")

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_reference = fields.Char('Partner Category')

    @api.multi
    @api.onchange('partner_id')
    def Onchange_partner(self):
        for l in self:
            l.partner_reference = l.partner_id.z_partner_category.name


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    partner_reference = fields.Char('Partner Category')

    @api.multi
    @api.onchange('partner_id')
    def Onchange_partnerr(self):
        for l in self:
            l.partner_reference = l.partner_id.z_partner_category.name

class PurchaseReport(models.Model):
    _inherit = 'purchase.report'

    partner_reference = fields.Char('Partner Category')

    def _select(self):
        return super(PurchaseReport, self)._select() + ",s.partner_reference as partner_reference"

    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + ",s.partner_reference"

class SaleReport(models.Model):
    _inherit = "sale.report"

    partner_reference = fields.Char('Partner Category')

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['partner_reference'] = ',s.partner_reference as partner_reference'
        groupby += ', s.partner_reference'
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    partner_reference = fields.Char('Partner Category',store=True,track_visibility='always',compute='change_partners')

    @api.multi
    @api.depends('partner_id')
    def change_partners(self):
        for l in self:
            l.partner_reference = l.partner_id.z_partner_category.name






