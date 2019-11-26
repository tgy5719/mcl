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
        if active_model == 'account.invoice':
            msg = "Dear *PARTNER*"
            if rec.partner_id.parent_id:
                msg +="(" + rec.partner_id.parent_id.name +")"
            msg += "\n\nHere is your "
            if rec.number:
                msg += "invoice *" + rec.number + '*'
            else:
                'invoice'
            if rec.origin:
                msg += " (with reference: " + rec.origin + ")"
            msg += " amounting in *" + self.format_amount(rec.amount_total, rec.currency_id) + "*"
            msg += " from " + rec.company_id.name + "."
            if rec.state == 'paid':
                msg += " This invoice is already paid."
            else:
                msg += " Please remit payment at your earliest convenience."
            msg += "\nDo not hesitate to contact us if you have any question.\n\n"
        result['message'] = msg
        return result
