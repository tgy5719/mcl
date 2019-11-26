from odoo import models, fields, api, exceptions, _
from odoo.exceptions import Warning
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
import openerp.addons.decimal_precision as dp
import datetime
from datetime import datetime
import math

AVAILABLE_PRIORITIES = [
    ('0', 'Low'),
    ('1', 'Medium'),
    ('2', 'High'),
    ('3', 'Very High'),
]
class CrmLeadWizard(models.TransientModel):
	_name= 'crm.lead.wizard'
	_description = 'Crm Lead wizard'

	def _default_lead(self):
		return self.env['crm.lead.login.restriction'].search([('id', '=',self.env.context.get('active_id'))], limit=1)

	name = fields.Many2one('crm.lead.login.restriction',string="Login Reference",default=_default_lead)
	
	z_lead_name = fields.Char('Name')

	z_partner_id = fields.Many2one('res.partner','Customer')

	z_partner_name = fields.Char('Company Name')
	
	z_street = fields.Char('Street')
	z_street2 = fields.Char('Street2')
	z_city = fields.Char('City')
	z_state_id = fields.Many2one("res.country.state", string='State')
	z_zip = fields.Char('Zip', change_default=True)
	z_country_id = fields.Many2one('res.country', string='Country')

	z_website = fields.Char('Website')

	z_sales_person = fields.Many2one('res.users',string="Sales Person",related="name.z_sales_person")
	z_team_id = fields.Many2one('crm.team', string='Sales Team', oldname='section_id',index=True, track_visibility='onchange', help='When sending mails, the default email address is taken from the Sales Team.')

	z_contact_name = fields.Char('Contact Name')
	z_title = fields.Many2one('res.partner.title')
	z_email_from = fields.Char('Email')
	z_function = fields.Char('Job Position')
	z_phone = fields.Char('Phone')
	z_mobile = fields.Char('Mobile')
	z_priority = fields.Selection(AVAILABLE_PRIORITIES, string='Priority', index=True, default=AVAILABLE_PRIORITIES[0][0])
	z_tag_ids = fields.Many2many('crm.lead.tag','z_tag_id', string='Tags', help="Classify and analyze your lead/opportunity categories like: Training, Service")

	z_description = fields.Char('Description')


	@api.multi
	def generate_leads(self):
		crm_leads = self.env['crm.lead']
		vals = {
		'name':self.z_lead_name,
		'partner_id':self.z_partner_id.id,
		'partner_name':self.z_partner_name,
		'street':self.z_street,
		'street2':self.z_street2,
		'city':self.z_city,
		'state_id':self.z_state_id.id,
		'zip':self.z_zip,
		'country_id':self.z_country_id.id,
		'website':self.z_website,
		'user_id':self.z_sales_person.id,
		'team_id':self.z_team_id.id,
		'contact_name':self.z_contact_name,
		'title':self.z_title.id,
		'email_from':self.z_email_from,
		'function':self.z_function,
		'phone':self.z_phone,
		'mobile':self.z_mobile,
		'type':'lead',
		'priority':self.z_priority,
		'tag_ids':self.z_tag_ids.ids,
		'description':self.z_description,
		}
		lead_obj = self.env['crm.lead'].create(vals)
