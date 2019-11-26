from odoo import api, fields, models,_

class HrEmployee(models.Model):
	_inherit = 'hr.employee'

	lta_applicable = fields.Boolean(string='LTA Applicable',store = True)
	#emp_type = fields.Boolean('If Employee')
	six = fields.One2many('lic.policy.details','policy')
	currency_id = fields.Many2one('res.currency', 'Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id.id)
	z_amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='lic_amount_all', track_visibility='always')

	@api.depends('six.z_amount')
	def lic_amount_all(self):
		for order in self:
			z_amount_total = 0.0
			for line in order.six:
				z_amount_total += line.z_amount
			order.update({
                'z_amount_total': z_amount_total,
            })
