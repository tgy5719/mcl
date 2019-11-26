from odoo import api, fields, models,_

class LicPolicyDetails(models.Model):
	_name = 'lic.policy.details'

	policy = fields.Many2one('hr.employee')
	z_policy_name = fields.Char(string='Policy Name')
	z_policy_num = fields.Char(string='Policy Number')
	z_amount = fields.Float(string="Amount")
	
	currency_id = fields.Many2one('res.currency', 'Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id.id)


	