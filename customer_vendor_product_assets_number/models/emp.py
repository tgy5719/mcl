# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import logging
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError
from odoo.modules.module import get_module_resource
_logger = logging.getLogger(__name__)
class Employee(models.Model):
	_name = "hr.employee"
	_inherit = ['hr.employee']

	employee_category = fields.Many2one('hr.category',string = 'Employee Category',store = True)
	employee_category_internal = fields.Many2one('hr.category.internal',string = 'Employee Category',store = True)
	number = fields.Char(string = 'nummer',readonly=True,compute = '_cege')
	row=fields.Integer(string='row',compute='damagey',readonly=True)
	count  = fields.Char(string='count',store=True)
	emp_number = fields.Char(string='Employee',compute ="_emp_number")
	emp_manual_number = fields.Char('Employee',store = True)
	emp_comman_nummber = fields.Char('employee')
	emp_testo = fields.Char('emp_code')
	emp_row = fields.Char('empl_row')
	emp_axe = fields.Char('employee_codes')
	status = fields.Selection([('draft', 'Open to Generate Sequence'),('sent', 'Auto Generated Sequence'),], string='Status',readonly=True, select=True, help='sequenceflow stages', default='draft')
	@api.one
	def damagey(self):
		for lita in self:
			count = self.env['hr.employee'].search_count([('employee_category.name','=',lita.employee_category.name)])
			if count == 0:
				self.row = count
			else:
				self.row = count
	@api.one
	def _cege(self):
		count = self.env['hr.employee'].search_count([('employee_category.name','=',self.employee_category.name)])
		n = count
		count=0
		while(n>0):
			count=count+1
			n=n//10
			if count == 1:
				self.number = "0000"
			if count == 2:
				self.number = "000"
			if count == 3:
				self.number = "00"
			if count == 4:
				self.number = "0"
	@api.one
	@api.depends('employee_category.name','number','row')
	def _emp_number(self):
		self.emp_number = str(self.employee_category.name)+"-"+str(self.number)+""+str(self.row)
	@api.one
	def sequence_generator(self):
		self.ensure_one()
		self.write({'status': 'sent',})
		for lita in self:
			count = self.env['hr.employee'].search_count([('employee_category.name','=',lita.employee_category.name)])
			if count == 0:
				self.row = count
			else:
				self.row = count	
			count = self.env['hr.employee'].search_count([('employee_category.name','=',self.employee_category.name)])
			n = count
			count=0
			while(n>0):
				count=count+1
				n=n//10
				if count == 1:
					self.number = "0000"
				if count == 2:
					self.number = "000"
				if count == 3:
					self.number = "00"
				if count == 4:
					self.number = "0"
			self.emp_testo = str(self.employee_category.name)+"-"+str(self.number)+""+str(self.row)	
	_sql_constraints = [('emp_testo_uniq', 'unique (emp_testo)', "The code ID must be unique, this one is already assigned to another employee.")]
	'''@api.model
	def create(self, vals):
		if self.employee_category == False:
			vals['emp_testo'] = str(self.employee_category.name)+"-"+str(self.number)+""+str(self.row)
		#vals['emp_number'] = str(self.employee_category.name)+"-"+str(self.number)+""+str(self.row)
		return super(Employee,self).create(vals)
	@api.multi
	def write(self, vals):
		if self.employee_category == False:
			vals['emp_testo'] = str(self.employee_category.name)+"-"+str(self.number)+""+str(self.row)
		#vals['emp_number'] = str(self.employee_category.name)+"-"+str(self.number)+""+str(self.row)
		return super(Employee,self).write(vals)'''

