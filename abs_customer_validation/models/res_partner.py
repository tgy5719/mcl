from odoo import api,fields,models,_
from odoo.exceptions import ValidationError
import re

class ResPartner(models.Model):
    _inherit="res.partner"

    def get_partner_list(self,partner_objs):
        partner_list = ''
        for partner in partner_objs:
            partner_list = partner_list + ' || ' + partner.name
        return partner_list

    @api.onchange('name')
    def onchange_name(self):
        if self.name and self.user_has_groups("abs_customer_validation.group_activate_customer_validation"):
            if self.env['res.partner'].search([('name','=',self.name)]):
                raise ValidationError(_('The record ' +self.name+' already exists ' ))

    @api.onchange('phone')
    def onchange_phonenumber(self):
        if self.phone and self.user_has_groups("abs_customer_validation.group_activate_customer_validation"):
            partner_objs = self.env['res.partner'].search([('phone','=',self.phone)])
            if self.get_partner_list(partner_objs):
                raise ValidationError(_('Phone Number '+str(self.phone)+' already exists in the following record:' + '\n' + self.get_partner_list(partner_objs)))

    @api.onchange('mobile')
    def onchange_mobilenumber(self):
        if self.mobile and self.user_has_groups("abs_customer_validation.group_activate_customer_validation"):
            partner_objs = self.env['res.partner'].search([('mobile','=',self.mobile)])
            if self.get_partner_list(partner_objs):
                raise ValidationError(_('Mobile Number '+str(self.mobile)+' already exists in the following record:' + '\n' + self.get_partner_list(partner_objs)))

    @api.onchange('fax')
    def onchange_fax(self):
        if self.fax and self.user_has_groups("abs_customer_validation.group_activate_customer_validation"):
            partner_objs = self.env['res.partner'].search([('fax','=',self.fax)])
            if self.get_partner_list(partner_objs):
                raise ValidationError(_('Fax Number '+str(self.fax)+' already exists in the following record:' + '\n' + self.get_partner_list(partner_objs)))

    @api.onchange('email')
    def onchange_email(self):
        if self.email and self.user_has_groups("abs_customer_validation.group_activate_customer_validation"):
            partner_objs = self.env['res.partner'].search([('email','=',self.email)])
            if self.get_partner_list(partner_objs):
                raise ValidationError(_('Email ID '+str(self.email)+' already exists in the following record:' + '\n' + self.get_partner_list(partner_objs)))

    @api.onchange('website')
    def onchange_website(self):
        if self.website and self.user_has_groups("abs_customer_validation.group_activate_customer_validation"):
            website_id = "http://"+str(self.website)
            partner_objs = self.env['res.partner'].search([('website','=',website_id)])
            if self.get_partner_list(partner_objs):
                raise ValidationError(_('Website Address '+str(self.website)+' already exists in the following record:' + '\n' + self.get_partner_list(partner_objs)))


    @staticmethod
    def check_gstin_chksum( gstin_num ):
        gstin_num=gstin_num.upper()
        keys = ['0','1','2','3','4','5','6','7','8','9','A', 'B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
        values=range(36)
        hash = {k:v for k, v in zip(keys, values)}
        index = 0
        sum=0 
        while index < len(gstin_num)-1:
            lettr = gstin_num[index]
            tmp = (hash[lettr])*((index%2)+1) #Factor =1 fr index odd
            sum += tmp//36 + tmp%36
            index = index + 1
        Z=sum%36
        Z=(36-Z)%36
        if((hash[(gstin_num[-1:])])==Z):
            #print('true')
            return True
        #print('false')
        return False
        
    @api.onchange('vat')
    def onchange_vat(self):
        if self.vat and self.user_has_groups("abs_customer_validation.group_activate_customer_validation"):
            partner_objs = self.env['res.partner'].search([('vat','=',self.vat)])
            if self.get_partner_list(partner_objs):
                raise ValidationError(_('GSTIN Number '+str(self.vat)+' already exists in the following record:' + '\n' + self.get_partner_list(partner_objs)))
            if not((self.vat)):
                return
            if(len(self.vat)!=15):
                return {
                'warning': {'title': 'Warning', 'message': 'Invalid GSTIN. GSTIN number must be 15 digits. Please check.',},    
                }
            if not(re.match("\d{2}[A-Z]{5}\d{4}[A-Z]{1}\d[Z]{1}[A-Z\d]{1}", self.vat.upper())):
                return {
                'warning': {'title': 'Warning', 'message': 'Invalid GSTIN format.\r\n.GSTIN must be in the format nnAAAAAnnnnA_Z_ where n=number, A=alphabet, _=either.',}, 
                }
            if not(ResPartner.check_gstin_chksum(self.vat)):
                return {
                'warning': {'title': 'Warning', 'message': 'Invalid GSTIN. Checksum validation failed. It means one or more characters are probably wrong.',},  
                }
            self.vat = self.vat.upper() 

