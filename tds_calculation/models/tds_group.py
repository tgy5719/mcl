# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp

# -*- coding: utf-8 -*-

import time
import math

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError

class AccountTdsGroup(models.Model):
    _name = "account.tds.group"
    _description = "TDS Group"
    active = fields.Boolean(default=True, help="Set active to false to hide the tax without removing it.")
    name = fields.Char(string="TDS Group Code",required=True)
    tds_group_name = fields.Char(string='TDS Group Name')

class AccountTdsNod(models.Model):
    _name = "account.tds.nod"
    _description = "TDS NOD"
    active = fields.Boolean(default=True, help="Set active to false to hide the DS NOD without removing it.")
    name = fields.Char(string="TDS NOD Code",required=True)
    tds_nod_name = fields.Char(string="TDS NOD Name")

class AccountTdsSection(models.Model):
    _name = "account.tds.section"
    _description = "TDS Section"
    active = fields.Boolean(default=True, help="Set active to false to hide the TDS Section without removing it.")
    name = fields.Char(string="TDS Section Code",required=True)
    tds_section_name = fields.Char(string="TDS Section Name")

class AccountAssesseCode(models.Model):
    _name = "account.assesse.code"
    _description = "Assesse"
    active = fields.Boolean(default=True, help="Set active to false to hide the Assesse Code without removing it.")
    name = fields.Char(string="Assessee Code",required=True)
    assesse_code_name = fields.Char(string="Assesse Name")

class AccountconcessionCode(models.Model):
    _name = "account.concession.code"
    _description = "Concession"
    active = fields.Boolean(default=True, help="Set active to false to hide the Concession Code without removing it.")
    name = fields.Char(string="Code",required=True)
    concession_code_name = fields.Char(string="Concession Name")
    concession_form_no = fields.Char(string="Concessional Form No.")


class AccountTdsGroupSettings(models.Model):
    _name = "account.tds.group.settings"
    _description = "TDS Group Setting"

    active = fields.Boolean(default=True, help="Set active to false to hide the tax without removing it.")
    name = fields.Char(string="TDS ID",required=True)
    tds_group_name = fields.Many2one('account.tds.group',string="TDS Group")
    date = fields.Datetime(string="Effective Date")
    tds_section = fields.Many2one('account.tds.section',string="TDS Section")
    tds_threshold_amount = fields.Integer(string="TDS Threshold Amount")
    surcharge_threshold_amount = fields.Integer("Surcharge Threshold Amount")
    account_id = fields.Many2one('account.account', string='TDS Account', ondelete='restrict',required=True)
    refund_account_id = fields.Many2one('account.account',string='TDS Account Reverse', ondelete='restrict',required=True)
    
class AccountTdsMapping(models.Model):
    _name = "account.tds.mapping"
    _description = "TDS Mapping"

    active = fields.Boolean(default=True, help="Set active to false to hide the tax without removing it.")
    state = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')], default='active')
    name = fields.Char(string="Name",required=True)
    tds_nod_name = fields.Many2one('account.tds.nod',string="TDS NOD",required=True)
    assesse_code = fields.Many2one('account.assesse.code',string="Assesse Code")
    tds_group = fields.Many2one('account.tds.group.settings',string="TDS ID",required=True)
    date = fields.Datetime(string="Effective Date")
    concession_code = fields.Many2one('account.concession.code',string="Concession code")
    tds = fields.Float(string="Tds %", digits=(16, 4)) 
    non_pan_tds = fields.Float(string="Non Pan TDS %", digits=(16, 4))
    non_pan_tds_req = fields.Boolean(string="Check if Non PAN TDS required", default=False)
    surcharge = fields.Float(string="Surcharge %", digits=(16, 4))
    e_cess = fields.Float(string="e CESS %",digits=(16, 4))
    she_cess = fields.Float(string="SHE Cess %",digits=(16, 4))


