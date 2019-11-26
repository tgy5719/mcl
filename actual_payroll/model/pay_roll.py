import time
from datetime import datetime
from datetime import time as datetime_time
from dateutil import relativedelta

import babel

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError

class HrContract(models.Model):
	_inherit = 'hr.contract'

	dearness_allowance_id = fields.Monetary('Dearness Allowance')