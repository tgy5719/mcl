from datetime import datetime,timedelta

from odoo import api, models, fields, _, exceptions
from dateutil.relativedelta import relativedelta
from time import strptime
from odoo.exceptions import UserError, ValidationError,Warning

class EmployeeLanguages(models.Model):
	_name = 'lang.employee'
	many = fields.Many2one('hr.employee')
	languages = fields.Many2one('cas.name', string='Languages')
	rite = fields.Boolean(string='Read')
	wr = fields.Boolean(string='Write')
	speak = fields.Boolean(string='Speak')

class LanguageName(models.Model):
	_name = 'cas.name'
	name = fields.Char(string='Languages')	

class Family_Details(models.Model):
	_name = 'family.details'

	bondage = fields.Many2one('hr.employee')
	relation = fields.Many2one('relation.name', string='Relation')
	name = fields.Char(string='Name')
	the_age = fields.Char(string='Age', size=3)
	qualification = fields.Many2one('qual.name', string='Qualification')
	occupation = fields.Char(string='Occupation')

class Relation(models.Model):
	_name = 'relation.name'
	name = fields.Char(string='Relation')

class QualificationName(models.Model):
	_name = 'qual.name'
	name = fields.Char(string='Qualification')

class EmployeesEducationDetails(models.Model):
	_name = 'educate.details'

	family = fields.Many2one('hr.employee')
	qualification = fields.Many2one('qualify.name', string='Qualification')
	college = fields.Char(string='College')
	year_of_passing = fields.Date(string='Year of passing')
	percentage = fields.Float(string='Percentage')

	@api.multi
	@api.constrains('percentage')
	def _check_age(self):
		if self.percentage>100.00:
			raise ValidationError(_("Percentage should be with in 100"))

class Qualification(models.Model):
	_name = "qualify.name"
	name = fields.Char(string="Qualification", store=True)

class DetailsExperience(models.Model):
	_name = 'experience.details'

	experience = fields.Many2one('hr.employee')
	period_from = fields.Date(string='Period From')
	period_to = fields.Date(string='Period To')
	organization = fields.Char(string='Organization')
	designation = fields.Many2one('designation.name', string='Designation')
	ctc = fields.Float(string='CTC')
	reason_for_leaving = fields.Many2one('reason.name', string='Reason for leaving')

	@api.multi
	@api.constrains("period_to","period_from")
	def _check_period(self):
		for rec in self:
			if rec.period_to < rec.period_from:
				raise ValidationError('Sorry, period_to must be greater than period_from')

class Designation(models.Model):
	_name = 'designation.name'
	name = fields.Char(string='Designation Name')

class ReasonLeaving(models.Model):
	_name = 'reason.name'
	name = fields.Char(string='Reason For Leaving')

class BloodGroup(models.Model):
	_name = 'group.name'
	name = fields.Char(string='Blood Group')

class EmployeeTransfer(models.Model):
	_name = 'employee.transfer'

	transfer = fields.Many2one('hr.employee')
	z_job_position = fields.Many2one('hr.job',string="Job Position")	
	z_period_from = fields.Date(string='Period From')
	z_period_to = fields.Date(string='Period To')
	z_location = fields.Many2one('res.partner',string="Location")	
