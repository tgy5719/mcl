# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from odoo.tools import float_compare, float_round
from odoo.addons import decimal_precision as dp


class MrpProductionWorkcenterLine(models.Model):
	_inherit = 'mrp.workorder'

	def do_finish(self):
		for line in self:
			if line.final_lot_id:
				line.final_lot_id.z_analytic_tag_ids = line.production_id.z_analytic_tag_ids_default.ids
		return super(MrpProductionWorkcenterLine, self).do_finish()

