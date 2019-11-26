from datetime import datetime,timedelta

from odoo import api, models, fields, _, exceptions
from dateutil.relativedelta import relativedelta
from time import strptime
from odoo.exceptions import UserError, ValidationError,Warning


class HrEmployee(models.Model):
	_inherit = 'hr.employee'
	alternative_address = fields.Text('Alternative Address',store = True)
	age = fields.Char('Age',store = True,size=3, compute='_compute_age')
	z_age = fields.Char('Age')
	date_of_joining = fields.Date('Date of Joining',store = True)
	date_of_relieving = fields.Date('Date of relieving',store = True)
	date_of_resignation = fields.Date('Date of resignation',store = True)
	one = fields.One2many('lang.employee','many')
	two = fields.One2many('family.details','bondage')
	three = fields.One2many('educate.details','family')
	four = fields.One2many('experience.details','experience')
	five = fields.One2many('employee.transfer','transfer')
	#six = fields.One2many('lic.policy.details','policy')
	esi_applicable = fields.Boolean(string='ESI Applicable',store = True)
	z_pf_no = fields.Char('PF No',store = True)
	z_esi_no = fields.Char('ESI No',store = True)
	z_epf_uan_no = fields.Char('EPF UAN No',store = True)
	z_blood_group = fields.Many2one('group.name', string='Blood Group')
	
	@api.constrains('date_of_relieving')
	def _check_release_date_of_relieving(self):
		for r in self:
			if r.date_of_relieving < self.date_of_joining:
				raise models.ValidationError('Date of relieving should be greater than Date of joining')
	@api.depends('birthday')
	def _compute_age(self):
		for rec in self:
			if rec.birthday:
				dt = str(rec.birthday)
				d1 = datetime.strptime(dt, "%Y-%m-%d").date()
				d2 = datetime.today()
				rd = relativedelta(d2, d1)
				rec.age = str(rd.years) + ' years' 
				rec.z_age = rec.age