class AccountNodConfiguration(models.Model):
    _name = "account.nod.confg"
    _description = "NOD Configuration"

    active = fields.Boolean(default=True, help="Set active to false to hide the NOD Configuration without removing it.")
    partner_type = fields.Selection([('vendor','Vendor'),('customer','Customer')], default='vendor')
    name = fields.Char(string="Code",required=True)
    partner_id = fields.Many2one('res.partner',string="Vendor Name",required=True)
    assesse_code = fields.Many2one('account.assesse.code',string="Assesse Code")
    conf_line_id = fields.One2many('account.nod.confg.line','nod_conf_id',string="Configuration Lines")

    @api.onchange('partner_type')
    def partner_type_change(self):
        res = {}
        if self.partner_type == 'customer':
            res['domain'] = {'partner_id': [('customer', '=', True)]}
        else:
            res['domain'] = {'partner_id': [('supplier', '=', True)]}
        return res
    #added 2 functions. Need to check the process to pass accounting entry else need to pass the same subtotal price to accounting entry.


#need to change the function to calculate the procecss fof tds



class AccountNodConfigurationLine(models.Model):
    _name = "account.nod.confg.line"
    _description = "NOD Configuration Line"

    nod_conf_id = fields.Many2one('account.nod.confg')

    active = fields.Boolean(default=True, help="Set active to false to hide the NOD Configuration without removing it.")
    partner_type = fields.Selection([('vendor','Vendor'),('customer','Customer')], default='vendor')
    partner_id = fields.Many2one('res.partner',string="Vendor Name",related="nod_conf_id.partner_id")
    name = fields.Many2one('account.tds.mapping',string="NOD/NOC")
    assesse_code = fields.Many2one('account.assesse.code',string="Assesse Code")
    concession_code = fields.Many2one('account.concession.code',string="Concessional code")
    concession_form_no = fields.Char(string="Concessional Form No.")
    account_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)], string='TDS Account', ondelete='restrict',related='name.tds_group.account_id')
    refund_account_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)], string='TDS Reversal Account', ondelete='restrict',related='name.tds_group.refund_account_id')
    tds_threshold_applicable = fields.Boolean(string="TDS Threshold Applicable",default=False)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    include_base_amount = fields.Boolean(string='Affect Base of Subsequent Taxes', default=False,
        help="If set, taxes which are computed after this one will be computed based on the price tax included.")
    sequence = fields.Integer(required=True, default=1,
        help="The sequence field is used to define order in which the tax lines are applied.")
    analytic = fields.Boolean(string="Include in Analytic Cost", help="If set, the amount computed by this tax will be assigned to the same analytic account as the invoice line (if any)")

    def get_grouping_key_tds(self, invoice_tds_vals):
        self.ensure_one()
        return str(invoice_tds_vals['tds_id']) + '-' + str(invoice_tds_vals['account_id']) + '-' + str(invoice_tds_vals['account_analytic_id'])


    @api.onchange('concession_code')
    def _onchange_partner(self):
        self.concession_form_no = "%s" % (self.concession_code.concession_form_no or "")

    @api.multi
    def compute_all_tds(self, price_unit, currency=None, quantity=1.0, product=None, partner=None):
        """ Returns all information required to apply taxes (in self + their children in case of a tax goup).
            We consider the sequence of the parent for group of taxes.
                Eg. considering letters as taxes and alphabetic order as sequence :
                [G, B([A, D, F]), E, C] will be computed as [A, D, F, C, E, G]

        RETURN: {
            'total_excluded': 0.0,    # Total without taxes
            'total_included': 0.0,    # Total with taxes
            'taxes': [{               # One dict for each tax in self and their children
                'id': int,
                'name': str,
                'amount': float,
                'sequence': int,
                'account_id': int,
                'refund_account_id': int,
                'analytic': boolean,
            }]
        } """
        if len(self) == 0:
            company_id = self.env.user.company_id
        else:
            company_id = self[0].company_id
        if not currency:
            currency = company_id.currency_id
        tds = []
        base = 0
        # By default, for each tax, tax amount will first be computed
        # and rounded at the 'Account' decimal precision for each
        # PO/SO/invoice line and then these rounded amounts will be
        # summed, leading to the total amount for that tax. But, if the
        # company has tax_calculation_rounding_method = round_globally,
        # we still follow the same method, but we use a much larger
        # precision when we round the tax amount for each line (we use
        # the 'Account' decimal precision + 5), and that way it's like
        # rounding after the sum of the tax amounts of each line
        prec = currency.decimal_places

        # In some cases, it is necessary to force/prevent the rounding of the tax and the total
        # amounts. For example, in SO/PO line, we don't want to round the price unit at the
        # precision of the currency.
        # The context key 'round' allows to force the standard behavior.
        round_tax = False if company_id.tax_calculation_rounding_method == 'round_globally' else True
        round_total = True
        if 'round' in self.env.context:
            round_tax = bool(self.env.context['round'])
            round_total = bool(self.env.context['round'])

        if not round_tax:
            prec += 5


        # Sorting key is mandatory in this case. When no key is provided, sorted() will perform a
        # search. However, the search method is overridden in account.tax in order to add a domain
        # depending on the context. This domain might filter out some taxes from self, e.g. in the
        # case of group taxes.
        for dis in self.sorted(key=lambda r: r.sequence):
           
            '''if dis.amount_type == 'group':
                children = dis.children_tds_ids.with_context(base_values=(base))
                ret = children.compute_all(price_unit, currency, quantity, product, partner)
                total_excluded = ret['total_excluded']
                base = ret['base'] if dis.include_base_amount else base
                total_included = ret['total_included']
                tax_amount = total_included - total_excluded
                taxes += ret['taxes']
                continue'''

            discount_amount = dis._compute_amount_tds(price_unit, quantity, product, partner)
            if not round_tax:
                discount_amount = round(discount_amount, prec)
            else:
                discount_amount = currency.round(discount_amount)

            # Keep base amount used for the current tax
            
            discount_base = 10


            tds.append({
                'id': dis.id,
                'name': dis.with_context(**{'lang': partner.lang} if partner else {}).name,
                'amount': discount_amount,
                'sequence': dis.sequence,
                'account_id': dis.account_id.id,
                'refund_account_id': dis.refund_account_id.id,
                'analytic': dis.analytic,

            })

        return {
            'tds': sorted(tds, key=lambda k: k['sequence']),
        }

    def _compute_amount_tds(self, price_unit, quantity=1.0, product=None, partner=None):
        """ Returns the amount of a single tax. base_amount is the actual amount on which the tax is applied, which is
            price_unit * quantity eventually affected by previous taxes (if tax is include_base_amount XOR price_include)
        """
        self.ensure_one()
        if self.name.concession_code.id == self.concession_code.id:
            if self.tds_threshold_applicable == True:
                if self.name.non_pan_tds_req == True:
                    if not self.partner_id.pan_no:
                        self.tds_percent_amount = 0
                        self.tds_percent = 0
                        self.non_pan_tds_percent = self.name.non_pan_tds # Fetching Non Pan TDS Percent Value
                        self.total_tds_amount = ((price_unit * quantity) * self.non_pan_tds_percent /100) #calculating Non Pan TDS total Value
                        self.non_pan_tds_percent_amount = self.total_tds_amount #Non Pad Calculated amount
                        if self.name.surcharge > 0:
                            self.surcharge_percent = self.name.surcharge  # Fetching Surcharge Percent Value
                            self.surcharge_percent_amount = self.total_tds_amount * self.name.surcharge/100 #calculating surcharge amount
                            self.total_tds_amount = self.surcharge_percent_amount + self.total_tds_amount # adding surcharge to the total tds amount
                        if self.name.e_cess > 0:
                            if self.name.she_cess > 0:
                                self.she_cess_percent = self.name.she_cess # Fetching She_Cess Percent Value
                                self.e_cess_percent = self.name.e_cess # Fetching E_cess Percent Value
                                self.she_cess_percent_amount = self.total_tds_amount * self.she_cess_percent/100 # calculating she cess amount
                                self.e_cess_percent_amount = self.total_tds_amount * self.e_cess_percent/100 # Calculating ecess amount
                                self.total_tds_amount = self.e_cess_percent_amount + self.she_cess_percent_amount + self.total_tds_amount # adding ecess and she_cess to total
                        return self.total_tds_amount
                    else:
                        self.non_pan_tds_percent_amount = 0
                        self.non_pan_tds_percent = 0
                        self.tds_percent = self.name.tds # fetching tds percent
                        self.total_tds_amount = ((price_unit * quantity) * self.tds_percent / 100)
                        self.tds_percent_amount = self.total_tds_amount
                        if self.name.surcharge > 0:
                            self.surcharge_percent = self.name.surcharge # Fetching Surcharge Percent Value
                            self.surcharge_percent_amount = self.total_tds_amount * self.name.surcharge/100 #calculating surcharge amount
                            self.total_tds_amount = self.surcharge_percent_amount + self.total_tds_amount # adding surcharge to the total tds amount
                        if self.name.e_cess > 0:
                            if self.name.she_cess > 0:
                                self.she_cess_percent = self.name.she_cess # Fetching She_Cess Percent Value
                                self.e_cess_percent = self.name.e_cess  # Fetching E_cess Percent Value
                                self.she_cess_percent_amount = self.total_tds_amount * self.she_cess_percent/100 # calculating she cess amount
                                self.e_cess_percent_amount = self.total_tds_amount * self.e_cess_percent/100 # Calculating ecess amount
                                self.total_tds_amount = self.e_cess_percent_amount + self.she_cess_percent_amount + self.total_tds_amount # adding ecess and she_cess to total
                        return self.total_tds_amount
                else:
                    self.non_pan_tds_percent = 0
                    self.non_pan_tds_percent_amount = 0
                    self.tds_percent = self.name.tds  # fetching tds percent
                    self.total_tds_amount = ((price_unit * quantity) * self.tds_percent / 100)
                    self.tds_percent_amount = self.total_tds_amount
                    if self.name.surcharge > 0:
                        self.surcharge_percent = self.name.surcharge  # Fetching Surcharge Percent Value
                        self.surcharge_percent_amount = self.total_tds_amount * self.name.surcharge/100 #calculating surcharge amount
                        self.total_tds_amount = self.surcharge_percent_amount + self.total_tds_amount # adding surcharge to the total tds amount
                    if self.name.e_cess > 0:
                        if self.name.she_cess > 0:
                            self.she_cess_percent = self.name.she_cess  # Fetching She_Cess Percent Value
                            self.e_cess_percent = self.name.e_cess  # Fetching E_cess Percent Value
                            self.she_cess_percent_amount = self.total_tds_amount * self.she_cess_percent/100 # calculating she cess amount
                            self.e_cess_percent_amount = self.total_tds_amount * self.e_cess_percent/100 # Calculating ecess amount
                            self.total_tds_amount = self.e_cess_percent_amount + self.she_cess_percent_amount + self.total_tds_amount # adding ecess and she_cess to total
                    return self.total_tds_amount
            else:
                if self.name.non_pan_tds_req == True:
                    if not self.partner_id.pan_no:
                        self.tds_percent_amount = 0
                        self.tds_percent = 0
                        self.non_pan_tds_percent = self.name.non_pan_tds  # Fetching Non Pan TDS Percent Value
                        self.total_tds_amount = ((price_unit * quantity) * self.non_pan_tds_percent /100) #calculating Non Pan TDS total Value
                        self.non_pan_tds_percent_amount = self.total_tds_amount #Non Pad Calculated amount
                        if self.name.surcharge > 0:
                            self.surcharge_percent = self.name.surcharge  # Fetching Surcharge Percent Value
                            self.surcharge_percent_amount = self.total_tds_amount * self.name.surcharge/100 #calculating surcharge amount
                            self.total_tds_amount = self.surcharge_percent_amount + self.total_tds_amount # adding surcharge to the total tds amount
                        if self.name.e_cess > 0:
                            if self.name.she_cess > 0:
                                self.she_cess_percent = self.name.she_cess  # Fetching She_Cess Percent Value
                                self.e_cess_percent = self.name.e_cess  # Fetching E_cess Percent Value
                                self.she_cess_percent_amount = self.total_tds_amount * self.she_cess_percent/100 # calculating she cess amount
                                self.e_cess_percent_amount = self.total_tds_amount * self.e_cess_percent/100 # Calculating ecess amount
                                self.total_tds_amount = self.e_cess_percent_amount + self.she_cess_percent_amount + self.total_tds_amount # adding ecess and she_cess to total
                        return self.total_tds_amount
                    else:
                        self.non_pan_tds_percent_amount = 0
                        self.non_pan_tds_percent = 0
                        self.tds_percent = self.name.tds  # fetching tds percent
                        self.total_tds_amount = ((price_unit * quantity) * self.tds_percent / 100)
                        self.tds_percent_amount = self.total_tds_amount
                        if self.name.surcharge > 0:
                            self.surcharge_percent = self.name.surcharge  # Fetching Surcharge Percent Value
                            self.surcharge_percent_amount = self.total_tds_amount * self.name.surcharge/100 #calculating surcharge amount
                            self.total_tds_amount = self.surcharge_percent_amount + self.total_tds_amount # adding surcharge to the total tds amount
                        if self.name.e_cess > 0:
                            if self.name.she_cess > 0:
                                self.she_cess_percent = self.name.she_cess  # Fetching She_Cess Percent Value
                                self.e_cess_percent = self.name.e_cess  # Fetching E_cess Percent Value
                                self.she_cess_percent_amount = self.total_tds_amount * self.she_cess_percent/100 # calculating she cess amount
                                self.e_cess_percent_amount = self.total_tds_amount * self.e_cess_percent/100 # Calculating ecess amount
                                self.total_tds_amount = self.e_cess_percent_amount + self.she_cess_percent_amount + self.total_tds_amount # adding ecess and she_cess to total
                        return self.total_tds_amount
                else:
                    self.non_pan_tds_percent = 0
                    self.non_pan_tds_percent_amount = 0
                    self.tds_percent = self.name.tds  # fetching tds percent
                    self.total_tds_amount = ((price_unit * quantity) * self.tds_percent / 100)
                    self.tds_percent_amount = self.total_tds_amount
                    if self.name.surcharge > 0:
                        self.surcharge_percent = self.name.surcharge  # Fetching Surcharge Percent Value
                        self.surcharge_percent_amount = self.total_tds_amount * self.name.surcharge/100 #calculating surcharge amount
                        self.total_tds_amount = self.surcharge_percent_amount + self.total_tds_amount # adding surcharge to the total tds amount
                    if self.name.e_cess > 0:
                        if self.name.she_cess > 0:
                            self.she_cess_percent = self.name.she_cess  # Fetching She_Cess Percent Value
                            self.e_cess_percent = self.name.e_cess  # Fetching E_cess Percent Value
                            self.she_cess_percent_amount = self.total_tds_amount * self.she_cess_percent/100 # calculating she cess amount
                            self.e_cess_percent_amount = self.total_tds_amount * self.e_cess_percent/100 # Calculating ecess amount
                            self.total_tds_amount = self.e_cess_percent_amount + self.she_cess_percent_amount + self.total_tds_amount # adding ecess and she_cess to total
                    return self.total_tds_amount
        else:
            self.total_tds_amount=0
            return self.total_tds_amount
