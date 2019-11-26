# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class SendWAMessage(models.TransientModel):
    _inherit = 'whatsapp.msg'

    @api.model
    def default_get(self, fields):
        result = super(SendWAMessage, self).default_get(fields)
        active_model = self.env.context.get('active_model')
        res_id = self.env.context.get('active_id')
        rec = self.env[active_model].browse(res_id)
        res_name = 'Invoice_' + rec.number.replace('/', '_') if active_model == 'account.invoice' else rec.name
        msg = result.get('message', '')
        if active_model == 'account.payment':
            msg = "Dear *PARTNER*\n\nThank you for your payment." \
            "Here is your payment receipt *" + (rec.name or '').replace('/','-') + "* amounting"\
            " to *" + self.format_amount(rec.amount, rec.currency_id) + "*"\
            " from " + rec.company_id.name + "."
            msg += "\nDo not hesitate to contact us if you have any question.\n\nBest regards."
        
        result['message'] = msg
        return result
