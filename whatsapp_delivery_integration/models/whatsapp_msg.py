# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _
from odoo.tools import html_sanitize

_logger = logging.getLogger(__name__)


class SendWAMessage(models.TransientModel):
    _inherit = 'whatsapp.msg'

    @api.model
    def default_get(self, fields):
        result = super(SendWAMessage, self).default_get(fields)
        active_model = self.env.context.get('active_model')
        res_id = self.env.context.get('active_id')
        rec = self.env[active_model].browse(res_id)
        user = self.env.user
        msg = result.get('message', '')
        if active_model == 'stock.picking':
            msg = "Hello *PARTNER*"\
            "\n\nWe are glad to inform you that your order has been shipped."
            if rec.carrier_tracking_ref:
                msg += "Your tracking reference is *"
                if rec.carrier_tracking_url:
                    msg += "<a href=" + rec.carrier_tracking_url + " target='_blank'>" + rec.carrier_tracking_ref + "</a>."
                else:
                    msg += rec.carrier_tracking_ref + "."
                msg += "*"
            msg += "\n\nPlease find your delivery order attached for more details.\n\nThank you."
        result['message'] = msg
        return result
