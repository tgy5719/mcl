from datetime import datetime,timedelta
from odoo import api, models, fields, _, exceptions
from dateutil.relativedelta import relativedelta
from time import strptime
from odoo.exceptions import UserError, ValidationError,Warning
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class LandedCost(models.Model):
	_inherit = 'stock.landed.cost'

	z_stock_picking = fields.Many2one('stock.picking',string="Stock Picking Ref")
	
