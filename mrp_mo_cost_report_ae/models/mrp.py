# -*- coding: utf-8 -*-

from odoo import api, models, fields


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    level = fields.Integer(default=0)
    has_child_mo = fields.Boolean()
    parent_id = fields.Integer()