
from lxml import etree
from odoo import api, fields, models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    z_cost_center_bool = fields.Boolean(string="Dimension",default=False)
