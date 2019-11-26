import time
from datetime import datetime
from datetime import timedelta
from datetime import time as datetime_time
from dateutil import relativedelta

import babel

from odoo import api, fields, models, tools, exceptions,_
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError

import calendar

from calendar import monthrange

import logging
import math
from odoo.tools import float_compare
import time
from datetime import datetime
from datetime import timedelta
from datetime import time as datetime_time
from dateutil import relativedelta

from odoo.exceptions import UserError, ValidationError,Warning

class HrPayInherit(models.Model):
    _inherit = "hr.payslip"

    period_month = fields.Float('Period Days',store=True,compute="_compute_total_days")
    no_days_working = fields.Float('Paid Days',store=True,compute="_compute_paid")
    unpaid_id = fields.Float('Unpaid',store=True,compute="_compute_week")
    no_days_month = fields.Integer('Calendar Days',compute="_compute_days_ii")

    @api.multi
    @api.depends('date_from')
    def _compute_days_ii(self):
    	for line in self:
    		date_from = fields.Datetime.from_string(line.date_from)
    		line.no_days_month = monthrange(date_from.year,date_from.month)[1]

    @api.depends('date_to','date_from')
    def _compute_total_days(self):
    	for line in self:
    		date_from = line.date_from
    		date_to = line.date_to
    		if date_from and not date_to:
    			date_to_with_delta = fields.Datetime.from_string(date_from)
    			self.date_to = str(date_to_with_delta)
    		if (date_to and date_from) and (date_from <= date_to):
    			line.period_month = self._get_number_of_days(date_from, date_to, line.employee_id.id)
    		else:
    			line.period_month = 0

    def _get_number_of_days(self, date_from, date_to, name):

    	from_dt = fields.Datetime.from_string(date_from)
    	to_dt = fields.Datetime.from_string(date_to)

    	time_delta = to_dt - from_dt
    	return math.ceil(time_delta.days + (float(time_delta.days) / 86400))

    @api.depends('date_from','date_to','employee_id')
    def _compute_week(self):
    	for l in self:
    		if l.date_from:
    			if l.date_to:
    				holidays = self.env['hr.leave'].search(['&',('date_from','>=',l.date_from),('date_to','<=',l.date_to),
    					('employee_id', '=', l.employee_id.id),
    					('unpaid_condition','=' , True)
    					])
    				for holiday in holidays:
    					l.unpaid_id += holiday.number_of_days_display

    @api.depends('date_from','date_to')
    def _compute_paid(self):
    	for line in self:
    		if line.date_from:
    			if line.date_to:
    				line.no_days_working = line.period_month - line.unpaid_id


class unpaid_leaves(models.Model):
    _inherit = "hr.leave"

    unpaid_condition = fields.Boolean(index=True, default=True,related='holiday_status_id.unpaid')


