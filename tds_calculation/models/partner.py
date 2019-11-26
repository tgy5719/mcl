# -*- coding: utf-8 -*-

from ast import literal_eval
from operator import itemgetter
import time

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP

class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    tax_ids = fields.One2many('account.fiscal.position.tax', 'position_id', string='Tax Mapping', copy=True)
    tds_ids = fields.One2many('account.fiscal.position.tds', 'position_tds_id', string='TDS Mapping', copy=True)



    @api.model     # noqa
    def map_tds(self, tds, product=None, partner=None):
        result = self.env['account.nod.confg'].browse()
        for tds in tds:
            tds_count = 0
            for t in self.tds_ids:
                if t.tds_src_id == tax:
                    tds_count += 1
                    if t.tds_dest_id:
                        result |= t.tds_dest_id
            if not tds_count:
                result |= tds
        return result



class AccountFiscalPositionTds(models.Model):
    _name = 'account.fiscal.position.tds'
    _description = 'Taxes Fiscal Position'
    _rec_name = 'position_tds_id'

    position_tds_id = fields.Many2one('account.fiscal.position', string='Fiscal Position',
        required=True, ondelete='cascade')
    tds_src_id = fields.Many2one('account.nod.confg', string='Tax on Product', required=True)
    tds_dest_id = fields.Many2one('account.nod.confg', string='Tax to Apply')

    _sql_constraints = [
        ('tds_src_dest_uniq',
         'unique (position_tds_id,tds_src_id,tds_dest_id)',
         'A tds fiscal position could be defined only once time on same tds.')
    ]

